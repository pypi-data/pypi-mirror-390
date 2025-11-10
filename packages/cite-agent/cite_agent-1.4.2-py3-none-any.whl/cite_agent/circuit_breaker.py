"""
Circuit Breaker Pattern Implementation
Detects failures, fails fast, auto-recovers gracefully
"""

import time
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional, Callable, Any, Dict
import logging

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """States of the circuit breaker"""
    CLOSED = "closed"          # Normal: requests pass through
    OPEN = "open"              # Failing: requests fail immediately (fast-fail)
    HALF_OPEN = "half_open"    # Testing: one request allowed to test recovery


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker behavior"""
    failure_threshold: float = 0.5        # % of requests that must fail to open
    min_requests_for_decision: int = 10   # min requests before making decision
    open_timeout: float = 30.0            # seconds before attempting recovery
    half_open_max_calls: int = 3          # max calls in half-open state before decision
    excluded_exceptions: tuple = ()       # exceptions that don't trigger circuit break


class CircuitBreakerMetrics:
    """Tracks circuit breaker health"""
    def __init__(self):
        self.total_calls = 0
        self.total_failures = 0
        self.total_successes = 0
        self.consecutive_failures = 0
        self.state_changes: list = []  # [(state, timestamp), ...]
        self.response_times: list = []  # Last N response times
        self.last_failure_message: Optional[str] = None
    
    def get_failure_rate(self) -> float:
        """Get recent failure rate (0.0 to 1.0)"""
        if self.total_calls == 0:
            return 0.0
        return self.total_failures / self.total_calls
    
    def get_avg_response_time(self) -> float:
        """Get average response time in seconds"""
        if not self.response_times:
            return 0.0
        return sum(self.response_times[-50:]) / len(self.response_times[-50:])
    
    def reset(self):
        """Reset metrics for new cycle"""
        self.total_calls = 0
        self.total_failures = 0
        self.total_successes = 0
        self.consecutive_failures = 0
        self.response_times = []


class CircuitBreaker:
    """
    Circuit breaker for preventing cascading failures
    
    States:
    1. CLOSED: Normal operation, requests pass through
    2. OPEN: Too many failures detected, requests fail immediately (fast-fail)
    3. HALF_OPEN: Testing recovery, allowing limited requests
    
    Usage:
        breaker = CircuitBreaker("backend_api", config)
        
        try:
            result = await breaker.call(api_client.query, user_id="user123")
        except CircuitBreakerOpen:
            print("Backend is unavailable, use offline mode")
    """
    
    def __init__(
        self,
        name: str,
        config: Optional[CircuitBreakerConfig] = None,
        on_state_change: Optional[Callable] = None
    ):
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self.state = CircuitState.CLOSED
        self.metrics = CircuitBreakerMetrics()
        self.last_state_change = datetime.now()
        self.on_state_change = on_state_change
        self.half_open_calls = 0
    
    async def call(
        self,
        func: Callable,
        *args,
        fallback: Optional[Callable] = None,
        **kwargs
    ) -> Any:
        """
        Execute a function with circuit breaker protection
        
        Args:
            func: Async function to call
            fallback: Optional fallback function if circuit is open
            *args, **kwargs: Arguments to pass to func
        
        Returns:
            Result from func or fallback
        
        Raises:
            CircuitBreakerOpen: If circuit is open and no fallback
        """
        # Check if we should transition states
        self._check_state_transition()
        
        if self.state == CircuitState.OPEN:
            if fallback:
                logger.warning(f"🔴 {self.name}: Circuit OPEN, using fallback")
                return await fallback(*args, **kwargs)
            else:
                logger.error(f"🔴 {self.name}: Circuit OPEN, no fallback available")
                raise CircuitBreakerOpen(f"{self.name} is temporarily unavailable")
        
        if self.state == CircuitState.HALF_OPEN:
            if self.half_open_calls >= self.config.half_open_max_calls:
                self._change_state(CircuitState.OPEN)
                raise CircuitBreakerOpen(f"{self.name} failed recovery test")
            self.half_open_calls += 1
        
        # Call the function with timing
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            self._on_success()
            response_time = time.time() - start_time
            self.metrics.response_times.append(response_time)
            return result
        
        except Exception as e:
            response_time = time.time() - start_time
            self._on_failure(str(e), response_time)
            raise
    
    def call_sync(
        self,
        func: Callable,
        *args,
        fallback: Optional[Callable] = None,
        **kwargs
    ) -> Any:
        """Synchronous version of call()"""
        self._check_state_transition()
        
        if self.state == CircuitState.OPEN:
            if fallback:
                logger.warning(f"🔴 {self.name}: Circuit OPEN, using fallback")
                return fallback(*args, **kwargs)
            else:
                raise CircuitBreakerOpen(f"{self.name} is temporarily unavailable")
        
        if self.state == CircuitState.HALF_OPEN:
            if self.half_open_calls >= self.config.half_open_max_calls:
                self._change_state(CircuitState.OPEN)
                raise CircuitBreakerOpen(f"{self.name} failed recovery test")
            self.half_open_calls += 1
        
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            self._on_success()
            response_time = time.time() - start_time
            self.metrics.response_times.append(response_time)
            return result
        
        except Exception as e:
            response_time = time.time() - start_time
            self._on_failure(str(e), response_time)
            raise
    
    def _on_success(self):
        """Record successful call"""
        self.metrics.total_calls += 1
        self.metrics.total_successes += 1
        self.metrics.consecutive_failures = 0
        
        # If in HALF_OPEN and getting successes, transition to CLOSED
        if self.state == CircuitState.HALF_OPEN:
            self._change_state(CircuitState.CLOSED)
            self.half_open_calls = 0
    
    def _on_failure(self, error_message: str, response_time: float):
        """Record failed call"""
        self.metrics.total_calls += 1
        self.metrics.total_failures += 1
        self.metrics.consecutive_failures += 1
        self.metrics.last_failure_message = error_message
        self.metrics.response_times.append(response_time)
        
        # Check if we should open the circuit
        if self.state == CircuitState.CLOSED:
            if self._should_open_circuit():
                self._change_state(CircuitState.OPEN)
                logger.error(f"🔴 {self.name}: Circuit OPEN (failure rate: {self.metrics.get_failure_rate():.1%})")
        
        elif self.state == CircuitState.HALF_OPEN:
            # Any failure in HALF_OPEN goes back to OPEN
            self._change_state(CircuitState.OPEN)
            logger.warning(f"🔴 {self.name}: Recovery failed, circuit OPEN again")
    
    def _should_open_circuit(self) -> bool:
        """Determine if circuit should open"""
        # Need minimum requests before deciding
        if self.metrics.total_calls < self.config.min_requests_for_decision:
            return False
        
        # Check failure rate
        failure_rate = self.metrics.get_failure_rate()
        return failure_rate >= self.config.failure_threshold
    
    def _check_state_transition(self):
        """Check if we should transition from OPEN to HALF_OPEN"""
        if self.state == CircuitState.OPEN:
            elapsed = (datetime.now() - self.last_state_change).total_seconds()
            if elapsed >= self.config.open_timeout:
                self._change_state(CircuitState.HALF_OPEN)
                logger.info(f"🟡 {self.name}: Circuit HALF_OPEN, testing recovery...")
    
    def _change_state(self, new_state: CircuitState):
        """Change circuit state"""
        if new_state != self.state:
            old_state = self.state
            self.state = new_state
            self.last_state_change = datetime.now()
            self.metrics.state_changes.append((new_state, self.last_state_change))
            
            # Notify callback
            if self.on_state_change:
                self.on_state_change(old_state, new_state, self.metrics)
            
            # Reset metrics for new cycle
            if new_state == CircuitState.CLOSED:
                self.metrics.reset()
            elif new_state == CircuitState.HALF_OPEN:
                self.half_open_calls = 0
    
    def reset(self):
        """Manually reset circuit to CLOSED"""
        self._change_state(CircuitState.CLOSED)
        logger.info(f"🟢 {self.name}: Circuit RESET to CLOSED")
    
    def get_status(self) -> Dict[str, Any]:
        """Get circuit breaker status"""
        return {
            "name": self.name,
            "state": self.state.value,
            "total_calls": self.metrics.total_calls,
            "total_failures": self.metrics.total_failures,
            "failure_rate": self.metrics.get_failure_rate(),
            "consecutive_failures": self.metrics.consecutive_failures,
            "avg_response_time": self.metrics.get_avg_response_time(),
            "last_failure": self.metrics.last_failure_message,
            "last_state_change": self.last_state_change.isoformat(),
        }
    
    def get_status_message(self) -> str:
        """Human-readable status"""
        status = self.get_status()
        state_emoji = {
            "closed": "🟢",
            "open": "🔴",
            "half_open": "🟡"
        }
        
        return f"""{state_emoji.get(status['state'], '⚪')} {self.name}: {status['state'].upper()}
  • Calls: {status['total_calls']} | Failures: {status['total_failures']} | Rate: {status['failure_rate']:.1%}
  • Avg latency: {status['avg_response_time']:.2f}s
  • Last issue: {status['last_failure'] or 'None'}"""


class CircuitBreakerOpen(Exception):
    """Raised when circuit breaker is open and request cannot proceed"""
    pass


class CircuitBreakerManager:
    """
    Manages multiple circuit breakers for different services
    """
    
    def __init__(self):
        self.breakers: Dict[str, CircuitBreaker] = {}
    
    def create(
        self,
        name: str,
        config: Optional[CircuitBreakerConfig] = None
    ) -> CircuitBreaker:
        """Create a new circuit breaker"""
        if name in self.breakers:
            logger.warning(f"Circuit breaker '{name}' already exists")
            return self.breakers[name]
        
        breaker = CircuitBreaker(name, config)
        self.breakers[name] = breaker
        return breaker
    
    def get(self, name: str) -> Optional[CircuitBreaker]:
        """Get an existing circuit breaker"""
        return self.breakers.get(name)
    
    def get_all_status(self) -> Dict[str, Dict]:
        """Get status of all circuit breakers"""
        return {
            name: breaker.get_status()
            for name, breaker in self.breakers.items()
        }
    
    def print_status(self):
        """Print status of all circuit breakers"""
        for name, breaker in self.breakers.items():
            print(breaker.get_status_message())


# Global instance
circuit_breakers = CircuitBreakerManager()


if __name__ == "__main__":
    import asyncio
    
    async def test_circuit_breaker():
        """Test the circuit breaker"""
        
        # Create a circuit breaker
        config = CircuitBreakerConfig(
            failure_threshold=0.5,
            min_requests_for_decision=3,
            open_timeout=5.0
        )
        breaker = CircuitBreaker("test_api", config)
        
        # Simulate failures
        async def failing_request():
            raise Exception("Backend error")
        
        async def working_request():
            return "Success"
        
        # Make requests
        print("Making requests...\n")
        
        for i in range(10):
            try:
                if i < 3:
                    await breaker.call(failing_request)
                else:
                    await breaker.call(working_request)
            except Exception as e:
                print(f"Request {i}: {type(e).__name__}: {e}")
            
            print(breaker.get_status_message())
            print()
            await asyncio.sleep(1)
    
    asyncio.run(test_circuit_breaker())
