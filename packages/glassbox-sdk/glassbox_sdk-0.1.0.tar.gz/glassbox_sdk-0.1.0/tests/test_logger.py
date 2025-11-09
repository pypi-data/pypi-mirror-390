"""
Pytest tests for Glassbox logger.
"""

import pytest
import sqlite3
import os
import tempfile
from glassbox_sdk.logger import GlassboxLogger, init, get_logger


class TestGlassboxLogger:
    """Test GlassboxLogger class."""
    
    def test_init_creates_database(self):
        """Test that logger initialization creates database."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            # Use environment variable to set custom db path
            import os as os_module
            original_env = os_module.environ.get('GLASSBOX_DB_PATH')
            os_module.environ['GLASSBOX_DB_PATH'] = db_path
            try:
                logger = GlassboxLogger(app_id="test-app")
                assert os.path.exists(db_path)
                assert logger.app_id == "test-app"
            finally:
                if original_env:
                    os_module.environ['GLASSBOX_DB_PATH'] = original_env
                elif 'GLASSBOX_DB_PATH' in os_module.environ:
                    del os_module.environ['GLASSBOX_DB_PATH']
    
    def test_log_creates_entry(self):
        """Test that log() creates database entry."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            import os as os_module
            original_env = os_module.environ.get('GLASSBOX_DB_PATH')
            os_module.environ['GLASSBOX_DB_PATH'] = db_path
            try:
                logger = GlassboxLogger(app_id="test-app")
            
            logger.log(
                model="gpt-4",
                input_tokens=100,
                output_tokens=50,
                latency_ms=250.0,
                cost_usd=0.005,
                valid=True
            )
            
                # Verify entry in database
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM logs")
                count = cursor.fetchone()[0]
                conn.close()
                
                assert count == 1
            finally:
                if original_env:
                    os_module.environ['GLASSBOX_DB_PATH'] = original_env
                elif 'GLASSBOX_DB_PATH' in os_module.environ:
                    del os_module.environ['GLASSBOX_DB_PATH']
    
    def test_log_handles_errors_gracefully(self):
        """Test that log() handles errors without breaking."""
        # Use invalid database path to trigger error
        import os as os_module
        original_env = os_module.environ.get('GLASSBOX_DB_PATH')
        os_module.environ['GLASSBOX_DB_PATH'] = "/invalid/path/test.db"
        try:
            logger = GlassboxLogger(app_id="test-app")
        
            # Should not raise exception
            logger.log(
                model="gpt-4",
                input_tokens=100,
                output_tokens=50,
                latency_ms=250.0,
                cost_usd=0.005,
                valid=True
            )
            
            # Should not crash
            assert True
        finally:
            if original_env:
                os_module.environ['GLASSBOX_DB_PATH'] = original_env
            elif 'GLASSBOX_DB_PATH' in os_module.environ:
                del os_module.environ['GLASSBOX_DB_PATH']
    
    def test_init_function(self):
        """Test init() function."""
        logger = init(app_id="test-init", sync_enabled=False)
        
        assert logger is not None
        assert logger.app_id == "test-init"
        assert logger.sync_enabled is False
    
    def test_get_logger(self):
        """Test get_logger() function."""
        # Should return None if not initialized
        logger = get_logger()
        assert logger is None
        
        # Initialize and get logger
        init(app_id="test-get")
        logger = get_logger()
        assert logger is not None
        assert logger.app_id == "test-get"


class TestLoggerErrorHandling:
    """Test error handling in logger."""
    
    def test_database_lock_handled(self):
        """Test that database locks don't crash."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            import os as os_module
            original_env = os_module.environ.get('GLASSBOX_DB_PATH')
            os_module.environ['GLASSBOX_DB_PATH'] = db_path
            try:
                logger = GlassboxLogger(app_id="test-app")
                
                # Create multiple loggers to test concurrency
                logger2 = GlassboxLogger(app_id="test-app")
            
            # Both should be able to log without crashing
            logger.log(
                model="gpt-4",
                input_tokens=100,
                output_tokens=50,
                latency_ms=250.0,
                cost_usd=0.005,
                valid=True
            )
            
                logger2.log(
                    model="gpt-3.5",
                    input_tokens=50,
                    output_tokens=25,
                    latency_ms=100.0,
                    cost_usd=0.001,
                    valid=True
                )
                
                # Should not crash
                assert True
            finally:
                if original_env:
                    os_module.environ['GLASSBOX_DB_PATH'] = original_env
                elif 'GLASSBOX_DB_PATH' in os_module.environ:
                    del os_module.environ['GLASSBOX_DB_PATH']

