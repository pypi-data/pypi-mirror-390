"""
Self-Healing Agent Mechanisms
Auto-recovery from common failures, learns what works
"""

import asyncio
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class FailureType(Enum):
    """Types of failures that can be detected"""
    PROVIDER_SLOW = "provider_slow"          # Provider responding slowly
    PROVIDER_DOWN = "provider_down"          # Provider completely down
    RATE_LIMIT = "rate_limit"                # Rate limit hit
    TIMEOUT = "timeout"                      # Request timeout
    DEGRADED_QUALITY = "degraded_quality"    # Responses getting worse
    MEMORY_LEAK = "memory_leak"              # Memory usage climbing
    CIRCUIT_OPEN = "circuit_open"            # Circuit breaker open


class RecoveryAction(Enum):
    """Recovery actions the agent can take"""
    SWITCH_PROVIDER = "switch_provider"      # Try different provider
    DEGRADE_MODE = "degrade_mode"            # Reduce features
    RETRY_EXPONENTIAL = "retry_exponential"  # Retry with backoff
    CLEAR_CACHE = "clear_cache"              # Clear caches
    RESTART_SESSION = "restart_session"      # Restart connection
    FALLBACK_LOCAL = "fallback_local"        # Use local data only
    ALERT_USER = "alert_user"                # Tell user about issue


@dataclass
class FailureEvent:
    """A detected failure"""
    failure_type: FailureType
    severity: float  # 0.0 to 1.0
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def __lt__(self, other):
        """For sorting by severity"""
        return self.severity < other.severity


@dataclass
class RecoveryHistory:
    """History of recovery actions taken"""
    failure_type: FailureType
    action_taken: RecoveryAction
    success: bool
    timestamp: datetime = field(default_factory=datetime.now)
    details: str = ""


class SelfHealingAgent:
    """
    Automatically detects failures and recovers gracefully
    
    Features:
    - Detects: slow providers, rate limits, degradation, circuit breaks
    - Responds: switches providers, degrades gracefully, clears caches
    - Learns: what recovery works for what failure
    - Remembers: past failures and what fixed them
    """
    
    def __init__(self):
        # Failure detection thresholds
        self.slow_threshold_ms = 5000  # >5s = slow
        self.degradation_threshold = 0.2  # >20% worse = degraded
        self.memory_threshold_mb = 500  # >500MB = leak
        
        # Failure tracking
        self.recent_failures: Dict[FailureType, List[FailureEvent]] = {
            ft: [] for ft in FailureType
        }
        
        # Recovery history (learn what works)
        self.recovery_history: List[RecoveryHistory] = []
        
        # Degradation state
        self.is_degraded = False
        self.degradation_reason: Optional[str] = None
        self.degradation_started: Optional[datetime] = None
        
        # Recovery callbacks
        self.recovery_callbacks: Dict[RecoveryAction, Callable] = {}
    
    def detect_slow_provider(
        self,
        provider: str,
        latency_ms: float,
        recent_latencies: List[float]
    ) -> bool:
        """Detect if provider is getting slow"""
        if latency_ms > self.slow_threshold_ms:
            logger.warning(f"🐢 Provider '{provider}' is slow: {latency_ms}ms")
            
            failure = FailureEvent(
                failure_type=FailureType.PROVIDER_SLOW,
                severity=min(1.0, latency_ms / 10000),  # Normalize
                context={"provider": provider, "latency_ms": latency_ms}
            )
            self.recent_failures[FailureType.PROVIDER_SLOW].append(failure)
            return True
        
        return False
    
    def detect_rate_limiting(
        self,
        provider: str,
        error_message: str
    ) -> bool:
        """Detect rate limit errors"""
        rate_limit_indicators = [
            "rate limit",
            "too many requests",
            "429",
            "quota exceeded",
            "requests per minute"
        ]
        
        if any(indicator in error_message.lower() for indicator in rate_limit_indicators):
            logger.warning(f"⚠️ Rate limit hit on provider '{provider}'")
            
            failure = FailureEvent(
                failure_type=FailureType.RATE_LIMIT,
                severity=0.7,
                context={"provider": provider, "error": error_message}
            )
            self.recent_failures[FailureType.RATE_LIMIT].append(failure)
            return True
        
        return False
    
    def detect_degradation(
        self,
        metric_name: str,
        current_value: float,
        historical_baseline: float
    ) -> bool:
        """Detect service degradation"""
        if historical_baseline == 0:
            return False
        
        degradation_rate = abs(current_value - historical_baseline) / historical_baseline
        
        if degradation_rate > self.degradation_threshold:
            logger.warning(
                f"📉 Degradation detected in '{metric_name}': "
                f"{historical_baseline} → {current_value} ({degradation_rate:.1%})"
            )
            
            failure = FailureEvent(
                failure_type=FailureType.DEGRADED_QUALITY,
                severity=min(1.0, degradation_rate),
                context={
                    "metric": metric_name,
                    "baseline": historical_baseline,
                    "current": current_value
                }
            )
            self.recent_failures[FailureType.DEGRADED_QUALITY].append(failure)
            return True
        
        return False
    
    def detect_memory_leak(self, current_memory_mb: float) -> bool:
        """Detect memory leaks"""
        if current_memory_mb > self.memory_threshold_mb:
            logger.warning(f"💾 High memory usage: {current_memory_mb}MB")
            
            failure = FailureEvent(
                failure_type=FailureType.MEMORY_LEAK,
                severity=min(1.0, current_memory_mb / 1000),
                context={"memory_mb": current_memory_mb}
            )
            self.recent_failures[FailureType.MEMORY_LEAK].append(failure)
            return True
        
        return False
    
    async def perform_recovery(
        self,
        failure: FailureEvent,
        available_providers: List[str],
        current_provider: str
    ) -> tuple[bool, Optional[str]]:
        """
        Perform recovery for a detected failure
        
        Returns:
            (success, recovery_action_taken)
        """
        # Check recovery history for this failure type
        previous_solutions = self._get_previous_solutions(failure.failure_type)
        
        if failure.failure_type == FailureType.PROVIDER_SLOW:
            # Try switching to faster provider
            better_provider = next(
                (p for p in available_providers if p != current_provider),
                None
            )
            if better_provider:
                logger.info(f"🔄 Switching provider: {current_provider} → {better_provider}")
                success = await self._execute_recovery(
                    RecoveryAction.SWITCH_PROVIDER,
                    {"new_provider": better_provider}
                )
                self._record_recovery(failure.failure_type, RecoveryAction.SWITCH_PROVIDER, success)
                return success, better_provider
        
        elif failure.failure_type == FailureType.RATE_LIMIT:
            # Wait and retry
            logger.info("⏳ Rate limited - exponential backoff")
            await asyncio.sleep(5)
            success = await self._execute_recovery(
                RecoveryAction.RETRY_EXPONENTIAL,
                {"wait_time": 5}
            )
            self._record_recovery(failure.failure_type, RecoveryAction.RETRY_EXPONENTIAL, success)
            return success, None
        
        elif failure.failure_type == FailureType.DEGRADED_QUALITY:
            # Clear cache and retry
            logger.info("🧹 Clearing cache to recover quality")
            success = await self._execute_recovery(
                RecoveryAction.CLEAR_CACHE,
                {}
            )
            self._record_recovery(failure.failure_type, RecoveryAction.CLEAR_CACHE, success)
            return success, None
        
        elif failure.failure_type == FailureType.MEMORY_LEAK:
            # Enter degradation mode
            logger.warning("📉 Entering degraded mode to manage memory")
            self._enter_degraded_mode("High memory usage")
            success = await self._execute_recovery(
                RecoveryAction.DEGRADE_MODE,
                {"reason": "memory"}
            )
            return success, None
        
        elif failure.failure_type == FailureType.CIRCUIT_OPEN:
            # Wait for circuit to recover
            logger.info("🔌 Circuit open - using fallback mode")
            success = await self._execute_recovery(
                RecoveryAction.FALLBACK_LOCAL,
                {}
            )
            return success, None
        
        # No recovery action found
        return False, None
    
    def _enter_degraded_mode(self, reason: str):
        """Enter degraded mode with reduced features"""
        self.is_degraded = True
        self.degradation_reason = reason
        self.degradation_started = datetime.now()
        logger.warning(f"⚠️ DEGRADED MODE: {reason}")
    
    def _exit_degraded_mode(self):
        """Exit degraded mode"""
        if self.degradation_started:
            duration = (datetime.now() - self.degradation_started).total_seconds()
            logger.info(f"🟢 Exiting degraded mode (lasted {duration:.0f}s)")
        
        self.is_degraded = False
        self.degradation_reason = None
        self.degradation_started = None
    
    async def _execute_recovery(
        self,
        action: RecoveryAction,
        params: Dict[str, Any]
    ) -> bool:
        """Execute a recovery action"""
        if action in self.recovery_callbacks:
            try:
                result = await self.recovery_callbacks[action](**params)
                return result
            except Exception as e:
                logger.error(f"❌ Recovery action failed: {e}")
                return False
        
        # Default implementations
        if action == RecoveryAction.SWITCH_PROVIDER:
            return True  # Caller handles
        elif action == RecoveryAction.RETRY_EXPONENTIAL:
            return True  # Already waited
        elif action == RecoveryAction.CLEAR_CACHE:
            return True  # No-op if no cache
        elif action == RecoveryAction.DEGRADE_MODE:
            return True  # Mode entered
        elif action == RecoveryAction.FALLBACK_LOCAL:
            return True  # Caller handles
        
        return False
    
    def _get_previous_solutions(self, failure_type: FailureType) -> List[RecoveryAction]:
        """Get previous recovery actions that worked for this failure type"""
        successes = [
            entry.action_taken
            for entry in self.recovery_history
            if entry.failure_type == failure_type and entry.success
        ]
        
        # Return most recent successes first
        from collections import Counter
        counts = Counter(successes)
        return [action for action, _ in counts.most_common()]
    
    def _record_recovery(
        self,
        failure_type: FailureType,
        action: RecoveryAction,
        success: bool
    ):
        """Record recovery action for learning"""
        entry = RecoveryHistory(
            failure_type=failure_type,
            action_taken=action,
            success=success,
            details=""
        )
        self.recovery_history.append(entry)
        
        if success:
            logger.info(f"✅ Recovery succeeded: {action.value}")
        else:
            logger.warning(f"❌ Recovery failed: {action.value}")
    
    def _cleanup_old_failures(self):
        """Remove old failure records (keep last hour)"""
        cutoff = datetime.now() - timedelta(hours=1)
        
        for failure_type in self.recent_failures:
            self.recent_failures[failure_type] = [
                f for f in self.recent_failures[failure_type]
                if f.timestamp > cutoff
            ]
    
    def get_failure_summary(self) -> Dict[str, int]:
        """Get summary of recent failures"""
        self._cleanup_old_failures()
        
        return {
            failure_type.value: len(failures)
            for failure_type, failures in self.recent_failures.items()
            if failures
        }
    
    def get_recovery_effectiveness(self) -> Dict[str, float]:
        """Get success rate of different recovery actions"""
        if not self.recovery_history:
            return {}
        
        action_results: Dict[RecoveryAction, tuple[int, int]] = {}  # (successes, total)
        
        for entry in self.recovery_history:
            if entry.action_taken not in action_results:
                action_results[entry.action_taken] = (0, 0)
            
            successes, total = action_results[entry.action_taken]
            total += 1
            if entry.success:
                successes += 1
            action_results[entry.action_taken] = (successes, total)
        
        return {
            action.value: successes / total
            for action, (successes, total) in action_results.items()
        }
    
    def get_status_message(self) -> str:
        """Human-readable status"""
        lines = ["🏥 **Self-Healing Status**"]
        
        if self.is_degraded:
            lines.append(f"⚠️ DEGRADED MODE: {self.degradation_reason}")
        else:
            lines.append("🟢 Normal operation")
        
        failures = self.get_failure_summary()
        if failures:
            lines.append("\n📊 **Recent Failures**")
            for failure_type, count in sorted(failures.items(), key=lambda x: x[1], reverse=True):
                lines.append(f"  • {failure_type}: {count}")
        
        effectiveness = self.get_recovery_effectiveness()
        if effectiveness:
            lines.append("\n✅ **Recovery Effectiveness**")
            for action, rate in sorted(effectiveness.items(), key=lambda x: x[1], reverse=True):
                lines.append(f"  • {action}: {rate:.1%} success rate")
        
        return "\n".join(lines)


# Global instance
self_healing_agent = SelfHealingAgent()


if __name__ == "__main__":
    agent = SelfHealingAgent()
    
    # Simulate some failures
    agent.detect_slow_provider("cerebras", 6000, [100, 200, 300])
    agent.detect_rate_limiting("groq", "429 Too Many Requests")
    agent.detect_degradation("accuracy", 0.75, 0.95)
    
    print(agent.get_status_message())
