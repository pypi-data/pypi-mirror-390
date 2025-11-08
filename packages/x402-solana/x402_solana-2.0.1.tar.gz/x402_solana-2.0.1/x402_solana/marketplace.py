"""
x402 Agent-to-Agent (A2A) Marketplace

Advanced marketplace for autonomous agent service trading.
Built for Hackathon Category 2: Agent-to-Agent Payments ($10k prize)
"""

import asyncio
import json
import time
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum
import logging

from .agent import PaymentAgent
from .identity import AgentRegistry, AgentIdentity
from .types import Network

logger = logging.getLogger(__name__)


class ServiceCategory(str, Enum):
    """Standard service categories for discovery"""
    DATA_ANALYSIS = "data_analysis"
    CONTENT_CREATION = "content_creation"
    IMAGE_GENERATION = "image_generation"
    CODE_GENERATION = "code_generation"
    TRANSLATION = "translation"
    RESEARCH = "research"
    COMPUTATION = "computation"
    STORAGE = "storage"
    VERIFICATION = "verification"
    ORACLE = "oracle"


@dataclass
class ServiceListing:
    """Service offered by an agent"""
    id: str
    provider: str  # Agent address
    name: str
    category: ServiceCategory
    description: str
    price_usdc: float
    min_reputation: float  # Minimum buyer reputation required
    max_daily_calls: int
    current_daily_calls: int
    metadata: Dict[str, Any]
    active: bool = True


@dataclass
class ServiceRequest:
    """Request for service from one agent to another"""
    id: str
    requester: str  # Agent address
    service_id: str
    parameters: Dict[str, Any]
    max_price: float
    timestamp: int
    deadline: Optional[int] = None


@dataclass
class ServiceResponse:
    """Response to service request"""
    request_id: str
    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None
    payment_signature: Optional[str] = None
    execution_time: float = 0.0


class A2AMarketplace:
    """
    Decentralized marketplace for agent-to-agent service trading
    
    Features:
    - Service discovery
    - Automatic matching
    - Price negotiation
    - Reputation-based access control
    - Service level agreements (SLAs)
    """
    
    def __init__(
        self,
        network: Network = Network.DEVNET,
        registry: Optional[AgentRegistry] = None
    ):
        self.network = network
        self.registry = registry or AgentRegistry()
        self.services: Dict[str, ServiceListing] = {}
        self.pending_requests: Dict[str, ServiceRequest] = {}
        self.service_handlers: Dict[str, Callable] = {}
        
        # Metrics
        self.total_transactions = 0
        self.total_volume = 0.0
        
        logger.info("A2A Marketplace initialized")
    
    def register_service(
        self,
        agent: PaymentAgent,
        name: str,
        category: ServiceCategory,
        description: str,
        price_usdc: float,
        handler: Callable,
        min_reputation: float = 0.0,
        max_daily_calls: int = 100,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Register a service offering
        
        Args:
            agent: Provider agent
            name: Service name
            category: Service category
            description: Service description
            price_usdc: Price per call
            handler: Async function to handle requests
            min_reputation: Minimum reputation required
            max_daily_calls: Rate limit
            metadata: Additional metadata
        
        Returns:
            Service ID
        """
        service_id = f"{agent.name}_{name}_{int(time.time())}"
        
        listing = ServiceListing(
            id=service_id,
            provider=str(agent.keypair.pubkey()),
            name=name,
            category=category,
            description=description,
            price_usdc=price_usdc,
            min_reputation=min_reputation,
            max_daily_calls=max_daily_calls,
            current_daily_calls=0,
            metadata=metadata or {}
        )
        
        self.services[service_id] = listing
        self.service_handlers[service_id] = handler
        
        logger.info(f"Service registered: {name} by {agent.name} (${price_usdc})")
        return service_id
    
    async def discover_services(
        self,
        category: Optional[ServiceCategory] = None,
        max_price: Optional[float] = None,
        min_reputation: Optional[float] = None
    ) -> List[ServiceListing]:
        """
        Discover available services
        
        Args:
            category: Filter by category
            max_price: Maximum price filter
            min_reputation: Minimum provider reputation
        
        Returns:
            List of matching services
        """
        matches = []
        
        for service in self.services.values():
            if not service.active:
                continue
            
            if category and service.category != category:
                continue
            
            if max_price and service.price_usdc > max_price:
                continue
            
            # Check provider reputation
            if min_reputation:
                reputation = self.registry.get_reputation(service.provider)
                if reputation.trust_score < min_reputation:
                    continue
            
            matches.append(service)
        
        # Sort by price and reputation
        matches.sort(key=lambda x: (x.price_usdc, -self._get_provider_reputation(x.provider)))
        return matches
    
    async def request_service(
        self,
        requester: PaymentAgent,
        service_id: str,
        parameters: Dict[str, Any],
        max_price: Optional[float] = None
    ) -> ServiceResponse:
        """
        Request a service from another agent
        
        Args:
            requester: Requesting agent
            service_id: Service to request
            parameters: Service parameters
            max_price: Maximum willing to pay
        
        Returns:
            Service response
        """
        if service_id not in self.services:
            return ServiceResponse(
                request_id="",
                success=False,
                error="Service not found"
            )
        
        service = self.services[service_id]
        
        # Check rate limits
        if service.current_daily_calls >= service.max_daily_calls:
            return ServiceResponse(
                request_id="",
                success=False,
                error="Service rate limit exceeded"
            )
        
        # Check requester reputation
        requester_rep = self.registry.get_reputation(str(requester.keypair.pubkey()))
        if requester_rep.trust_score < service.min_reputation:
            return ServiceResponse(
                request_id="",
                success=False,
                error=f"Insufficient reputation: {requester_rep.trust_score:.1f} < {service.min_reputation}"
            )
        
        # Check budget
        if max_price and service.price_usdc > max_price:
            return ServiceResponse(
                request_id="",
                success=False,
                error=f"Price {service.price_usdc} exceeds max {max_price}"
            )
        
        if not requester.can_afford(service.price_usdc):
            return ServiceResponse(
                request_id="",
                success=False,
                error="Insufficient budget"
            )
        
        # Create request
        request_id = f"req_{int(time.time() * 1000)}"
        request = ServiceRequest(
            id=request_id,
            requester=str(requester.keypair.pubkey()),
            service_id=service_id,
            parameters=parameters,
            max_price=max_price or service.price_usdc,
            timestamp=int(time.time())
        )
        
        # Execute service
        start_time = time.time()
        try:
            handler = self.service_handlers[service_id]
            result = await handler(**parameters)
            
            # Process payment (simulated for hackathon)
            payment_signature = f"sim_payment_{request_id}"
            
            # Update metrics
            service.current_daily_calls += 1
            self.total_transactions += 1
            self.total_volume += service.price_usdc
            
            # Record transaction in registry
            self.registry.record_transaction(
                from_agent=request.requester,
                to_agent=service.provider,
                amount_usdc=service.price_usdc,
                success=True,
                signature=payment_signature,
                rating=5  # Auto 5-star for successful
            )
            
            execution_time = time.time() - start_time
            
            logger.info(
                f"Service executed: {service.name} for {requester.name} "
                f"(${service.price_usdc}, {execution_time:.2f}s)"
            )
            
            return ServiceResponse(
                request_id=request_id,
                success=True,
                result=result,
                payment_signature=payment_signature,
                execution_time=execution_time
            )
            
        except Exception as e:
            logger.error(f"Service execution failed: {e}")
            return ServiceResponse(
                request_id=request_id,
                success=False,
                error=str(e),
                execution_time=time.time() - start_time
            )
    
    async def negotiate_price(
        self,
        requester: PaymentAgent,
        service_id: str,
        target_price: float
    ) -> Optional[float]:
        """
        Negotiate service price
        
        Simple negotiation: Accept if within 20% of list price
        """
        if service_id not in self.services:
            return None
        
        service = self.services[service_id]
        
        # Check if negotiation is acceptable
        min_acceptable = service.price_usdc * 0.8
        
        if target_price >= min_acceptable:
            logger.info(f"Price negotiated: ${service.price_usdc} -> ${target_price}")
            return target_price
        
        return None
    
    def _get_provider_reputation(self, provider_address: str) -> float:
        """Get provider's reputation score"""
        rep = self.registry.get_reputation(provider_address)
        return rep.trust_score
    
    def get_market_stats(self) -> Dict[str, Any]:
        """Get marketplace statistics"""
        active_services = sum(1 for s in self.services.values() if s.active)
        avg_price = sum(s.price_usdc for s in self.services.values()) / len(self.services) if self.services else 0
        
        return {
            "total_services": len(self.services),
            "active_services": active_services,
            "average_price": avg_price,
            "total_transactions": self.total_transactions,
            "total_volume": self.total_volume,
            "categories": list(set(s.category for s in self.services.values()))
        }


class ServiceOrchestrator:
    """
    Orchestrate complex multi-agent workflows
    """
    
    def __init__(self, marketplace: A2AMarketplace):
        self.marketplace = marketplace
    
    async def execute_workflow(
        self,
        initiator: PaymentAgent,
        workflow: List[Dict[str, Any]]
    ) -> List[ServiceResponse]:
        """
        Execute a multi-step workflow across multiple agents
        
        Example workflow:
        [
            {"service": "research", "params": {"topic": "AI"}},
            {"service": "analysis", "params": {"data": "{previous_result}"}},
            {"service": "report", "params": {"analysis": "{previous_result}"}}
        ]
        """
        results = []
        previous_result = None
        
        for step in workflow:
            # Find matching service
            services = await self.marketplace.discover_services(
                category=step.get("category"),
                max_price=step.get("max_price")
            )
            
            if not services:
                results.append(ServiceResponse(
                    request_id=f"step_{len(results)}",
                    success=False,
                    error="No matching service found"
                ))
                break
            
            # Use best service
            service = services[0]
            
            # Substitute previous result in parameters
            params = step["params"].copy()
            for key, value in params.items():
                if isinstance(value, str) and "{previous_result}" in value:
                    params[key] = previous_result
            
            # Execute service
            response = await self.marketplace.request_service(
                requester=initiator,
                service_id=service.id,
                parameters=params
            )
            
            results.append(response)
            
            if not response.success:
                break
            
            previous_result = response.result
        
        return results


class AgentDAO:
    """
    Decentralized Autonomous Organization for agents
    
    Agents can vote on marketplace rules, fee structures, etc.
    """
    
    def __init__(self, registry: AgentRegistry):
        self.registry = registry
        self.proposals: Dict[str, Dict] = {}
        self.votes: Dict[str, Dict[str, bool]] = {}
    
    def create_proposal(
        self,
        proposer: str,
        title: str,
        description: str,
        action: Dict[str, Any]
    ) -> str:
        """Create a governance proposal"""
        proposal_id = f"prop_{int(time.time())}"
        
        self.proposals[proposal_id] = {
            "id": proposal_id,
            "proposer": proposer,
            "title": title,
            "description": description,
            "action": action,
            "created_at": int(time.time()),
            "status": "active"
        }
        
        self.votes[proposal_id] = {}
        
        logger.info(f"Proposal created: {title}")
        return proposal_id
    
    def vote(self, voter: str, proposal_id: str, support: bool):
        """Cast a vote weighted by reputation"""
        if proposal_id not in self.proposals:
            raise ValueError("Proposal not found")
        
        if self.proposals[proposal_id]["status"] != "active":
            raise ValueError("Proposal not active")
        
        # Weight vote by reputation
        reputation = self.registry.get_reputation(voter)
        weight = reputation.trust_score / 100.0
        
        self.votes[proposal_id][voter] = support
        
        logger.info(f"Vote cast: {voter[:8]}... -> {proposal_id} ({support})")
    
    def execute_proposal(self, proposal_id: str) -> bool:
        """Execute proposal if it passes"""
        if proposal_id not in self.proposals:
            return False
        
        # Calculate weighted votes
        total_for = 0.0
        total_against = 0.0
        
        for voter, support in self.votes[proposal_id].items():
            reputation = self.registry.get_reputation(voter)
            weight = reputation.trust_score / 100.0
            
            if support:
                total_for += weight
            else:
                total_against += weight
        
        # Require 66% approval
        if total_for / (total_for + total_against) >= 0.66:
            self.proposals[proposal_id]["status"] = "executed"
            logger.info(f"Proposal executed: {self.proposals[proposal_id]['title']}")
            return True
        
        self.proposals[proposal_id]["status"] = "rejected"
        return False