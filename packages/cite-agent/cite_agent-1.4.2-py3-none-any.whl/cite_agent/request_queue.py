"""
Intelligent Request Queue with Backpressure
Prioritizes requests, prevents thundering herd, gracefully degrades under load
"""

import asyncio
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Callable
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class RequestPriority(Enum):
    """Request priority levels"""
    URGENT = 0      # User initiated, blocking
    NORMAL = 1      # Standard requests
    BATCH = 2       # Background/analysis
    MAINTENANCE = 3 # Cleanup, archival


@dataclass
class QueuedRequest:
    """A request waiting in queue"""
    request_id: str
    user_id: str
    priority: RequestPriority
    submitted_at: datetime
    max_wait_time: float  # seconds
    callback: Callable
    args: tuple = field(default_factory=tuple)
    kwargs: dict = field(default_factory=dict)
    
    def is_expired(self) -> bool:
        """Check if request exceeded max wait time"""
        elapsed = (datetime.now() - self.submitted_at).total_seconds()
        return elapsed > self.max_wait_time


class CircuitStatus(Enum):
    """Circuit breaker status"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject fast
    HALF_OPEN = "half_open"  # Testing recovery


@dataclass
class RequestQueueMetrics:
    """Metrics about queue health"""
    queue_depth: int
    total_queued: int
    total_processed: int
    total_expired: int
    avg_wait_time: float
    p95_wait_time: float
    circuit_status: CircuitStatus
    active_requests: int
    max_concurrent: int


class IntelligentRequestQueue:
    """
    Priority queue with backpressure, circuit breaker integration, and metrics
    
    Features:
    - Priority levels (urgent > normal > batch > maintenance)
    - Per-user concurrency limits
    - Queue depth monitoring
    - Automatic circuit breaker integration
    - Request expiration (don't serve stale requests)
    - User notifications about wait time
    - Graceful degradation under load
    """
    
    def __init__(
        self,
        max_concurrent_global: int = 50,
        max_concurrent_per_user: int = 3,
        queue_size_limit: int = 1000,
        warning_threshold: float = 0.7,  # warn when queue at 70%
        rejection_threshold: float = 0.95  # reject when queue at 95%
    ):
        self.max_concurrent_global = max_concurrent_global
        self.max_concurrent_per_user = max_concurrent_per_user
        self.queue_size_limit = queue_size_limit
        self.warning_threshold = warning_threshold
        self.rejection_threshold = rejection_threshold
        
        # Queues by priority
        self.queues: Dict[RequestPriority, asyncio.Queue] = {
            priority: asyncio.Queue(maxsize=queue_size_limit)
            for priority in RequestPriority
        }
        
        # Active requests tracking
        self.active_requests: Dict[str, datetime] = {}  # request_id -> start_time
        self.user_active: Dict[str, int] = {}  # user_id -> count
        
        # Metrics
        self.total_processed = 0
        self.total_queued = 0
        self.total_expired = 0
        self.wait_times: List[float] = []  # for p95 calculation
        
        # Circuit breaker state
        self.circuit_status = CircuitStatus.CLOSED
        self.circuit_open_at: Optional[datetime] = None
        self.circuit_recovery_timeout = 30  # seconds
        
        # Background worker
        self.worker_task: Optional[asyncio.Task] = None
        self.is_running = False
    
    async def start(self):
        """Start the queue worker"""
        if self.is_running:
            return
        
        self.is_running = True
        self.worker_task = asyncio.create_task(self._process_queue())
        logger.info("🚀 Request queue started")
    
    async def stop(self):
        """Stop the queue worker"""
        self.is_running = False
        if self.worker_task:
            await self.worker_task
        logger.info("⛔ Request queue stopped")
    
    async def submit(
        self,
        user_id: str,
        callback: Callable,
        priority: RequestPriority = RequestPriority.NORMAL,
        max_wait_time: float = 30.0,
        request_id: Optional[str] = None,
        *args,
        **kwargs
    ) -> tuple[bool, Optional[str]]:
        """
        Submit a request to the queue
        
        Returns:
            (success, error_message)
        """
        if request_id is None:
            request_id = f"{user_id}_{time.time()}"
        
        # Check queue capacity
        queue_usage = self._get_queue_usage()
        
        if queue_usage > self.rejection_threshold:
            return False, f"System overloaded (queue at {queue_usage*100:.0f}%). Please try again in 30 seconds."
        
        if queue_usage > self.warning_threshold:
            warning = f"⚠️ System busy. Your request may take up to {max_wait_time:.0f}s."
        else:
            warning = None
        
        # Check circuit breaker
        if self.circuit_status == CircuitStatus.OPEN:
            if self._should_attempt_recovery():
                self.circuit_status = CircuitStatus.HALF_OPEN
                logger.info("🔄 Circuit breaker: attempting recovery")
            else:
                return False, "System is temporarily unavailable. Retrying in 30s..."
        
        # Create queued request
        request = QueuedRequest(
            request_id=request_id,
            user_id=user_id,
            priority=priority,
            submitted_at=datetime.now(),
            max_wait_time=max_wait_time,
            callback=callback,
            args=args,
            kwargs=kwargs
        )
        
        # Add to appropriate priority queue
        try:
            self.queues[priority].put_nowait(request)
            self.total_queued += 1
            
            message = f"✓ Queued (position #{self._get_queue_depth()})"
            if warning:
                message += f"\n{warning}"
            
            return True, message
        
        except asyncio.QueueFull:
            return False, "Queue is full. Please try again soon."
    
    async def _process_queue(self):
        """Main worker: continuously process queued requests"""
        while self.is_running:
            try:
                # Check if we can process more requests
                if len(self.active_requests) >= self.max_concurrent_global:
                    await asyncio.sleep(0.1)
                    continue
                
                # Get next request from highest priority queue
                request = await self._get_next_request()
                if request is None:
                    await asyncio.sleep(0.1)
                    continue
                
                # Check expiration
                if request.is_expired():
                    self.total_expired += 1
                    logger.warning(f"⏰ Request {request.request_id} expired (waited too long)")
                    continue
                
                # Check user concurrency limit
                user_count = self.user_active.get(request.user_id, 0)
                if user_count >= self.max_concurrent_per_user:
                    # Re-queue this request with same priority
                    await self.queues[request.priority].put(request)
                    await asyncio.sleep(0.5)
                    continue
                
                # Execute the request
                await self._execute_request(request)
            
            except Exception as e:
                logger.error(f"❌ Queue worker error: {e}", exc_info=True)
                await asyncio.sleep(1)
    
    async def _get_next_request(self) -> Optional[QueuedRequest]:
        """Get highest priority non-empty request"""
        # Try each priority level in order
        for priority in RequestPriority:
            try:
                return self.queues[priority].get_nowait()
            except asyncio.QueueEmpty:
                continue
        
        return None
    
    async def _execute_request(self, request: QueuedRequest):
        """Execute a request and track metrics"""
        request_id = request.request_id
        start_time = datetime.now()
        
        try:
            # Track active request
            self.active_requests[request_id] = start_time
            self.user_active[request.user_id] = self.user_active.get(request.user_id, 0) + 1
            
            wait_time = (start_time - request.submitted_at).total_seconds()
            self.wait_times.append(wait_time)
            
            logger.debug(f"▶️ Executing {request_id} (waited {wait_time:.1f}s)")
            
            # Call the callback
            result = await request.callback(*request.args, **request.kwargs)
            
            # Record success
            self.total_processed += 1
            
            # Update circuit breaker
            if self.circuit_status == CircuitStatus.HALF_OPEN:
                self.circuit_status = CircuitStatus.CLOSED
                logger.info("🟢 Circuit breaker: recovered")
            
            return result
        
        except Exception as e:
            logger.error(f"❌ Request {request_id} failed: {e}")
            
            # Update circuit breaker on failure
            self._on_request_failure()
            
            raise
        
        finally:
            # Clean up tracking
            self.active_requests.pop(request_id, None)
            self.user_active[request.user_id] -= 1
            
            elapsed = (datetime.now() - start_time).total_seconds()
            logger.debug(f"✓ Request {request_id} completed in {elapsed:.2f}s")
    
    def _on_request_failure(self):
        """Called when a request fails - updates circuit breaker"""
        # Track failure rate
        if len(self.active_requests) > 0:
            failure_rate = self.total_queued / max(1, self.total_processed + 1)
            
            # Open circuit if failure rate high
            if failure_rate > 0.3:  # >30% failure rate
                if self.circuit_status != CircuitStatus.OPEN:
                    logger.error(f"🔴 Circuit breaker: OPEN (failure rate {failure_rate:.1%})")
                    self.circuit_status = CircuitStatus.OPEN
                    self.circuit_open_at = datetime.now()
    
    def _should_attempt_recovery(self) -> bool:
        """Check if circuit breaker should attempt recovery"""
        if not self.circuit_open_at:
            return True
        
        elapsed = (datetime.now() - self.circuit_open_at).total_seconds()
        return elapsed > self.circuit_recovery_timeout
    
    def _get_queue_usage(self) -> float:
        """Get current queue usage as percentage (0.0 to 1.0)"""
        total_queued = sum(q.qsize() for q in self.queues.values())
        return min(1.0, total_queued / self.queue_size_limit)
    
    def _get_queue_depth(self) -> int:
        """Get total requests in queue"""
        return sum(q.qsize() for q in self.queues.values())
    
    def get_metrics(self) -> RequestQueueMetrics:
        """Get current queue metrics"""
        queue_depth = self._get_queue_depth()
        wait_times_sorted = sorted(self.wait_times[-100:])  # Last 100 requests
        
        p95_wait = wait_times_sorted[int(len(wait_times_sorted) * 0.95)] if wait_times_sorted else 0
        avg_wait = sum(self.wait_times) / len(self.wait_times) if self.wait_times else 0
        
        return RequestQueueMetrics(
            queue_depth=queue_depth,
            total_queued=self.total_queued,
            total_processed=self.total_processed,
            total_expired=self.total_expired,
            avg_wait_time=avg_wait,
            p95_wait_time=p95_wait,
            circuit_status=self.circuit_status,
            active_requests=len(self.active_requests),
            max_concurrent=self.max_concurrent_global
        )
    
    def get_status_message(self) -> str:
        """Human-readable queue status"""
        metrics = self.get_metrics()
        usage = self._get_queue_usage()
        
        lines = [
            "📊 **Request Queue Status**",
            f"• Queue depth: {metrics.queue_depth}/{self.queue_size_limit} ({usage*100:.0f}%)",
            f"• Active requests: {metrics.active_requests}/{metrics.max_concurrent}",
            f"• Processed: {metrics.total_processed} | Queued: {metrics.total_queued} | Expired: {metrics.total_expired}",
            f"• Avg wait: {metrics.avg_wait_time:.1f}s | P95 wait: {metrics.p95_wait_time:.1f}s",
            f"• Circuit breaker: {metrics.circuit_status.value.upper()}",
        ]
        
        return "\n".join(lines)


# Example usage
async def example():
    """Example of using the queue"""
    queue = IntelligentRequestQueue(
        max_concurrent_global=10,
        max_concurrent_per_user=2
    )
    
    await queue.start()
    
    # Simulate a callback
    async def process_query(query: str) -> str:
        await asyncio.sleep(1)  # Simulate work
        return f"Result for: {query}"
    
    # Submit requests
    for i in range(5):
        success, msg = await queue.submit(
            user_id="user1",
            callback=process_query,
            priority=RequestPriority.NORMAL,
            args=(f"query_{i}",)
        )
        print(f"Request {i}: {msg}")
    
    # Wait a bit
    await asyncio.sleep(10)
    
    # Check status
    print(queue.get_status_message())
    
    await queue.stop()


if __name__ == "__main__":
    asyncio.run(example())
