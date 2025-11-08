"""
x402 Payment Agent for Solana

Autonomous agents that can make payments with budget management.
"""

import asyncio
import logging
import time
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from solders.keypair import Keypair

from .client import X402Client
from .types import Network

logger = logging.getLogger(__name__)


@dataclass
class TransactionRecord:
    """Record of a payment transaction"""
    signature: str
    timestamp: int
    amount_usdc: float
    url: str
    success: bool
    error: Optional[str] = None


@dataclass
class BudgetManager:
    """
    Budget manager for autonomous agents
    
    Prevents overspending with configurable limits.
    """
    max_per_request: float = 1.0  # Max USDC per request
    max_per_hour: float = 10.0    # Max USDC per hour
    max_per_day: float = 100.0    # Max USDC per day
    transactions: List[TransactionRecord] = field(default_factory=list)
    
    def can_spend(self, amount: float) -> tuple[bool, str]:
        """
        Check if agent can spend amount
        
        Returns:
            (can_spend, reason_if_not)
        """
        # Check per-request limit
        if amount > self.max_per_request:
            return False, f"Amount {amount} exceeds per-request limit {self.max_per_request}"
        
        # Check hourly limit
        hour_ago = int(time.time()) - 3600
        hourly_spent = sum(
            tx.amount_usdc for tx in self.transactions
            if tx.timestamp >= hour_ago and tx.success
        )
        
        if hourly_spent + amount > self.max_per_hour:
            return False, f"Would exceed hourly limit ({hourly_spent + amount} > {self.max_per_hour})"
        
        # Check daily limit
        day_ago = int(time.time()) - 86400
        daily_spent = sum(
            tx.amount_usdc for tx in self.transactions
            if tx.timestamp >= day_ago and tx.success
        )
        
        if daily_spent + amount > self.max_per_day:
            return False, f"Would exceed daily limit ({daily_spent + amount} > {self.max_per_day})"
        
        return True, ""
    
    def record_transaction(
        self,
        signature: str,
        amount_usdc: float,
        url: str,
        success: bool,
        error: Optional[str] = None
    ):
        """Record a transaction"""
        self.transactions.append(
            TransactionRecord(
                signature=signature,
                timestamp=int(time.time()),
                amount_usdc=amount_usdc,
                url=url,
                success=success,
                error=error
            )
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get spending statistics"""
        now = int(time.time())
        hour_ago = now - 3600
        day_ago = now - 86400
        
        hourly_spent = sum(
            tx.amount_usdc for tx in self.transactions
            if tx.timestamp >= hour_ago and tx.success
        )
        
        daily_spent = sum(
            tx.amount_usdc for tx in self.transactions
            if tx.timestamp >= day_ago and tx.success
        )
        
        total_spent = sum(
            tx.amount_usdc for tx in self.transactions
            if tx.success
        )
        
        return {
            "total_transactions": len(self.transactions),
            "successful": sum(1 for tx in self.transactions if tx.success),
            "failed": sum(1 for tx in self.transactions if not tx.success),
            "hourly_spent": hourly_spent,
            "daily_spent": daily_spent,
            "total_spent": total_spent,
            "limits": {
                "per_request": self.max_per_request,
                "per_hour": self.max_per_hour,
                "per_day": self.max_per_day
            }
        }


class PaymentAgent:
    """
    Autonomous payment agent with budget management
    
    An AI agent that can make x402 payments autonomously while
    respecting budget limits and tracking spending.
    
    Example:
        >>> # Create agent with budget limits
        >>> agent = PaymentAgent(
        ...     keypair=keypair,
        ...     max_per_request=0.10,  # 10 cents per request
        ...     max_per_hour=1.00,     # $1 per hour
        ...     max_per_day=10.00      # $10 per day
        ... )
        >>> 
        >>> # Agent autonomously fetches paid resources
        >>> data = await agent.fetch_resource(
        ...     "https://api.example.com/data",
        ...     max_price=0.05
        ... )
    """
    
    def __init__(
        self,
        keypair: Keypair,
        network: Network = Network.DEVNET,
        max_per_request: float = 1.0,
        max_per_hour: float = 10.0,
        max_per_day: float = 100.0,
        name: Optional[str] = None
    ):
        """
        Initialize payment agent
        
        Args:
            keypair: Solana keypair for the agent
            network: Solana network
            max_per_request: Max USDC per request
            max_per_hour: Max USDC per hour
            max_per_day: Max USDC per day
            name: Optional name for the agent
        """
        self.keypair = keypair
        self.network = network
        self.name = name or f"Agent-{str(keypair.pubkey())[:8]}"
        
        self.client = X402Client(keypair, network)
        self.budget = BudgetManager(
            max_per_request=max_per_request,
            max_per_hour=max_per_hour,
            max_per_day=max_per_day
        )
        
        logger.info(f"Agent {self.name} initialized with wallet {keypair.pubkey()}")
    
    async def fetch_resource(
        self,
        url: str,
        max_price: Optional[float] = None,
        method: str = "GET",
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch a resource with automatic payment and budget checking
        
        Args:
            url: Resource URL
            max_price: Maximum price willing to pay (uses budget limit if not set)
            method: HTTP method
            **kwargs: Additional request parameters
        
        Returns:
            Response data if successful, None if budget exceeded or failed
        """
        # Use budget limit if max_price not specified
        if max_price is None:
            max_price = self.budget.max_per_request
        
        # Check budget
        can_spend, reason = self.budget.can_spend(max_price)
        if not can_spend:
            logger.warning(f"Agent {self.name} cannot spend: {reason}")
            self.budget.record_transaction(
                signature="",
                amount_usdc=0,
                url=url,
                success=False,
                error=reason
            )
            return None
        
        # Attempt to fetch with payment
        try:
            logger.info(f"Agent {self.name} fetching {url} (max: ${max_price})")
            
            result = await self.client.fetch(
                url=url,
                max_price_usdc=max_price,
                method=method,
                **kwargs
            )
            
            # Record successful transaction
            # Note: Actual amount might be less than max_price
            self.budget.record_transaction(
                signature="success",  # Would get from response in full implementation
                amount_usdc=max_price,  # Conservative estimate
                url=url,
                success=True
            )
            
            logger.info(f"Agent {self.name} successfully fetched {url}")
            return result
        
        except Exception as e:
            logger.error(f"Agent {self.name} failed to fetch {url}: {e}")
            self.budget.record_transaction(
                signature="",
                amount_usdc=0,
                url=url,
                success=False,
                error=str(e)
            )
            return None
    
    async def batch_fetch(
        self,
        urls: List[str],
        max_price_per_url: float = None,
        max_concurrent: int = 5
    ) -> Dict[str, Any]:
        """
        Fetch multiple resources concurrently with budget management
        
        Args:
            urls: List of URLs to fetch
            max_price_per_url: Max price per URL
            max_concurrent: Max concurrent requests
        
        Returns:
            Dict mapping URLs to their data (or None if failed)
        """
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def fetch_with_semaphore(url: str):
            async with semaphore:
                return await self.fetch_resource(url, max_price_per_url)
        
        tasks = [fetch_with_semaphore(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return {
            url: result if not isinstance(result, Exception) else None
            for url, result in zip(urls, results)
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get agent statistics"""
        stats = self.budget.get_stats()
        stats["agent_name"] = self.name
        stats["wallet_address"] = str(self.keypair.pubkey())
        stats["network"] = self.network.value
        return stats
    
    def can_afford(self, price: float) -> bool:
        """Check if agent can afford a price"""
        can_spend, _ = self.budget.can_spend(price)
        return can_spend
    
    async def negotiate_price(
        self,
        url: str,
        target_price: float,
        max_attempts: int = 3
    ) -> Optional[Dict[str, Any]]:
        """
        Try to fetch resource with price negotiation
        
        Some APIs might accept lower payments. This tries progressively
        higher prices up to target_price.
        
        Args:
            url: Resource URL
            target_price: Maximum acceptable price
            max_attempts: Number of price points to try
        
        Returns:
            Data if successful at any price point
        """
        # Try different price points
        price_points = [
            target_price * (i + 1) / max_attempts
            for i in range(max_attempts)
        ]
        
        for price in price_points:
            logger.info(f"Agent {self.name} trying price ${price:.4f}")
            result = await self.fetch_resource(url, price)
            if result is not None:
                return result
        
        return None
    
    async def close(self):
        """Close agent connections"""
        await self.client.close()


# Agent coordination utilities
class AgentCoordinator:
    """
    Coordinate multiple payment agents
    
    Useful for managing a fleet of agents with shared or individual budgets.
    """
    
    def __init__(self):
        self.agents: Dict[str, PaymentAgent] = {}
    
    def add_agent(self, agent: PaymentAgent):
        """Add an agent to the coordinator"""
        self.agents[agent.name] = agent
        logger.info(f"Added agent {agent.name} to coordinator")
    
    def remove_agent(self, name: str):
        """Remove an agent"""
        if name in self.agents:
            del self.agents[name]
            logger.info(f"Removed agent {name}")
    
    async def distribute_task(
        self,
        urls: List[str],
        max_price_per_url: float = 0.10
    ) -> Dict[str, Any]:
        """
        Distribute URLs across available agents
        
        Agents work in parallel, each respecting their own budgets.
        
        Args:
            urls: URLs to fetch
            max_price_per_url: Max price per URL
        
        Returns:
            Combined results from all agents
        """
        if not self.agents:
            raise ValueError("No agents available")
        
        # Distribute URLs round-robin
        agent_tasks = {name: [] for name in self.agents}
        
        for i, url in enumerate(urls):
            agent_name = list(self.agents.keys())[i % len(self.agents)]
            agent_tasks[agent_name].append(url)
        
        # Execute in parallel
        results = {}
        tasks = []
        
        for agent_name, agent_urls in agent_tasks.items():
            if agent_urls:
                agent = self.agents[agent_name]
                task = agent.batch_fetch(agent_urls, max_price_per_url)
                tasks.append(task)
        
        all_results = await asyncio.gather(*tasks)
        
        # Combine results
        for result_dict in all_results:
            results.update(result_dict)
        
        return results
    
    def get_fleet_stats(self) -> Dict[str, Any]:
        """Get statistics for all agents"""
        return {
            agent_name: agent.get_stats()
            for agent_name, agent in self.agents.items()
        }
    
    def get_total_spent(self) -> float:
        """Get total amount spent by all agents"""
        total = 0.0
        for agent in self.agents.values():
            stats = agent.get_stats()
            total += stats["total_spent"]
        return total