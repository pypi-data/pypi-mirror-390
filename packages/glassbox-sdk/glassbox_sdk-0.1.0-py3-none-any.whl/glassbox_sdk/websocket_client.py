"""
WebSocket client for CLI to receive real-time metrics from backend
"""

import asyncio
import json
import sys
from typing import Optional, Callable
from datetime import datetime

try:
    import websockets
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False


class GlassboxWebSocketClient:
    """WebSocket client for real-time metrics"""
    
    def __init__(self, backend_url: str = "http://localhost:8000", app_id: Optional[str] = None):
        self.backend_url = backend_url.replace('http://', 'ws://').replace('https://', 'wss://')
        self.app_id = app_id
        self.connected = False
        self.callbacks = []
    
    def on_metrics(self, callback: Callable):
        """Register callback for metrics updates"""
        self.callbacks.append(callback)
    
    async def connect(self):
        """Connect to WebSocket server"""
        if not WEBSOCKETS_AVAILABLE:
            print("⚠️  websockets library not installed. Install with: pip install websockets")
            return False
        
        ws_url = f"{self.backend_url}/ws/metrics"
        if self.app_id:
            ws_url += f"?app_id={self.app_id}"
        
        try:
            self.websocket = await websockets.connect(ws_url)
            self.connected = True
            return True
        except Exception as e:
            print(f"❌ Failed to connect to WebSocket: {e}")
            return False
    
    async def listen(self):
        """Listen for messages from WebSocket"""
        if not self.connected:
            return
        
        try:
            async for message in self.websocket:
                data = json.loads(message)
                
                if data.get('type') == 'metrics':
                    # Call registered callbacks
                    for callback in self.callbacks:
                        callback(data.get('data', {}))
                
                elif data.get('type') == 'new_log':
                    # Handle new log entry
                    log_data = data.get('data', {})
                    self._handle_new_log(log_data)
        
        except Exception as e:
            print(f"❌ WebSocket error: {e}")
            self.connected = False
    
    def _handle_new_log(self, log_data: dict):
        """Handle new log entry"""
        # Format and print log entry
        timestamp = log_data.get('timestamp', '')
        model = log_data.get('model', 'unknown')
        cost = log_data.get('cost_usd', 0.0)
        latency = log_data.get('latency_ms', 0)
        valid = log_data.get('valid', True)
        prompt_id = log_data.get('prompt_id', '')
        
        # Format timestamp
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            time_str = dt.strftime('%H:%M:%S')
        except:
            time_str = timestamp[:19] if timestamp else '--:--:--'
        
        # Print formatted log
        status = "✓" if valid else "✗"
        cost_str = f"${cost:.6f}" if cost else "$0.000000"
        latency_str = f"{latency:.0f}ms"
        
        print(f"[{time_str}] {status} {model:20} {cost_str:12} {latency_str:8} {prompt_id[:8]}")
    
    async def disconnect(self):
        """Disconnect from WebSocket"""
        if self.connected:
            await self.websocket.close()
            self.connected = False


async def connect_and_listen(backend_url: str = "http://localhost:8000", app_id: Optional[str] = None):
    """Connect to WebSocket and listen for metrics"""
    client = GlassboxWebSocketClient(backend_url, app_id)
    
    if await client.connect():
        print("✅ Connected to Glassbox backend")
        print("📊 Receiving real-time metrics...")
        print()
        
        # Register callback for metrics updates
        def on_metrics(metrics: dict):
            if metrics.get('total_calls', 0) > 0:
                total = metrics.get('total_calls', 0)
                cost = metrics.get('total_cost', 0.0)
                latency = metrics.get('avg_latency', 0.0)
                validity = metrics.get('validity_rate', 0.0)
                
                print(f"📊 Summary: Calls={total} | Valid={validity:.1f}% | Avg Latency={latency:.0f}ms | Total Cost=${cost:.6f}")
        
        client.on_metrics(on_metrics)
        
        # Listen for messages
        await client.listen()
    else:
        print("⚠️  Falling back to local database polling")

