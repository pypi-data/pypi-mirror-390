"""
Glassbox Logger - Core logging functionality
"""

import sqlite3
import threading
import time
import logging
import requests
from typing import Optional, Dict, Any
from contextlib import contextmanager
from .utils import (
    calculate_cost,
    extract_tokens,
    extract_model,
    generate_prompt_id,
    get_timestamp,
    validate_output
)
from .environment import get_app_id_with_env, get_database_path_with_env, get_environment
from .test_mode import should_disable_tracking, is_test_mode, get_test_logger
from .auto_detect import get_smart_defaults, detect_installed_libraries, print_detection_summary
from .logging_config import setup_logging

# Initialize logging
setup_logging()


class GlassboxLogger:
    """
    Main logger class for Glassbox AI observability.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        app_id: str = "default",
        backend_url: Optional[str] = None,
        sync_enabled: bool = True,
        environment: Optional[str] = None,
        privacy_config: Optional[Any] = None
    ):
        self.api_key = api_key
        # Add environment suffix to app_id
        self.app_id = get_app_id_with_env(app_id, environment)
        self.backend_url = backend_url or "http://localhost:8000"
        self.sync_enabled = sync_enabled
        self.environment = environment or get_environment()
        self.privacy_config = privacy_config
        self._lock = threading.Lock()
        
        # Initialize local SQLite database with environment separation
        self.db_path = get_database_path_with_env(".glassbox.db", environment)
        self._init_db()
    
    def _init_db(self) -> None:
        """Initialize SQLite database for local-first logging."""
        try:
            with sqlite3.connect(self.db_path, timeout=5.0) as conn:
                # Enable WAL mode for better concurrency
                conn.execute("PRAGMA journal_mode=WAL")
                conn.execute("PRAGMA synchronous=NORMAL")  # Faster writes
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        app_id TEXT NOT NULL,
                        prompt_id TEXT NOT NULL,
                        model TEXT NOT NULL,
                        input_tokens INTEGER NOT NULL,
                        output_tokens INTEGER NOT NULL,
                        latency_ms REAL NOT NULL,
                        cost_usd REAL NOT NULL,
                        valid INTEGER NOT NULL,
                        timestamp TEXT NOT NULL,
                        synced INTEGER DEFAULT 0
                    )
                """)
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_timestamp ON logs(timestamp)
                """)
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_synced ON logs(synced)
                """)
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_app_id ON logs(app_id)
                """)
                conn.commit()
        except Exception as e:
            # If database init fails, we can't log but shouldn't crash
            # Use basic logging if logger not initialized yet
            try:
                self.logger.error(f"Glassbox database init error: {e}", exc_info=True)
            except (AttributeError, NameError):
                # Logger not initialized yet, use fallback
                import sys
                print(f"Glassbox database init error: {e}", file=sys.stderr)
    
    def log(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        latency_ms: float,
        cost_usd: float,
        valid: bool,
        prompt_id: Optional[str] = None,
        timestamp: Optional[str] = None
    ) -> None:
        """
        Log an AI call to local database and optionally sync to backend.
        """
        prompt_id = prompt_id or generate_prompt_id()
        timestamp = timestamp or get_timestamp()
        
        log_entry = {
            "app_id": self.app_id,
            "prompt_id": prompt_id,
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "latency_ms": latency_ms,
            "cost_usd": cost_usd,
            "valid": valid,
            "timestamp": timestamp
        }
        
        # Write to local database
        # CRITICAL: Never let logging errors break user code
        try:
            with self._lock:
                with sqlite3.connect(self.db_path, timeout=5.0) as conn:
                    # Enable WAL mode for better concurrency
                    conn.execute("PRAGMA journal_mode=WAL")
                    conn.execute("""
                        INSERT INTO logs 
                        (app_id, prompt_id, model, input_tokens, output_tokens, 
                         latency_ms, cost_usd, valid, timestamp, synced)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
                    """, (
                        log_entry["app_id"],
                        log_entry["prompt_id"],
                        log_entry["model"],
                        log_entry["input_tokens"],
                        log_entry["output_tokens"],
                        log_entry["latency_ms"],
                        log_entry["cost_usd"],
                        1 if log_entry["valid"] else 0,
                        log_entry["timestamp"]
                    ))
                    conn.commit()
        except Exception as e:
            # CRITICAL: Silently fail - never break user code
            # Log error for debugging, but don't raise
            try:
                self.logger.error(f"Glassbox logging error (non-fatal): {e}", exc_info=True)
            except (AttributeError, NameError):
                # Logger not initialized yet, use fallback
                import sys
                print(f"Glassbox logging error (non-fatal): {e}", file=sys.stderr)
        
        # Sync to backend if enabled
        if self.sync_enabled and self.backend_url:
            try:
                self._sync_to_backend(log_entry)
            except Exception as e:
                # Silently fail - local-first approach
                try:
                    self.logger.debug(f"Backend sync failed (non-fatal): {e}", exc_info=True)
                except (AttributeError, NameError):
                    # Ultimate fallback - logger not available, silently fail
                    pass
    
    def _sync_to_backend(self, log_entry: Dict[str, Any]) -> None:
        """Sync log entry to backend API."""
        headers = {}
        if self.api_key:
            headers["X-API-Key"] = self.api_key
        
        response = requests.post(
            f"{self.backend_url}/api/logs",
            json=log_entry,
            headers=headers,
            timeout=5
        )
        response.raise_for_status()
        
        # Mark as synced in local DB
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    UPDATE logs SET synced = 1 
                    WHERE prompt_id = ? AND timestamp = ?
                """, (log_entry["prompt_id"], log_entry["timestamp"]))
                conn.commit()
    
    @contextmanager
    def track_call(self, model: str):
        """
        Context manager to track an AI call with automatic timing.
        
        Usage:
            with logger.track_call("gpt-4") as call:
                response = openai.ChatCompletion.create(...)
                call.log(response)
        """
        start_time = time.time()
        prompt_id = generate_prompt_id()
        
        class CallTracker:
            def __init__(self, logger, model, prompt_id, start_time):
                self.logger = logger
                self.model = model
                self.prompt_id = prompt_id
                self.start_time = start_time
                self.response = None
                self.logged = False
            
            def log(self, response: Any) -> None:
                """Log the response after the call completes."""
                if self.logged:
                    return  # Already logged
                
                self.response = response
                self.logged = True
                latency_ms = (time.time() - self.start_time) * 1000
                
                input_tokens, output_tokens = extract_tokens(response)
                model_name = extract_model(response, self.model)
                cost_usd = calculate_cost(model_name, input_tokens, output_tokens)
                valid = validate_output(response)
                
                self.logger.log(
                    model=model_name,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    latency_ms=latency_ms,
                    cost_usd=cost_usd,
                    valid=valid,
                    prompt_id=self.prompt_id
                )
        
        tracker = CallTracker(self, model, prompt_id, start_time)
        yield tracker


# Global logger instance
_logger: Optional[GlassboxLogger] = None


def init(
    api_key: Optional[str] = None,
    app_id: Optional[str] = None,
    backend_url: Optional[str] = None,
    sync_enabled: Optional[bool] = None,
    auto_wrap: bool = True,
    environment: Optional[str] = None,
    test_mode: Optional[bool] = None,
    verbose: bool = False
) -> GlassboxLogger:
    """
    Initialize Glassbox — Codex-style minimal.
    
    One line, zero config. Auto-detects everything.
    
    Examples:
        glassbox.init()  # That's it!
        
        # Optional: customize
        glassbox.init(api_key="your-key")
        glassbox.init(app_id="my-app")
    """
    global _logger
    
    # Check if tracking should be disabled
    if test_mode is None:
        test_mode = should_disable_tracking()
    
    if test_mode:
        # Return mock logger in test mode
        _logger = get_test_logger()
        return _logger
    
    # Get smart defaults based on detected environment
    defaults = get_smart_defaults()
    
    # Use provided values or smart defaults
    final_app_id = app_id or defaults.get('app_id', 'default')
    final_backend_url = backend_url or defaults.get('backend_url', 'http://localhost:8000')
    final_sync_enabled = sync_enabled if sync_enabled is not None else defaults.get('sync_enabled', True)
    final_environment = environment or defaults.get('environment', 'development')
    
    # Print detection summary if verbose
    if verbose:
        print_detection_summary()
    
    _logger = GlassboxLogger(
        api_key=api_key,
        app_id=final_app_id,
        backend_url=final_backend_url,
        sync_enabled=final_sync_enabled,
        environment=final_environment
    )
    
    # Auto-wrap AI library calls for zero-configuration setup
    if auto_wrap:
        try:
            from .auto_wrap import auto_wrap_all
            auto_wrap_all()
        except Exception:
            pass  # Silently fail if wrapping fails
        
        # Also enable HTTP interception for universal compatibility
        try:
            from .http_interceptor import intercept_http
            intercept_http()
        except Exception:
            pass  # Silently fail if interception fails
        
        # Enable async HTTP interception
        try:
            from .async_interceptor import intercept_async_http
            intercept_async_http()
        except Exception:
            pass  # Silently fail if async interception fails
    
    # Sandbox mode detection (no API keys) - but don't auto-generate demo data
    # Demo data is only available via explicit 'glassbox test' command
    # Users should see instructions instead when database is empty
    # Removed: auto-generation of demo data via enable_sandbox_mode()
    
    return _logger


def get_logger() -> Optional[GlassboxLogger]:
    """Get the global logger instance.
    
    Returns:
        The global GlassboxLogger instance, or None if not initialized.
    """
    return _logger


def log_call(
    model: str,
    response: Any,
    latency_ms: Optional[float] = None,
    prompt_id: Optional[str] = None
) -> None:
    """
    Convenience function to log a call using the global logger.
    
    Usage:
        response = openai.ChatCompletion.create(...)
        glassbox.log_call("gpt-4", response)
    """
    if _logger is None:
        # Auto-initialize with defaults
        init()
    
    if latency_ms is None:
        # Can't calculate latency without timing, use 0
        latency_ms = 0
    
    input_tokens, output_tokens = extract_tokens(response)
    model_name = extract_model(response, model)
    cost_usd = calculate_cost(model_name, input_tokens, output_tokens)
    valid = validate_output(response)
    
    _logger.log(
        model=model_name,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        latency_ms=latency_ms,
        cost_usd=cost_usd,
        valid=valid,
        prompt_id=prompt_id
    )

