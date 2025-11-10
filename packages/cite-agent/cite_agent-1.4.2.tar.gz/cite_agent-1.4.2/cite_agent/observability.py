"""
Comprehensive Observability System
Metrics collection, tracing, and analytics for decision making
"""

import json
import time
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class EventType(Enum):
    """Types of observable events"""
    REQUEST_QUEUED = "request_queued"
    REQUEST_STARTED = "request_started"
    REQUEST_COMPLETED = "request_completed"
    REQUEST_FAILED = "request_failed"
    REQUEST_TIMEOUT = "request_timeout"
    
    API_CALL = "api_call"
    API_CALL_SUCCESS = "api_call_success"
    API_CALL_FAILURE = "api_call_failure"
    
    CIRCUIT_BREAKER_STATE_CHANGE = "circuit_breaker_state_change"
    RATE_LIMIT_HIT = "rate_limit_hit"
    QUEUE_FULL = "queue_full"
    
    PROVIDER_SWITCH = "provider_switch"
    FALLBACK_ACTIVATED = "fallback_activated"
    DEGRADATION_MODE = "degradation_mode"


@dataclass
class ObservableEvent:
    """A single observable event"""
    event_type: EventType
    timestamp: datetime = field(default_factory=datetime.now)
    user_id: Optional[str] = None
    request_id: Optional[str] = None
    duration_ms: Optional[float] = None  # For timing events
    status: Optional[str] = None  # success, failure, etc.
    provider: Optional[str] = None  # api provider used
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        data['event_type'] = self.event_type.value
        data['timestamp'] = self.timestamp.isoformat()
        return data


class Histogram:
    """Simple histogram for tracking value distributions"""
    
    def __init__(self, name: str, buckets: List[float] = None):
        self.name = name
        self.buckets = buckets or [0.01, 0.05, 0.1, 0.5, 1.0, 5.0, 10.0]
        self.values: Dict[float, int] = {b: 0 for b in self.buckets}
        self.values['inf'] = 0
        self.all_values = []
    
    def observe(self, value: float):
        """Record a value"""
        self.all_values.append(value)
        for bucket in self.buckets:
            if value <= bucket:
                self.values[bucket] += 1
                return
        self.values['inf'] += 1
    
    def get_percentile(self, p: float) -> float:
        """Get percentile (0.0-1.0)"""
        if not self.all_values:
            return 0.0
        sorted_vals = sorted(self.all_values)
        idx = int(len(sorted_vals) * p)
        return sorted_vals[min(idx, len(sorted_vals) - 1)]
    
    def get_stats(self) -> Dict[str, float]:
        """Get distribution statistics"""
        if not self.all_values:
            return {"count": 0}
        
        sorted_vals = sorted(self.all_values)
        return {
            "count": len(sorted_vals),
            "min": sorted_vals[0],
            "max": sorted_vals[-1],
            "mean": sum(sorted_vals) / len(sorted_vals),
            "p50": self.get_percentile(0.5),
            "p95": self.get_percentile(0.95),
            "p99": self.get_percentile(0.99),
        }


@dataclass
class ProviderMetrics:
    """Metrics for a specific API provider"""
    provider_name: str
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    total_latency_ms: float = 0.0
    latency_histogram: Histogram = field(default_factory=lambda: Histogram("latency"))
    error_counts: Dict[str, int] = field(default_factory=dict)
    last_used: Optional[datetime] = None
    
    def record_success(self, latency_ms: float):
        """Record successful API call"""
        self.total_calls += 1
        self.successful_calls += 1
        self.total_latency_ms += latency_ms
        self.latency_histogram.observe(latency_ms / 1000.0)  # Convert to seconds
        self.last_used = datetime.now()
    
    def record_failure(self, error_type: str, latency_ms: float = 0):
        """Record failed API call"""
        self.total_calls += 1
        self.failed_calls += 1
        self.total_latency_ms += latency_ms
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1
        self.last_used = datetime.now()
    
    def get_success_rate(self) -> float:
        """Get success rate 0.0-1.0"""
        if self.total_calls == 0:
            return 0.0
        return self.successful_calls / self.total_calls
    
    def get_avg_latency_ms(self) -> float:
        """Get average latency in ms"""
        if self.total_calls == 0:
            return 0.0
        return self.total_latency_ms / self.total_calls


@dataclass
class UserBehaviorMetrics:
    """Metrics about a specific user's behavior"""
    user_id: str
    total_requests: int = 0
    total_api_calls: int = 0
    total_failures: int = 0
    most_common_provider: Optional[str] = None
    avg_requests_per_hour: float = 0.0
    first_seen: datetime = field(default_factory=datetime.now)
    last_seen: Optional[datetime] = None
    preferred_providers: Dict[str, int] = field(default_factory=dict)


class ObservabilitySystem:
    """
    Central observability system collecting metrics from all components
    
    Tracks:
    - Request latencies (p50, p95, p99)
    - Provider performance (success rate, latency, errors)
    - User behavior patterns
    - Error types and frequencies
    - Circuit breaker state changes
    - Rate limit hits and queue fills
    """
    
    def __init__(self, storage_dir: Optional[Path] = None):
        self.storage_dir = storage_dir or Path.home() / ".nocturnal_archive" / "observability"
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Event log
        self.events: List[ObservableEvent] = []
        self.event_index = 0
        
        # Metrics
        self.provider_metrics: Dict[str, ProviderMetrics] = {}
        self.user_metrics: Dict[str, UserBehaviorMetrics] = {}
        self.request_latencies = Histogram("request_latency")
        
        # Counters
        self.counters: Dict[str, int] = {
            "total_requests": 0,
            "total_failures": 0,
            "circuit_breaks": 0,
            "rate_limits": 0,
            "fallbacks": 0,
        }
    
    def record_event(self, event: ObservableEvent):
        """Record an observable event"""
        self.events.append(event)
        self.event_index += 1
        
        # Log to file periodically
        if len(self.events) % 100 == 0:
            self._flush_events()
        
        # Update metrics based on event type
        if event.event_type == EventType.REQUEST_COMPLETED:
            self.counters["total_requests"] += 1
            if event.duration_ms:
                self.request_latencies.observe(event.duration_ms / 1000.0)
        
        elif event.event_type == EventType.REQUEST_FAILED:
            self.counters["total_failures"] += 1
        
        elif event.event_type == EventType.CIRCUIT_BREAKER_STATE_CHANGE:
            self.counters["circuit_breaks"] += 1
        
        elif event.event_type == EventType.RATE_LIMIT_HIT:
            self.counters["rate_limits"] += 1
        
        elif event.event_type == EventType.FALLBACK_ACTIVATED:
            self.counters["fallbacks"] += 1
        
        # Update user metrics
        if event.user_id:
            self._update_user_metrics(event)
        
        # Update provider metrics
        if event.provider:
            self._update_provider_metrics(event)
    
    def _update_user_metrics(self, event: ObservableEvent):
        """Update metrics for a specific user"""
        user_id = event.user_id
        if user_id not in self.user_metrics:
            self.user_metrics[user_id] = UserBehaviorMetrics(user_id=user_id)
        
        metrics = self.user_metrics[user_id]
        
        if event.event_type == EventType.REQUEST_COMPLETED:
            metrics.total_requests += 1
            metrics.last_seen = event.timestamp
        
        if event.provider:
            metrics.total_api_calls += 1
            metrics.preferred_providers[event.provider] = \
                metrics.preferred_providers.get(event.provider, 0) + 1
            metrics.most_common_provider = max(
                metrics.preferred_providers,
                key=metrics.preferred_providers.get
            )
        
        if event.event_type == EventType.REQUEST_FAILED:
            metrics.total_failures += 1
    
    def _update_provider_metrics(self, event: ObservableEvent):
        """Update metrics for a specific provider"""
        provider = event.provider
        if provider not in self.provider_metrics:
            self.provider_metrics[provider] = ProviderMetrics(provider_name=provider)
        
        metrics = self.provider_metrics[provider]
        
        if event.event_type == EventType.API_CALL_SUCCESS:
            metrics.record_success(event.duration_ms or 0)
        elif event.event_type == EventType.API_CALL_FAILURE:
            metrics.record_failure(event.error_message or "unknown", event.duration_ms or 0)
    
    def record_api_call(
        self,
        provider: str,
        user_id: Optional[str] = None,
        request_id: Optional[str] = None,
        duration_ms: float = 0,
        success: bool = True,
        error: Optional[str] = None
    ):
        """Convenience method to record an API call"""
        event_type = EventType.API_CALL_SUCCESS if success else EventType.API_CALL_FAILURE
        event = ObservableEvent(
            event_type=event_type,
            user_id=user_id,
            request_id=request_id,
            provider=provider,
            duration_ms=duration_ms,
            status="success" if success else "failure",
            error_message=error
        )
        self.record_event(event)
    
    def _flush_events(self):
        """Write events to disk"""
        try:
            filename = self.storage_dir / f"events_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
            with open(filename, 'a') as f:
                for event in self.events[-100:]:
                    f.write(json.dumps(event.to_dict()) + '\n')
        except Exception as e:
            logger.error(f"Failed to flush events: {e}")
    
    def get_provider_rankings(self) -> List[tuple]:
        """Rank providers by performance"""
        rankings = []
        for provider_name, metrics in self.provider_metrics.items():
            score = (
                metrics.get_success_rate() * 100 -  # Success rate (0-100)
                (metrics.get_avg_latency_ms() / 1000)  # Latency penalty
            )
            rankings.append((provider_name, score, metrics))
        
        return sorted(rankings, key=lambda x: x[1], reverse=True)
    
    def get_best_provider(self, exclude: Optional[List[str]] = None) -> Optional[str]:
        """Get highest-performing provider"""
        rankings = self.get_provider_rankings()
        exclude = exclude or []
        
        for provider_name, score, metrics in rankings:
            if provider_name not in exclude and metrics.total_calls > 0:
                return provider_name
        
        return None
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get comprehensive metrics summary"""
        request_stats = self.request_latencies.get_stats()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "requests": {
                "total": self.counters["total_requests"],
                "failures": self.counters["total_failures"],
                "failure_rate": (
                    self.counters["total_failures"] / max(1, self.counters["total_requests"])
                ),
                "latency": request_stats,
            },
            "providers": {
                name: {
                    "total_calls": m.total_calls,
                    "success_rate": m.get_success_rate(),
                    "avg_latency_ms": m.get_avg_latency_ms(),
                    "errors": m.error_counts,
                }
                for name, m in self.provider_metrics.items()
            },
            "users": {
                "total": len(self.user_metrics),
                "active": len([u for u in self.user_metrics.values() if u.last_seen]),
            },
            "incidents": {
                "circuit_breaks": self.counters["circuit_breaks"],
                "rate_limits": self.counters["rate_limits"],
                "fallbacks": self.counters["fallbacks"],
            },
        }
    
    def get_status_message(self) -> str:
        """Human-readable observability status"""
        summary = self.get_metrics_summary()
        req = summary["requests"]
        
        lines = [
            "📊 **Observability Summary**",
            f"• Total requests: {req['total']} | Failures: {req['failures']} | Rate: {req['failure_rate']:.1%}",
            f"• Latency: p50={req['latency'].get('p50', 0):.2f}s | p95={req['latency'].get('p95', 0):.2f}s | p99={req['latency'].get('p99', 0):.2f}s",
            f"• Users: {summary['users']['total']} total | {summary['users']['active']} active",
            f"• Incidents: {summary['incidents']['circuit_breaks']} circuit breaks | {summary['incidents']['rate_limits']} rate limits | {summary['incidents']['fallbacks']} fallbacks",
        ]
        
        if self.provider_metrics:
            lines.append("\n📈 **Provider Performance**")
            for provider_name, score, metrics in self.get_provider_rankings()[:3]:
                lines.append(
                    f"  • {provider_name}: {metrics.get_success_rate():.1%} success | "
                    f"{metrics.get_avg_latency_ms():.0f}ms avg latency"
                )
        
        return "\n".join(lines)


# Global observability instance
observability = ObservabilitySystem()


if __name__ == "__main__":
    # Test the observability system
    obs = ObservabilitySystem()
    
    # Simulate some events
    for i in range(20):
        obs.record_api_call(
            provider="cerebras" if i % 2 == 0 else "groq",
            user_id=f"user_{i % 3}",
            request_id=f"req_{i}",
            duration_ms=100 + i * 10,
            success=i % 5 != 0  # 20% failure rate
        )
    
    print(obs.get_status_message())
    print("\n" + json.dumps(obs.get_metrics_summary(), indent=2, default=str))
