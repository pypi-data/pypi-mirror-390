"""
GNU Parallel-style live metrics display for terminal-first developers.
Instant, actionable, composable.
"""

import sys
import time
import json
from typing import Optional, Dict, List
from datetime import datetime
from .ui import Colors, colorize, format_currency, format_duration


class LiveMetricsDisplay:
    """
    GNU Parallel-style live metrics display.
    Real-time, color-coded, actionable insights.
    """
    
    def __init__(self, json_output: bool = False):
        self.json_output = json_output
        self.start_time = time.time()
        self.call_count = 0
        self.total_cost = 0.0
        self.failures = []
        self.slow_calls = []  # Track top slowest calls
        self.model_stats = {}  # Per-model statistics
        
    def display_header(self):
        """Display Codex-style minimal header."""
        if self.json_output:
            return
        # Codex-style: no header, just start
    
    def display_call(self, model: str, latency_ms: float, cost: float, valid: bool, prompt_id: str = ""):
        """Display a single AI call - delightful, color-coded, beautiful."""
        self.call_count += 1
        self.total_cost += cost
        
        # Codex-style: Show minimal header on first call
        if self.call_count == 1:
            header = f"{'':2} {'Model':20} {'Latency':10} {'Cost':12}"
            print(colorize(header, Colors.DIM + Colors.BOLD))
            print(colorize("─" * 46, Colors.DIM))
        
        # Track slow calls
        if latency_ms > 1000:  # > 1 second
            self.slow_calls.append({
                'model': model,
                'latency': latency_ms,
                'cost': cost,
                'valid': valid,
                'prompt_id': prompt_id[:8] if prompt_id else ''
            })
            # Keep only top 3 slowest
            self.slow_calls.sort(key=lambda x: x['latency'], reverse=True)
            self.slow_calls = self.slow_calls[:3]
        
        # Track failures
        if not valid:
            self.failures.append({
                'model': model,
                'latency': latency_ms,
                'cost': cost,
                'prompt_id': prompt_id[:8] if prompt_id else ''
            })
        
        # Update model stats
        if model not in self.model_stats:
            self.model_stats[model] = {
                'calls': 0,
                'total_cost': 0.0,
                'total_latency': 0.0,
                'valid_calls': 0
            }
        
        self.model_stats[model]['calls'] += 1
        self.model_stats[model]['total_cost'] += cost
        self.model_stats[model]['total_latency'] += latency_ms
        if valid:
            self.model_stats[model]['valid_calls'] += 1
        
        if self.json_output:
            # JSON output for composability
            print(json.dumps({
                'timestamp': datetime.utcnow().isoformat(),
                'model': model,
                'latency_ms': latency_ms,
                'cost_usd': cost,
                'valid': valid,
                'prompt_id': prompt_id
            }))
            return
        
        # Delightful UX: Color-coded, emoji-rich, beautiful output
        model_display = model[:18] if len(model) <= 18 else model[:15] + "..."
        cost_display = format_currency(cost)
        latency_display = format_duration(latency_ms)
        
        # Status with emoji and color
        if valid:
            if latency_ms < 200:  # Fast
                status = colorize("⚡", Colors.BRIGHT_GREEN)
            elif latency_ms < 1000:  # Normal
                status = colorize("✓", Colors.SUCCESS)
            else:  # Slow but valid
                status = colorize("🐌", Colors.WARNING)
        else:
            status = colorize("❌", Colors.ERROR)
        
        # Color-code latency (green=fast, yellow=slow, red=very slow)
        if latency_ms < 200:
            latency_color = Colors.BRIGHT_GREEN
        elif latency_ms < 1000:
            latency_color = Colors.SUCCESS
        elif latency_ms < 2000:
            latency_color = Colors.WARNING
        else:
            latency_color = Colors.ERROR
        
        latency_display = colorize(latency_display, latency_color)
        
        # Color-code cost (subtle highlight for expensive calls)
        if cost > 0.01:
            cost_display = colorize(cost_display, Colors.WARNING)
        elif cost > 0.001:
            cost_display = colorize(cost_display, Colors.INFO)
        else:
            cost_display = colorize(cost_display, Colors.SUCCESS)
        
        # Codex-style: Clean, minimal table row
        model_col = colorize(model_display, Colors.BOLD)
        print(f"{status} {model_col:20} {latency_display:10} {cost_display:12}")
        sys.stdout.flush()
    
    def display_summary(self):
        """Display beautiful, scannable summary with delightful touches."""
        if self.json_output:
            summary = {
                'total_calls': self.call_count,
                'total_cost_usd': self.total_cost,
                'total_time_seconds': time.time() - self.start_time,
                'failures': len(self.failures),
                'failure_rate': (len(self.failures) / self.call_count * 100) if self.call_count > 0 else 0,
                'slow_calls': self.slow_calls,
                'model_stats': self.model_stats
            }
            print(json.dumps(summary, indent=2))
            return
        
        elapsed = time.time() - self.start_time
        failure_rate = (len(self.failures) / self.call_count * 100) if self.call_count > 0 else 0
        avg_latency = sum(s['total_latency'] / s['calls'] for s in self.model_stats.values()) / len(self.model_stats) if self.model_stats else 0
        validity_rate = (sum(s['valid_calls'] for s in self.model_stats.values()) / self.call_count * 100) if self.call_count > 0 else 0
        
        print()
        # Codex-style: Organized summary table
        from .ui import print_table
        
        # Summary table
        summary_rows = [[
            colorize(f"{self.call_count:,}", Colors.BOLD),
            colorize(format_currency(self.total_cost), Colors.BOLD + (Colors.WARNING if self.total_cost > 1 else Colors.SUCCESS)),
            colorize(format_duration(avg_latency), Colors.BOLD),
            colorize(f"{validity_rate:.1f}%", Colors.BOLD + (Colors.SUCCESS if validity_rate > 95 else Colors.WARNING if validity_rate > 80 else Colors.ERROR)),
            colorize(format_duration(elapsed * 1000), Colors.DIM)
        ]]
        print_table(
            headers=["Calls", "Cost", "Avg Latency", "Valid", "Time"],
            rows=summary_rows,
            title=None
        )
        
        # Top models table (if multiple)
        if len(self.model_stats) > 1:
            sorted_models = sorted(self.model_stats.items(), key=lambda x: x[1]['total_cost'], reverse=True)
            model_rows = []
            for model, stats in sorted_models[:5]:  # Top 5
                model_valid = (stats['valid_calls'] / stats['calls'] * 100) if stats['calls'] > 0 else 0
                model_rows.append([
                    model,
                    f"{stats['calls']:,}",
                    format_currency(stats['total_cost']),
                    format_duration(stats['total_latency'] / stats['calls']),
                    f"{model_valid:.1f}%"
                ])
            print_table(
                headers=["Model", "Calls", "Cost", "Avg Latency", "Valid"],
                rows=model_rows,
                title=None
            )
        
        # Smart suggestions (contextual, helpful)
        self._display_smart_tips()
        
        print(colorize("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", Colors.DIM))
        print()
    
    def _display_smart_tips(self):
        """Display smart, contextual tips - delightful and helpful."""
        tips = []
        
        # Cost optimization tips
        if self.total_cost > 10:
            tips.append({
                'icon': '💰',
                'priority': 'high',
                'message': f"Spending {format_currency(self.total_cost)}",
                'suggestion': "Try gpt-3.5-turbo for simple tasks (saves ~90%)"
            })
        elif self.total_cost > 1:
            tips.append({
                'icon': '💡',
                'priority': 'medium',
                'message': f"Cost: {format_currency(self.total_cost)}",
                'suggestion': "Consider model optimization for cost savings"
            })
        
        # Latency optimization tips
        if self.slow_calls:
            avg_slow = sum(c['latency'] for c in self.slow_calls) / len(self.slow_calls)
            if avg_slow > 2000:
                tips.append({
                    'icon': '⚡',
                    'priority': 'high',
                    'message': f"Slow calls detected ({format_duration(avg_slow)} avg)",
                    'suggestion': "Batch prompts or use faster models (claude-3-haiku, gpt-3.5-turbo)"
                })
        
        # Failure analysis tips
        if self.failures:
            failure_rate = (len(self.failures) / self.call_count * 100) if self.call_count > 0 else 0
            if failure_rate > 10:
                tips.append({
                    'icon': '⚠️',
                    'priority': 'high',
                    'message': f"High failure rate: {failure_rate:.1f}%",
                    'suggestion': "Check API keys and rate limits"
                })
            elif failure_rate > 5:
                tips.append({
                    'icon': '💡',
                    'priority': 'medium',
                    'message': f"Failure rate: {failure_rate:.1f}%",
                    'suggestion': "Review patterns with 'glassbox stats'"
                })
        
        # Model efficiency tips
        if len(self.model_stats) > 1:
            most_expensive = max(self.model_stats.items(), key=lambda x: x[1]['total_cost'])
            if 'gpt-4' in most_expensive[0].lower() and most_expensive[1]['total_cost'] > 5:
                tips.append({
                    'icon': '💡',
                    'priority': 'medium',
                    'message': f"{most_expensive[0]}: {format_currency(most_expensive[1]['total_cost'])}",
                    'suggestion': "Use gpt-3.5-turbo for non-critical tasks (saves ~90%)"
                })
        
        # Show only top 2 tips (don't overwhelm)
        if tips:
            # Sort by priority (high first)
            priority_order = {'high': 0, 'medium': 1, 'low': 2}
            tips.sort(key=lambda x: priority_order.get(x.get('priority', 'low'), 2))
            tips = tips[:2]  # Top 2 only
            
            print(colorize("💡 Smart Suggestions", Colors.BOLD + Colors.INFO))
            print()
            for tip in tips:
                print(f"  {tip['icon']} {colorize(tip['message'], Colors.INFO)}")
                print(f"     {colorize('→', Colors.DIM)} {tip['suggestion']}")
                print()


def format_live_metrics_json(metrics: List[Dict]) -> str:
    """Format metrics as JSON for composability."""
    return json.dumps(metrics, indent=2)


def get_actionable_tips(metrics: Dict) -> List[str]:
    """Generate actionable tips from metrics."""
    tips = []
    
    total_cost = metrics.get('total_cost', 0)
    avg_latency = metrics.get('avg_latency', 0)
    failure_rate = metrics.get('failure_rate', 0)
    
    if total_cost > 10:
        tips.append("💰 High cost detected. Consider using cheaper models for simple tasks.")
    
    if avg_latency > 2000:
        tips.append("⚡ High latency. Consider batching or using faster models.")
    
    if failure_rate > 5:
        tips.append("⚠️ High failure rate. Review failing calls to identify patterns.")
    
    return tips

