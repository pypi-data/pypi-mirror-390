"""
x402 Infrastructure Accelerators

Advanced infrastructure components to accelerate x402 development.
Built for Hackathon Category 4: SDKs & Infrastructure ($10k prize)
"""

import asyncio
import json
import time
import hashlib
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum
import logging
import sqlite3

import httpx

# Optional Redis support - handle compatibility issues with Python 3.12
REDIS_AVAILABLE = False
aioredis = None

try:
    # Try new redis package (redis>=4.2.0) - Python 3.12 compatible
    import redis.asyncio as aioredis
    REDIS_AVAILABLE = True
except ImportError:
    # Redis not available, will use local cache only
    pass

logger = logging.getLogger(__name__)


class PaymentRouter:
    """
    Intelligent payment routing across multiple providers and chains
    
    Automatically selects the best payment path based on:
    - Network fees
    - Confirmation times  
    - Success rates
    - User preferences
    """
    
    def __init__(self):
        self.routes: Dict[str, Dict] = {}
        self.metrics: Dict[str, Dict] = {}
        self._init_routes()
    
    def _init_routes(self):
        """Initialize available payment routes"""
        self.routes = {
            "solana_native": {
                "chain": "solana",
                "facilitator": None,
                "avg_fee": 0.00025,
                "avg_confirmation_ms": 400,
                "success_rate": 0.99
            },
            "solana_cdp": {
                "chain": "solana",
                "facilitator": "cdp",
                "avg_fee": 0,  # CDP covers fees
                "avg_confirmation_ms": 600,
                "success_rate": 0.995
            },
            "base_cdp": {
                "chain": "base",
                "facilitator": "cdp",
                "avg_fee": 0,
                "avg_confirmation_ms": 2000,
                "success_rate": 0.99
            },
            "ethereum_cdp": {
                "chain": "ethereum",
                "facilitator": "cdp",
                "avg_fee": 0,
                "avg_confirmation_ms": 15000,
                "success_rate": 0.98
            }
        }
    
    def select_best_route(
        self,
        requirements: Dict[str, Any],
        preferences: Optional[Dict] = None
    ) -> str:
        """
        Select the best payment route
        
        Args:
            requirements: Payment requirements from server
            preferences: User preferences (speed, cost, chain)
        
        Returns:
            Best route identifier
        """
        network = requirements.get("network", "solana")
        amount = requirements.get("amount", 0)
        
        # Filter compatible routes
        compatible = []
        for route_id, route in self.routes.items():
            if network in route_id or network == route["chain"]:
                compatible.append((route_id, route))
        
        if not compatible:
            return "solana_native"  # Default fallback
        
        # Score routes
        best_route = None
        best_score = -1
        
        for route_id, route in compatible:
            score = self._score_route(route, preferences)
            if score > best_score:
                best_score = score
                best_route = route_id
        
        logger.info(f"Selected route: {best_route} (score: {best_score:.2f})")
        return best_route
    
    def _score_route(self, route: Dict, preferences: Optional[Dict]) -> float:
        """Score a route based on preferences"""
        score = 100.0
        
        # Success rate is most important
        score *= route["success_rate"]
        
        # Speed preference
        if preferences and preferences.get("priority") == "speed":
            if route["avg_confirmation_ms"] < 1000:
                score *= 1.2
            elif route["avg_confirmation_ms"] > 10000:
                score *= 0.8
        
        # Cost preference
        if preferences and preferences.get("priority") == "cost":
            if route["avg_fee"] == 0:
                score *= 1.3
            elif route["avg_fee"] > 0.001:
                score *= 0.9
        
        return score
    
    def record_outcome(self, route_id: str, success: bool, duration_ms: int):
        """Record route performance for learning"""
        if route_id not in self.metrics:
            self.metrics[route_id] = {
                "attempts": 0,
                "successes": 0,
                "total_duration": 0
            }
        
        self.metrics[route_id]["attempts"] += 1
        if success:
            self.metrics[route_id]["successes"] += 1
        self.metrics[route_id]["total_duration"] += duration_ms
        
        # Update route success rate
        if self.metrics[route_id]["attempts"] > 10:
            self.routes[route_id]["success_rate"] = (
                self.metrics[route_id]["successes"] / 
                self.metrics[route_id]["attempts"]
            )


class PaymentCache:
    """
    High-performance caching layer for x402 payments
    
    Reduces latency and costs by caching:
    - Payment requirements
    - Verification results
    - Resource data
    """
    
    def __init__(self, redis_url: Optional[str] = None):
        self.redis_url = redis_url
        self.redis = None
        self.local_cache: Dict[str, Dict] = {}
        
    async def connect(self):
        """Connect to Redis if available"""
        if self.redis_url:
            try:
                self.redis = await aioredis.create_redis_pool(self.redis_url)
                logger.info("Connected to Redis cache")
            except:
                logger.warning("Redis unavailable, using local cache")
    
    async def get_requirements(self, url: str) -> Optional[Dict]:
        """Get cached payment requirements"""
        cache_key = f"req:{hashlib.md5(url.encode()).hexdigest()}"
        
        # Try Redis first
        if self.redis:
            try:
                data = await self.redis.get(cache_key)
                if data:
                    return json.loads(data)
            except:
                pass
        
        # Fallback to local cache
        if cache_key in self.local_cache:
            entry = self.local_cache[cache_key]
            if entry["expires"] > time.time():
                return entry["data"]
        
        return None
    
    async def set_requirements(self, url: str, requirements: Dict, ttl: int = 300):
        """Cache payment requirements"""
        cache_key = f"req:{hashlib.md5(url.encode()).hexdigest()}"
        
        # Store in Redis
        if self.redis:
            try:
                await self.redis.setex(
                    cache_key,
                    ttl,
                    json.dumps(requirements)
                )
            except:
                pass
        
        # Store in local cache
        self.local_cache[cache_key] = {
            "data": requirements,
            "expires": time.time() + ttl
        }
    
    async def get_receipt(self, signature: str) -> Optional[Dict]:
        """Get cached payment receipt"""
        cache_key = f"receipt:{signature}"
        
        if self.redis:
            try:
                data = await self.redis.get(cache_key)
                if data:
                    return json.loads(data)
            except:
                pass
        
        if cache_key in self.local_cache:
            return self.local_cache[cache_key]["data"]
        
        return None
    
    async def set_receipt(self, signature: str, receipt: Dict):
        """Cache payment receipt (permanent)"""
        cache_key = f"receipt:{signature}"
        
        if self.redis:
            try:
                await self.redis.set(cache_key, json.dumps(receipt))
            except:
                pass
        
        self.local_cache[cache_key] = {
            "data": receipt,
            "expires": float('inf')  # Never expires
        }


class PaymentPool:
    """
    Connection pooling for x402 clients
    
    Manages a pool of payment clients for high-throughput applications
    """
    
    def __init__(self, size: int = 10):
        self.size = size
        self.clients: List[Any] = []
        self.available: asyncio.Queue = asyncio.Queue()
        self.stats = {
            "total_requests": 0,
            "active_connections": 0,
            "pool_exhausted_count": 0
        }
    
    async def initialize(self, client_factory: Callable):
        """Initialize the connection pool"""
        for _ in range(self.size):
            client = await client_factory()
            self.clients.append(client)
            await self.available.put(client)
        
        logger.info(f"Initialized payment pool with {self.size} clients")
    
    async def acquire(self, timeout: float = 5.0) -> Any:
        """Acquire a client from the pool"""
        try:
            client = await asyncio.wait_for(
                self.available.get(),
                timeout=timeout
            )
            self.stats["active_connections"] += 1
            self.stats["total_requests"] += 1
            return client
        except asyncio.TimeoutError:
            self.stats["pool_exhausted_count"] += 1
            raise Exception("Payment pool exhausted")
    
    async def release(self, client: Any):
        """Return a client to the pool"""
        self.stats["active_connections"] -= 1
        await self.available.put(client)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get pool statistics"""
        return {
            **self.stats,
            "available": self.available.qsize(),
            "utilization": (self.stats["active_connections"] / self.size) * 100
        }


class BatchProcessor:
    """
    Batch payment processing for efficiency
    
    Groups multiple small payments into batches for:
    - Reduced transaction fees
    - Better throughput
    - Atomic processing
    """
    
    def __init__(self, batch_size: int = 10, batch_timeout: float = 1.0):
        self.batch_size = batch_size
        self.batch_timeout = batch_timeout
        self.pending: List[Dict] = []
        self.lock = asyncio.Lock()
    
    async def add_payment(
        self,
        recipient: str,
        amount: float,
        callback: Callable
    ) -> None:
        """Add a payment to the batch"""
        async with self.lock:
            self.pending.append({
                "recipient": recipient,
                "amount": amount,
                "callback": callback,
                "added_at": time.time()
            })
            
            # Process if batch is full
            if len(self.pending) >= self.batch_size:
                await self._process_batch()
    
    async def _process_batch(self):
        """Process all pending payments as a batch"""
        if not self.pending:
            return
        
        batch = self.pending.copy()
        self.pending.clear()
        
        logger.info(f"Processing batch of {len(batch)} payments")
        
        # In production, this would create a single transaction
        # with multiple transfer instructions
        
        # For now, simulate batch processing
        for payment in batch:
            try:
                # Simulate payment
                result = {"success": True, "signature": f"batch_{time.time()}"}
                await payment["callback"](result)
            except Exception as e:
                logger.error(f"Batch payment failed: {e}")
                await payment["callback"]({"success": False, "error": str(e)})
    
    async def start_background_processor(self):
        """Start background batch processor"""
        while True:
            await asyncio.sleep(self.batch_timeout)
            async with self.lock:
                if self.pending:
                    # Check if any payments are old enough
                    oldest = min(p["added_at"] for p in self.pending)
                    if time.time() - oldest >= self.batch_timeout:
                        await self._process_batch()


class MetricsCollector:
    """
    Comprehensive metrics collection for x402 payments
    """
    
    def __init__(self, db_path: str = "x402_metrics.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize metrics database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS payment_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp INTEGER NOT NULL,
                url TEXT NOT NULL,
                amount REAL NOT NULL,
                network TEXT NOT NULL,
                success BOOLEAN NOT NULL,
                duration_ms INTEGER,
                error TEXT
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_timestamp 
            ON payment_metrics(timestamp)
        """)
        
        conn.commit()
        conn.close()
    
    def record_payment(
        self,
        url: str,
        amount: float,
        network: str,
        success: bool,
        duration_ms: int,
        error: Optional[str] = None
    ):
        """Record a payment metric"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO payment_metrics
            (timestamp, url, amount, network, success, duration_ms, error)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            int(time.time()),
            url,
            amount,
            network,
            success,
            duration_ms,
            error
        ))
        
        conn.commit()
        conn.close()
    
    def get_statistics(
        self,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get payment statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Build query
        query = "SELECT * FROM payment_metrics WHERE 1=1"
        params = []
        
        if start_time:
            query += " AND timestamp >= ?"
            params.append(start_time)
        
        if end_time:
            query += " AND timestamp <= ?"
            params.append(end_time)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        # Calculate statistics
        total_payments = len(rows)
        successful = sum(1 for r in rows if r[5])  # success column
        total_volume = sum(r[3] for r in rows)  # amount column
        avg_duration = sum(r[6] or 0 for r in rows) / len(rows) if rows else 0
        
        # Network breakdown
        network_stats = {}
        for row in rows:
            network = row[4]
            if network not in network_stats:
                network_stats[network] = {"count": 0, "volume": 0}
            network_stats[network]["count"] += 1
            network_stats[network]["volume"] += row[3]
        
        conn.close()
        
        return {
            "total_payments": total_payments,
            "successful_payments": successful,
            "success_rate": (successful / total_payments * 100) if total_payments else 0,
            "total_volume_usdc": total_volume,
            "average_duration_ms": avg_duration,
            "network_breakdown": network_stats
        }


class WebhookManager:
    """
    Webhook management for payment events
    
    Notify external systems about payment events
    """
    
    def __init__(self):
        self.webhooks: Dict[str, List[str]] = {}
        self.retry_queue: List[Dict] = []
    
    def register_webhook(self, event_type: str, url: str):
        """Register a webhook for an event type"""
        if event_type not in self.webhooks:
            self.webhooks[event_type] = []
        self.webhooks[event_type].append(url)
        logger.info(f"Registered webhook for {event_type}: {url}")
    
    async def trigger(
        self,
        event_type: str,
        data: Dict[str, Any],
        retry_on_failure: bool = True
    ):
        """Trigger webhooks for an event"""
        if event_type not in self.webhooks:
            return
        
        for webhook_url in self.webhooks[event_type]:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        webhook_url,
                        json={
                            "event": event_type,
                            "timestamp": int(time.time()),
                            "data": data
                        },
                        timeout=5.0
                    )
                    
                    if response.status_code != 200 and retry_on_failure:
                        self.retry_queue.append({
                            "url": webhook_url,
                            "event": event_type,
                            "data": data,
                            "attempts": 1
                        })
                    
            except Exception as e:
                logger.error(f"Webhook failed: {webhook_url} - {e}")
                if retry_on_failure:
                    self.retry_queue.append({
                        "url": webhook_url,
                        "event": event_type,
                        "data": data,
                        "attempts": 1
                    })
    
    async def process_retry_queue(self):
        """Process failed webhooks"""
        while self.retry_queue:
            item = self.retry_queue.pop(0)
            
            if item["attempts"] >= 3:
                logger.error(f"Webhook permanently failed: {item['url']}")
                continue
            
            try:
                async with httpx.AsyncClient() as client:
                    await client.post(
                        item["url"],
                        json={
                            "event": item["event"],
                            "data": item["data"],
                            "retry": True
                        }
                    )
            except:
                item["attempts"] += 1
                self.retry_queue.append(item)


class RateLimiter:
    """
    Rate limiting for x402 endpoints
    
    Prevent abuse and ensure fair usage
    """
    
    def __init__(
        self,
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000
    ):
        self.rpm_limit = requests_per_minute
        self.rph_limit = requests_per_hour
        self.requests: Dict[str, List[int]] = {}
    
    def is_allowed(self, client_id: str) -> bool:
        """Check if client is within rate limits"""
        now = int(time.time())
        
        if client_id not in self.requests:
            self.requests[client_id] = []
        
        # Clean old requests
        self.requests[client_id] = [
            ts for ts in self.requests[client_id]
            if now - ts < 3600  # Keep last hour
        ]
        
        # Check per-minute limit
        recent_minute = [
            ts for ts in self.requests[client_id]
            if now - ts < 60
        ]
        if len(recent_minute) >= self.rpm_limit:
            return False
        
        # Check per-hour limit
        if len(self.requests[client_id]) >= self.rph_limit:
            return False
        
        # Record request
        self.requests[client_id].append(now)
        return True
    
    def get_limits_for_client(self, client_id: str) -> Dict[str, int]:
        """Get current limits for a client"""
        now = int(time.time())
        
        if client_id not in self.requests:
            return {
                "requests_last_minute": 0,
                "requests_last_hour": 0,
                "remaining_rpm": self.rpm_limit,
                "remaining_rph": self.rph_limit
            }
        
        recent_minute = len([
            ts for ts in self.requests[client_id]
            if now - ts < 60
        ])
        
        recent_hour = len([
            ts for ts in self.requests[client_id]
            if now - ts < 3600
        ])
        
        return {
            "requests_last_minute": recent_minute,
            "requests_last_hour": recent_hour,
            "remaining_rpm": max(0, self.rpm_limit - recent_minute),
            "remaining_rph": max(0, self.rph_limit - recent_hour)
        }