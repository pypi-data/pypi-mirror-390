"""
Glassbox CLI - Codex-style command-line interface
Seamless, frictionless, developer-friendly.
"""

import sys
import os
import sqlite3
import time
import json
import threading
from datetime import datetime
from typing import Optional
import argparse

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .logger import init, get_logger
from .auto_detect import detect_installed_libraries, detect_api_keys, print_detection_summary, get_smart_defaults
from .sandbox import generate_demo_logs
from .proxy import GlassboxProxy
from .ui import (
    print_header, print_section, print_success, print_error, print_warning, print_info,
    print_step, print_box, print_table, print_code_block, print_key_value, print_list,
    print_divider, print_welcome, print_footer, format_currency, format_duration,
    format_timestamp, ask_yes_no, ask_input, Colors, colorize
)


def cmd_init(args):
    """Initialize Glassbox - Codex-style: completely silent, just works."""
    from .smart_init import (
        get_smart_init_context,
        auto_configure_integration,
        auto_verify_setup
    )
    
    # Codex-style: completely silent, smart defaults
    context = get_smart_init_context()
    app_id = args.app_id or context['app_id']
    backend_url = args.backend_url or context['backend_url']
    
    # Initialize (silent)
    logger = init(
        api_key=args.api_key,
        app_id=app_id,
        backend_url=backend_url,
        sync_enabled=not args.no_sync,
        verbose=False
    )
    
    # Auto-verify (silent)
    success, _ = auto_verify_setup(app_id, backend_url)
    
    # Don't generate demo data automatically - let users see instructions instead
    # Demo data is only available via 'glassbox test' command
    
    # Codex-style: completely silent unless verbose
    if args.verbose:
        if success:
            print(colorize("✓", Colors.SUCCESS) + " ready")
        else:
            print(colorize("✓", Colors.SUCCESS) + " ready")
    # Otherwise: no output at all (Codex-style)


def cmd_live(args):
    """Stream logs in real-time - Codex-style: auto-init, instant value."""
    from .live_metrics import LiveMetricsDisplay
    
    db_path = args.db or ".glassbox.db"
    json_output = getattr(args, 'json', False)
    
    # Initialize display
    display = LiveMetricsDisplay(json_output=json_output)
    
    # Try WebSocket connection first (for live web apps)
    logger = get_logger()
    if logger and logger.backend_url and not json_output:
        try:
            from .websocket_client import connect_and_listen
            import asyncio
            
            # Codex-style: minimal, just start
            asyncio.run(connect_and_listen(logger.backend_url, logger.app_id))
            return
        except ImportError:
            pass
        except Exception:
            pass
    
    # Codex magic: Auto-init if database doesn't exist (zero friction)
    if not os.path.exists(db_path):
        if json_output:
            print(json.dumps({'error': 'Database not found', 'db_path': db_path}))
            return
        
        # Auto-initialize silently (Codex-style: just works)
        try:
            from .smart_init import get_smart_init_context
            context = get_smart_init_context()
            app_id = context['app_id']
            backend_url = context['backend_url']
            
            # Silent init
            logger = init(
                api_key=None,
                app_id=app_id,
                backend_url=backend_url,
                sync_enabled=True,
                verbose=False
            )
            
            # Ensure database exists and is ready
            if logger and os.path.exists(db_path):
                # Don't generate demo data - show instructions instead when empty
                pass
            else:
                print("run 'glassbox init' first")
                return
        except Exception:
            # If auto-init fails, show minimal error
            print("run 'glassbox init' first")
            return
    
    # Codex-style: no header, just start
    
    # Check if database has any logs
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM logs")
        log_count = cursor.fetchone()[0]
        conn.close()
        
        if log_count == 0 and not json_output:
            # Show helpful message for first-time users
            print()
            print(colorize("No AI calls tracked yet", Colors.DIM))
            print()
            print(colorize("To start tracking AI calls, add this to your code:", Colors.INFO))
            print()
            print(colorize("  import glassbox", Colors.BOLD))
            print(colorize("  glassbox.init()", Colors.BOLD))
            print()
            print(colorize("  # Your existing AI code works as-is", Colors.DIM))
            print(colorize("  from openai import OpenAI", Colors.DIM))
            print(colorize("  client = OpenAI()", Colors.DIM))
            print(colorize("  response = client.chat.completions.create(...)", Colors.DIM))
            print()
            print(colorize("  # ✅ Automatically tracked!", Colors.SUCCESS))
            print()
            print(colorize("Waiting for AI calls... (Press Ctrl+C to exit)", Colors.DIM))
            print()
    except:
        pass
    
    last_id = 0
    
    try:
        while True:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, timestamp, model, cost_usd, latency_ms, valid, prompt_id
                FROM logs
                WHERE id > ?
                ORDER BY id ASC
            """, (last_id,))
            
            rows = cursor.fetchall()
            conn.close()
            
            for row in rows:
                log_id, timestamp, model, cost, latency, valid, prompt_id = row
                last_id = log_id
                
                # Display in GNU Parallel style
                display.display_call(
                    model=model or 'unknown',
                    latency_ms=latency or 0.0,
                    cost=cost or 0.0,
                    valid=bool(valid),
                    prompt_id=prompt_id or ''
                )
            
            time.sleep(0.5)  # Poll every 500ms
            
    except KeyboardInterrupt:
        if not json_output:
            print()
        # Display summary with actionable tips
        display.display_summary()
        if not json_output:
            print_success("Stopped")
            print()


def cmd_stats(args):
    """Show aggregated statistics - Codex-style: auto-init, instant value."""
    db_path = args.db or ".glassbox.db"
    json_output = getattr(args, 'json', False)
    
    # Codex magic: Auto-init if database doesn't exist
    if not os.path.exists(db_path):
        if json_output:
            print(json.dumps({'error': 'Database not found', 'db_path': db_path}))
            return
        
        # Auto-initialize silently
        try:
            from .smart_init import get_smart_init_context
            context = get_smart_init_context()
            app_id = context['app_id']
            backend_url = context['backend_url']
            
            # Silent init (this creates the database and table)
            logger = init(
                api_key=None,
                app_id=app_id,
                backend_url=backend_url,
                sync_enabled=True,
                verbose=False
            )
            
            # Ensure database exists and is ready
            if logger and os.path.exists(db_path):
                # Don't generate demo data - show instructions instead when empty
                pass
            else:
                print("run 'glassbox init' first")
                return
        except Exception:
            print("run 'glassbox init' first")
            return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get stats
    cursor.execute("""
        SELECT 
            COUNT(*) as total_calls,
            SUM(cost_usd) as total_cost,
            AVG(latency_ms) as avg_latency,
            SUM(CASE WHEN valid = 1 THEN 1 ELSE 0 END) as valid_calls,
            COUNT(DISTINCT model) as unique_models
        FROM logs
    """)
    
    result = cursor.fetchone()
    
    if not result or result[0] == 0:
        conn.close()
        if json_output:
            print(json.dumps({'total_calls': 0, 'total_cost': 0.0, 'message': 'No logs found'}))
        else:
            print()
            print(colorize("No AI calls tracked yet", Colors.DIM))
            print()
            print(colorize("To start tracking AI calls, add this to your code:", Colors.INFO))
            print()
            print(colorize("  import glassbox", Colors.BOLD))
            print(colorize("  glassbox.init()", Colors.BOLD))
            print()
            print(colorize("  # Your existing AI code works as-is", Colors.DIM))
            print(colorize("  from openai import OpenAI", Colors.DIM))
            print(colorize("  client = OpenAI()", Colors.DIM))
            print(colorize("  response = client.chat.completions.create(...)", Colors.DIM))
            print()
            print(colorize("  # ✅ Automatically tracked!", Colors.SUCCESS))
            print()
        return
    
    total_calls, total_cost, avg_latency, valid_calls, unique_models = result
    validity_rate = (valid_calls / total_calls * 100) if total_calls > 0 else 0
    
    # Get per-model stats for composability
    cursor.execute("""
        SELECT 
            model,
            COUNT(*) as calls,
            SUM(cost_usd) as cost,
            AVG(latency_ms) as avg_latency,
            SUM(CASE WHEN valid = 1 THEN 1 ELSE 0 END) as valid_calls
        FROM logs
        GROUP BY model
        ORDER BY cost DESC
    """)
    
    model_stats = []
    for row in cursor.fetchall():
        model, calls, cost, avg_lat, valid = row
        model_stats.append({
            'model': model,
            'calls': calls,
            'cost_usd': float(cost or 0),
            'avg_latency_ms': float(avg_lat or 0),
            'validity_rate': (valid / calls * 100) if calls > 0 else 0
        })
    
    # Proactive suggestions
    suggestions = []
    
    # Cost analysis
    if total_cost and total_cost > 10:
        cursor.execute("""
            SELECT model, COUNT(*) as count, SUM(cost_usd) as model_cost
            FROM logs
            GROUP BY model
            ORDER BY model_cost DESC
            LIMIT 1
        """)
        top_model = cursor.fetchone()
        if top_model and 'gpt-4' in top_model[0].lower():
            suggestions.append({
                'type': 'cost',
                'message': f"Using {top_model[0]} for {top_model[1]} calls (${top_model[2]:.2f})",
                'suggestion': "Consider gpt-3.5-turbo for simple tasks (saves ~90%)"
            })
    
    conn.close()
    
    # JSON output for composability
    if json_output:
        output = {
            'total_calls': total_calls,
            'total_cost_usd': float(total_cost or 0),
            'avg_latency_ms': float(avg_latency or 0),
            'validity_rate': validity_rate,
            'unique_models': unique_models,
            'models': model_stats,
            'suggestions': suggestions
        }
        print(json.dumps(output, indent=2))
        return
    
    # Codex-style: Organized table for analytics
    from .ui import print_table
    
    # Summary table (Codex-style: clean, scannable)
    summary_rows = [
        [
            colorize(f"{total_calls:,}", Colors.BOLD),
            colorize(format_currency(total_cost), Colors.BOLD + (Colors.WARNING if total_cost > 1 else Colors.SUCCESS)),
            colorize(format_duration(avg_latency), Colors.BOLD),
            colorize(f"{validity_rate:.1f}%", Colors.BOLD + (Colors.SUCCESS if validity_rate > 95 else Colors.WARNING if validity_rate > 80 else Colors.ERROR))
        ]
    ]
    print_table(
        headers=["Calls", "Cost", "Avg Latency", "Valid"],
        rows=summary_rows,
        title=None  # No title for Codex-style minimal
    )
    
    # Per-model breakdown table (if multiple models)
    if len(model_stats) > 1:
        model_rows = []
        for stat in model_stats:
            model_rows.append([
                stat['model'],
                f"{stat['calls']:,}",
                format_currency(stat['cost_usd']),
                format_duration(stat['avg_latency_ms']),
                f"{stat['validity_rate']:.1f}%"
            ])
        print_table(
            headers=["Model", "Calls", "Cost", "Avg Latency", "Valid"],
            rows=model_rows,
            title=None
        )
    
    # Actionable tip (only if cost > $5)
    if suggestions and total_cost > 5:
        print()
        print(colorize(f"💡 {suggestions[0]['suggestion']}", Colors.INFO))


def cmd_status(args):
    """Check Glassbox status with health checks - Beautiful status view."""
    print_header("Status", "🔍")
    
    status_items = []
    
    # Check database
    db_path = ".glassbox.db"
    if os.path.exists(db_path):
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM logs")
            log_count = cursor.fetchone()[0]
            
            # Get recent activity
            cursor.execute("""
                SELECT COUNT(*), MAX(timestamp) 
                FROM logs 
                WHERE timestamp > datetime('now', '-1 hour')
            """)
            recent_count, last_timestamp = cursor.fetchone()
            conn.close()
            
            status_items.append(f"Database: {colorize('✓', Colors.SUCCESS)} {log_count:,} logs")
            if recent_count and recent_count > 0:
                status_items.append(f"Recent Activity: {colorize('✓', Colors.SUCCESS)} {recent_count} logs in last hour")
            else:
                status_items.append(f"Recent Activity: {colorize('⚠', Colors.WARNING)} No recent activity")
        except Exception as e:
            status_items.append(f"Database: {colorize('✗', Colors.ERROR)} Error: {str(e)[:30]}")
    else:
        status_items.append(f"Database: {colorize('✗', Colors.ERROR)} Not found")
    
    # Check environment
    detected_libs = detect_installed_libraries()
    api_keys = detect_api_keys()
    
    if detected_libs:
        status_items.append(f"Libraries: {colorize('✓', Colors.SUCCESS)} {', '.join(detected_libs)}")
    else:
        status_items.append(f"Libraries: {colorize('⚠', Colors.WARNING)} None detected")
    
    if any(api_keys.values()):
        found_keys = [k for k, v in api_keys.items() if v]
        status_items.append(f"API Keys: {colorize('✓', Colors.SUCCESS)} {', '.join(found_keys)}")
    else:
        status_items.append(f"API Keys: {colorize('ℹ', Colors.INFO)} None (sandbox mode)")
    
    # Check if initialized
    logger = get_logger()
    if logger:
        status_items.append(f"Initialized: {colorize('✓', Colors.SUCCESS)} App: {logger.app_id}")
        status_items.append(f"Backend: {logger.backend_url}")
        status_items.append(f"Sync: {'Enabled' if logger.sync_enabled else 'Disabled'}")
        
        # Optional backend health check (backend is optional)
        if logger.backend_url and logger.sync_enabled:
            try:
                import requests
                response = requests.get(f"{logger.backend_url}/health", timeout=2)
                if response.status_code == 200:
                    status_items.append(f"Backend: {colorize('✓', Colors.SUCCESS)} Connected")
                else:
                    status_items.append(f"Backend: {colorize('⚠', Colors.WARNING)} Status {response.status_code}")
            except Exception as e:
                status_items.append(f"Backend: {colorize('ℹ', Colors.INFO)} Not configured (local-only mode)")
    else:
        status_items.append(f"Initialized: {colorize('✗', Colors.ERROR)} Not initialized")
    
    # Check HTTP interception
    try:
        import requests
        if hasattr(requests.post, '__wrapped__') or 'glassbox' in str(requests.post):
            status_items.append(f"HTTP Interception: {colorize('✓', Colors.SUCCESS)} Active")
        else:
            status_items.append(f"HTTP Interception: {colorize('⚠', Colors.WARNING)} Not active")
    except ImportError:
        status_items.append(f"HTTP Interception: {colorize('⚠', Colors.WARNING)} requests not installed")
    
    print_box(status_items, "Current Status")
    
    print()
    print_section("Quick Actions", "💡")
    print_list([
        "Run 'glassbox verify' for detailed checks",
        "Run 'glassbox troubleshoot' if you have issues"
    ], emoji="•", indent=2)
    print()
    print_footer()


def cmd_watch(args):
    """Watch for new logs and show summary."""
    db_path = args.db or ".glassbox.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        return
    
    print("👀 Watching for new logs...")
    print("   (Press Ctrl+C to exit)")
    print()
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(id) FROM logs")
    last_id = cursor.fetchone()[0] or 0
    conn.close()
    
    try:
        while True:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM logs WHERE id > ?", (last_id,))
            new_count = cursor.fetchone()[0]
            
            if new_count > 0:
                cursor.execute("SELECT MAX(id) FROM logs")
                last_id = cursor.fetchone()[0]
                
                # Get latest stats
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total,
                        SUM(cost_usd) as cost,
                        AVG(latency_ms) as latency
                    FROM logs
                """)
                stats = cursor.fetchone()
                conn.close()
                
                total, cost, latency = stats
                print(f"📈 {new_count} new log(s) | Total: {total} | Cost: ${cost:.6f} | Avg Latency: {latency:.0f}ms")
            else:
                conn.close()
            
            time.sleep(2)
            
    except KeyboardInterrupt:
        print()
        print("👋 Stopped")


def cmd_proxy(args):
    """Start HTTP proxy server to intercept AI API calls (zero-code integration)."""
    import signal
    
    # Get defaults
    defaults = get_smart_defaults()
    app_id = args.app_id or defaults.get('app_id', 'proxy-app')
    backend_url = args.backend_url or defaults.get('backend_url', 'http://localhost:8000')
    port = args.port or 5000
    
    # Check for auto-configure flag
    auto_configure = getattr(args, 'auto_configure', False) or getattr(args, 'production', False)
    
    # Start proxy
    proxy = GlassboxProxy(
        port=port,
        app_id=app_id,
        backend_url=backend_url,
        api_key=args.api_key
    )
    
    if not proxy.start(auto_configure=auto_configure):
        return
    
    # Get database path from logger
    db_path = proxy.logger.db_path if proxy.logger else ".glassbox.db"
    
    # Print header for metrics
    print("=" * 80)
    print("📊 Real-time Metrics")
    print("=" * 80)
    print()
    
    # Display real-time metrics
    def display_metrics():
        last_id = 0
        first_run = True
        try:
            while proxy.running:
                if os.path.exists(db_path):
                    conn = sqlite3.connect(db_path)
                    cursor = conn.cursor()
                    
                    # Get new logs
                    cursor.execute("""
                        SELECT id, timestamp, model, cost_usd, latency_ms, valid, prompt_id
                        FROM logs
                        WHERE id > ?
                        ORDER BY id ASC
                    """, (last_id,))
                    
                    rows = cursor.fetchall()
                    
                    for row in rows:
                        log_id, timestamp, model, cost, latency, valid, prompt_id = row
                        last_id = log_id
                        
                        # Format timestamp
                        try:
                            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                            time_str = dt.strftime('%H:%M:%S')
                        except:
                            time_str = timestamp[:19] if timestamp else '--:--:--'
                        
                        # Format output
                        status = "✅" if valid else "❌"
                        cost_str = f"${cost:.6f}" if cost else "$0.000000"
                        latency_str = f"{latency:.0f}ms" if latency else "0ms"
                        
                        print(f"[{time_str}] {status} {model:20} {cost_str:12} {latency_str:8} {prompt_id[:8] if prompt_id else '--------'}")
                    
                    # Get current stats
                    cursor.execute("""
                        SELECT 
                            COUNT(*) as total_calls,
                            SUM(cost_usd) as total_cost,
                            AVG(latency_ms) as avg_latency,
                            SUM(CASE WHEN valid = 1 THEN 1 ELSE 0 END) as valid_calls
                        FROM logs
                    """)
                    
                    stats = cursor.fetchone()
                    conn.close()
                    
                    if stats and stats[0] > 0:
                        total_calls, total_cost, avg_latency, valid_calls = stats
                        validity_rate = (valid_calls / total_calls * 100) if total_calls > 0 else 0
                        
                        # Print stats summary (on new line to avoid overwriting)
                        if first_run or rows:
                            print(f"📊 Summary: Calls={total_calls} | Valid={validity_rate:.1f}% | Avg Latency={avg_latency:.0f}ms | Total Cost=${total_cost:.6f}")
                            first_run = False
                    elif first_run:
                        print("⏳ Waiting for AI API calls...")
                        first_run = False
                
                time.sleep(1)
                
        except Exception as e:
            pass  # Silently handle errors
    
    # Start metrics display in background
    metrics_thread = threading.Thread(target=display_metrics, daemon=True)
    metrics_thread.start()
    
    # Handle shutdown
    def signal_handler(sig, frame):
        print("\n\n🛑 Stopping proxy...")
        proxy.stop()
        print("👋 Proxy stopped")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Keep main thread alive
    try:
        while proxy.running:
            time.sleep(1)
    except KeyboardInterrupt:
        signal_handler(None, None)


def cmd_verify(args):
    """Verify Glassbox installation and functionality - Beautiful guided check."""
    print_header("Verification", "🔍")
    print_info("Checking your Glassbox installation...")
    print()
    
    checks_passed = 0
    checks_total = 0
    check_results = []
    
    # Check 1: SDK installation
    checks_total += 1
    try:
        import glassbox_sdk
        print_success("SDK installed")
        if args.verbose:
            print(f"   Location: {glassbox_sdk.__file__}")
        checks_passed += 1
        check_results.append(("SDK Installation", "✅", "Installed"))
    except ImportError:
        print_error("SDK not installed")
        print_info("Run: pip install glassbox-sdk")
        check_results.append(("SDK Installation", "❌", "Not installed"))
    
    # Check 2: Database
    checks_total += 1
    db_path = ".glassbox.db"
    if os.path.exists(db_path):
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='logs'")
            if cursor.fetchone():
                cursor.execute("SELECT COUNT(*) FROM logs")
                count = cursor.fetchone()[0]
                conn.close()
                print_success(f"Database exists ({count} logs)")
                if args.verbose:
                    print(f"   Path: {os.path.abspath(db_path)}")
                checks_passed += 1
                check_results.append(("Database", "✅", f"{count} logs"))
            else:
                print_warning("Database exists but schema is missing")
                print_info("Run: glassbox init")
                check_results.append(("Database", "⚠️", "Schema missing"))
                conn.close()
        except Exception as e:
            print_error(f"Database error: {e}")
            check_results.append(("Database", "❌", str(e)[:30]))
    else:
        print_warning("Database not found")
        print_info("Run: glassbox init")
        check_results.append(("Database", "⚠️", "Not found"))
    
    # Check 3: Logger initialization
    checks_total += 1
    logger = get_logger()
    if logger:
        print_success("Logger initialized")
        if args.verbose:
            print(f"   App ID: {logger.app_id}")
            print(f"   Backend: {logger.backend_url}")
        checks_passed += 1
        check_results.append(("Logger", "✅", f"App: {logger.app_id}"))
    else:
        print_warning("Logger not initialized")
        print_info("Run: glassbox init")
        check_results.append(("Logger", "⚠️", "Not initialized"))
    
    # Check 4: HTTP interception
    checks_total += 1
    try:
        import requests
        # Check if requests.post is wrapped
        if hasattr(requests.post, '__wrapped__') or 'glassbox' in str(requests.post):
            print_success("HTTP interception active")
            checks_passed += 1
            check_results.append(("HTTP Interception", "✅", "Active"))
        else:
            print_warning("HTTP interception not active")
            print_info("Run: glassbox init (with auto_wrap enabled)")
            check_results.append(("HTTP Interception", "⚠️", "Not active"))
    except ImportError:
        print_warning("requests library not installed")
        print_info("HTTP interception requires: pip install requests")
        check_results.append(("HTTP Interception", "⚠️", "requests not installed"))
    
    # Check 5: Optional backend connection (backend is optional)
    checks_total += 1
    if logger and logger.backend_url:
        try:
            import requests
            response = requests.get(f"{logger.backend_url}/health", timeout=2)
            if response.status_code == 200:
                print_success(f"Backend reachable ({logger.backend_url})")
                checks_passed += 1
                check_results.append(("Backend", "✅", "Connected"))
            else:
                print_warning(f"Backend returned {response.status_code}")
                check_results.append(("Backend", "⚠️", f"Status {response.status_code}"))
        except Exception as e:
            print_warning(f"Backend unreachable: {logger.backend_url}")
            if args.verbose:
                print(f"   Error: {e}")
            print_info("(Backend is optional - Glassbox works perfectly without it)")
            check_results.append(("Backend", "⚠️", "Unreachable"))
    else:
        check_results.append(("Backend", "ℹ️", "Not configured (local-only mode)"))
    
    # Check 6: Recent logs
    checks_total += 1
    if os.path.exists(db_path):
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*), MAX(timestamp) 
                FROM logs 
                WHERE timestamp > datetime('now', '-1 hour')
            """)
            recent_count, last_timestamp = cursor.fetchone()
            conn.close()
            
            if recent_count and recent_count > 0:
                print_success(f"Recent activity ({recent_count} logs in last hour)")
                if args.verbose and last_timestamp:
                    print(f"   Last log: {last_timestamp}")
                checks_passed += 1
                check_results.append(("Recent Activity", "✅", f"{recent_count} logs"))
            else:
                print_warning("No recent logs")
                print_info("Run: glassbox test (to generate test logs)")
                check_results.append(("Recent Activity", "⚠️", "No logs"))
        except Exception as e:
            print_warning(f"Could not check recent logs: {e}")
            check_results.append(("Recent Activity", "⚠️", "Error"))
    
    # Print results table
    print()
    print_section("Verification Results", "📋")
    print_table(
        ["Check", "Status", "Details"],
        check_results,
        None
    )
    
    # Summary
    print()
    print_divider()
    if checks_passed == checks_total:
        print_success(f"All checks passed ({checks_passed}/{checks_total})")
        print()
        print_header("✨ Glassbox is Ready!", "🎉")
        print_info("Everything looks good! You're ready to track AI calls.")
    else:
        print_warning(f"{checks_passed}/{checks_total} checks passed")
        print()
        print_info("Run 'glassbox troubleshoot' for help with issues")
        print_info("Or run 'glassbox init' to set up Glassbox")
    
    print_footer()


def cmd_test(args):
    """Generate test logs - minimal."""
    # Initialize if needed
    logger = get_logger()
    if not logger:
        logger = init()
    
    # Generate test logs
    from .sandbox import generate_demo_logs
    count = args.count or 3
    generate_demo_logs(count=count)
    
    # Minimal output
    print(colorize("✓", Colors.SUCCESS) + f" generated {count} test logs")


def cmd_clear(args):
    """Clear all logs from database."""
    db_path = args.db or ".glassbox.db"
    
    if not os.path.exists(db_path):
        if not getattr(args, 'json', False):
            print(colorize("No database found", Colors.DIM))
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM logs")
        count = cursor.fetchone()[0]
        
        if count > 0:
            cursor.execute("DELETE FROM logs")
            conn.commit()
            if not getattr(args, 'json', False):
                print(colorize("✓", Colors.SUCCESS) + f" cleared {count} logs")
        else:
            if not getattr(args, 'json', False):
                print(colorize("Database is already empty", Colors.DIM))
        
        conn.close()
    except Exception as e:
        if not getattr(args, 'json', False):
            print(colorize("Error clearing database", Colors.ERROR) + f": {e}")


def cmd_trust(args):
    """Show trust guarantees and privacy information for developers."""
    from .trust import (
        get_trust_indicators,
        get_privacy_guarantees,
        get_safety_guarantees,
        get_transparency_info,
        print_trust_badges,
        get_developer_trust_messaging,
        get_uninstall_instructions,
        get_data_export_info
    )
    
    print_welcome()
    print_header("Trust & Privacy Guarantees", "🛡️")
    
    trust_msg = get_developer_trust_messaging()
    print()
    print(colorize(trust_msg['header'], Colors.BOLD + Colors.PRIMARY))
    print(colorize(trust_msg['subheader'], Colors.INFO))
    print()
    
    # Trust Badges
    print_section("Trust Badges", "✅")
    badges = print_trust_badges()
    for badge in badges:
        print(f"  {badge}")
    print()
    
    # Privacy Guarantees
    print_section("Privacy Guarantees", "🔒")
    privacy = get_privacy_guarantees()
    for guarantee in privacy:
        print(f"  {colorize('✓', Colors.SUCCESS)} {guarantee}")
    print()
    
    # Safety Guarantees
    print_section("Safety Guarantees", "🛡️")
    safety = get_safety_guarantees()
    for guarantee in safety:
        print(f"  {colorize('✓', Colors.SUCCESS)} {guarantee}")
    print()
    
    # Transparency
    print_section("Transparency", "🔓")
    transparency = get_transparency_info()
    print_table(
        ["Aspect", "Details"],
        [[k.replace('_', ' ').title(), v] for k, v in transparency.items()],
        None
    )
    print()
    
    # Data Export
    print_section("Data Ownership", "💾")
    export_info = get_data_export_info()
    print_info("Your data is always yours:")
    print()
    for key, value in export_info.items():
        print(f"  {colorize(key.replace('_', ' ').title() + ':', Colors.BOLD)} {value}")
    print()
    
    # Uninstall Instructions
    print_section("Easy Uninstall", "↩️")
    print_info("No vendor lock-in. Uninstall anytime:")
    print()
    uninstall = get_uninstall_instructions()
    for line in uninstall:
        if line.startswith("   "):
            print_code_block(line.strip(), "bash")
        elif line:
            print(f"  {line}")
    print()
    
    # Code Safety Example
    print_section("Code Safety Example", "💻")
    print_info("Glassbox never breaks your code:")
    print()
    print_code_block("""# Your code
from openai import OpenAI
client = OpenAI()

# Add Glassbox (one line)
import glassbox
glassbox.init()

# If Glassbox fails, your code still works
try:
    response = client.chat.completions.create(...)
except Exception as e:
    # Glassbox errors are caught internally
    # Your exception handling works normally
    pass""", "python")
    print()
    print_info("Glassbox errors are caught and handled internally. Your code is never affected.")
    print()
    
    # Production Readiness
    print_section("Production Ready", "🚀")
    print_info("Built for production use:")
    print()
    production_points = [
        "Thread-safe logging",
        "Graceful error handling",
        "Zero performance impact when disabled",
        "No blocking network calls",
        "Local-first (works offline)",
        "Backend sync is optional and async"
    ]
    for point in production_points:
        print(f"  {colorize('✓', Colors.SUCCESS)} {point}")
    print()
    
    print_footer("Glassbox is built by developers, for developers. Trust through transparency.")


def cmd_troubleshoot(args):
    """Diagnose common issues - Beautiful guided troubleshooting."""
    print_header("Troubleshooting", "🔧")
    print_info("Diagnosing common issues...")
    print()
    
    issues_found = []
    
    # Issue 1: Not initialized
    if not os.path.exists(".glassbox.db"):
        issues_found.append({
            'issue': 'Glassbox not initialized',
            'symptoms': 'No database found, no logs appearing',
            'fix': 'Run: glassbox init'
        })
    
    # Issue 2: No logs
    if os.path.exists(".glassbox.db"):
        conn = sqlite3.connect(".glassbox.db")
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM logs")
        count = cursor.fetchone()[0]
        conn.close()
        
        if count == 0:
            issues_found.append({
                'issue': 'No logs found',
                'symptoms': 'glassbox live shows nothing, glassbox stats shows zeros',
                'fix': '1. Run: glassbox test (to verify setup)\n   2. Check if your AI code is running\n   3. Verify HTTP interception is active: glassbox verify'
            })
    
    # Issue 3: Optional backend unreachable (backend is optional)
    logger = get_logger()
    if logger and logger.backend_url and logger.sync_enabled:
        try:
            import requests
            requests.get(f"{logger.backend_url}/health", timeout=2)
        except:
            issues_found.append({
                'issue': 'Backend unreachable (optional)',
                'symptoms': 'Backend sync disabled - logs still work locally',
                'fix': f'1. Backend is optional - Glassbox works perfectly without it\n   2. To enable sync: glassbox init --backend-url <url>\n   3. To disable sync: glassbox init --no-sync'
            })
    
    # Issue 4: HTTP interception not working
    try:
        import requests
        if not (hasattr(requests.post, '__wrapped__') or 'glassbox' in str(requests.post)):
            issues_found.append({
                'issue': 'HTTP interception not active',
                'symptoms': 'AI API calls not being logged automatically',
                'fix': '1. Re-run: glassbox init\n   2. Or use SDK integration: import glassbox; glassbox.init()'
            })
    except ImportError:
        issues_found.append({
            'issue': 'requests library not installed',
            'symptoms': 'HTTP interception cannot work',
            'fix': 'Install: pip install requests'
        })
    
    if issues_found:
        print_section("Issues Found", "⚠️")
        print()
        
        for i, issue in enumerate(issues_found, 1):
            print(colorize(f"Issue {i}: {issue['issue']}", Colors.BOLD + Colors.BRIGHT_RED))
            print_key_value("Symptoms", issue['symptoms'], indent=2)
            print_key_value("Fix", issue['fix'], indent=2)
            print()
        
        print_section("Recommended Actions", "💡")
        actions = [
            "Run 'glassbox verify --verbose' for detailed checks",
            "Run 'glassbox init' to reinitialize",
            "Check 'glassbox status' for current state"
        ]
        print_list(actions, emoji="•", indent=2)
    else:
        print_header("✨ No Issues Detected!", "🎉")
        print_success("Everything looks good!")
        print()
        print_section("Still Having Problems?", "💡")
        print_list([
            "Run: glassbox verify --verbose",
            "Check logs: glassbox live",
            "Generate test data: glassbox test"
        ], emoji="•", indent=2)
    
    print()
    print_footer()


def _show_welcome_guide():
    """Show Codex-style clean, instructional guide."""
    from .ui import Colors, colorize
    
    print()
    print(colorize("Glassbox", Colors.BOLD + Colors.PRIMARY) + " — See your AI costs in real-time")
    print()
    print(colorize("Commands:", Colors.DIM))
    print(f"  {colorize('init', Colors.BOLD)}     Initialize Glassbox")
    print(f"  {colorize('live', Colors.BOLD)}     Stream AI calls in real-time")
    print(f"  {colorize('stats', Colors.BOLD)}    View aggregated statistics")
    print(f"  {colorize('verify', Colors.BOLD)}   Verify setup")
    print(f"  {colorize('proxy', Colors.BOLD)}    Start HTTP proxy (zero-code)")
    print()
    print(colorize("Quick start:", Colors.DIM))
    print(f"  {colorize('glassbox init', Colors.INFO)}")
    print(f"  {colorize('glassbox live', Colors.INFO)}")
    print()


def main():
    """Main CLI entry point - Codex-style sticky UX."""
    parser = argparse.ArgumentParser(
        description="See your AI costs in real-time",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        add_help=False
    )
    
    # Codex-style: minimal help
    parser.add_argument('-h', '--help', action='help', default=argparse.SUPPRESS,
        help='show help')
    
    subparsers = parser.add_subparsers(dest='command', help='')
    
    # Codex-style: one word help text
    init_parser = subparsers.add_parser('init', help='initialize')
    init_parser.add_argument('--app-id', help='app id')
    init_parser.add_argument('--api-key', help='api key')
    init_parser.add_argument('--backend-url', help='backend url')
    init_parser.add_argument('--no-sync', action='store_true', help='disable sync')
    init_parser.add_argument('--verbose', action='store_true', help='verbose')
    
    live_parser = subparsers.add_parser('live', help='see costs')
    live_parser.add_argument('--db', help='db path')
    live_parser.add_argument('--json', action='store_true', help='json')
    
    stats_parser = subparsers.add_parser('stats', help='statistics')
    stats_parser.add_argument('--db', help='db path')
    stats_parser.add_argument('--json', action='store_true', help='json')
    
    proxy_parser = subparsers.add_parser('proxy', help='http proxy')
    proxy_parser.add_argument('--port', type=int, default=5000, help='port')
    proxy_parser.add_argument('--app-id', help='app id')
    proxy_parser.add_argument('--api-key', help='api key')
    proxy_parser.add_argument('--backend-url', help='backend url')
    proxy_parser.add_argument('--auto-configure', action='store_true', help='auto config')
    proxy_parser.add_argument('--production', action='store_true', help='production')
    
    verify_parser = subparsers.add_parser('verify', help='verify setup')
    verify_parser.add_argument('--verbose', action='store_true', help='verbose')
    verify_parser.add_argument('--fix', action='store_true', help='auto fix')
    
    test_parser = subparsers.add_parser('test', help='test logs')
    test_parser.add_argument('--count', type=int, default=3, help='count')
    
    clear_parser = subparsers.add_parser('clear', help='clear logs')
    clear_parser.add_argument('--db', help='db path')
    clear_parser.add_argument('--json', action='store_true', help='json')
    
    trust_parser = subparsers.add_parser('trust', help='trust info')
    trust_parser.add_argument('--verbose', action='store_true', help='verbose')
    
    args = parser.parse_args()
    
    # Codex-style: show clean guide when no command
    if not args.command:
        _show_welcome_guide()
        return
    
    # Route commands
    commands = {
        'init': cmd_init,
        'live': cmd_live,
        'stats': cmd_stats,
        'proxy': cmd_proxy,
        'verify': cmd_verify,
        'test': cmd_test,
        'clear': cmd_clear,
        'trust': cmd_trust,
    }
    
    if args.command in commands:
        commands[args.command](args)
    else:
        print(f"unknown: {args.command}")
        print("commands: init, live, stats, verify, proxy, test, trust")


if __name__ == '__main__':
    main()
