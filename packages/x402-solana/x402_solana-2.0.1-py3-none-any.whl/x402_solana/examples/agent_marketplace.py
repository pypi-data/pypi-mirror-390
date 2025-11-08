"""
Example: Agent-to-Agent Marketplace

Demonstrates autonomous agents trading services with each other.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from solders.keypair import Keypair

from x402_solana import (
    PaymentAgent,
    Network,
    create_wallet,
    save_wallet,
)
from x402_solana import AgentMCPServer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MarketplaceAgent(PaymentAgent):
    """
    An agent that can both buy and sell services
    """
    
    def __init__(
        self,
        keypair: Keypair,
        name: str,
        specialization: str,
        network: Network = Network.DEVNET
    ):
        super().__init__(
            keypair=keypair,
            network=network,
            max_per_request=0.50,
            max_per_hour=5.00,
            max_per_day=20.00,
            name=name
        )
        
        self.specialization = specialization
        self.mcp_server = AgentMCPServer(
            wallet_address=str(keypair.pubkey()),
            agent_name=name,
            network=network
        )
        
        # Track services and reputation
        self.services_offered: List[str] = []
        self.reputation_score = 100
        self.completed_transactions = 0
    
    def offer_service(
        self,
        service_name: str,
        price_usdc: float,
        description: str,
        handler: callable
    ):
        """Register a service this agent offers"""
        @self.mcp_server.service(
            price_usdc=price_usdc,
            description=description
        )
        async def service_handler(**params):
            result = await handler(**params)
            self.completed_transactions += 1
            self.reputation_score += 1
            return result
        
        service_handler.__name__ = service_name
        self.services_offered.append(service_name)
        
        logger.info(f"Agent {self.name} offering: {service_name} (${price_usdc})")
    
    async def request_service(
        self,
        provider_agent: 'MarketplaceAgent',
        service_name: str,
        params: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Request a service from another agent"""
        # Check if we can afford it
        service_price = self._get_service_price(provider_agent, service_name)
        if not self.can_afford(service_price):
            logger.warning(f"{self.name} cannot afford {service_name} from {provider_agent.name}")
            return None
        
        logger.info(f"{self.name} requesting {service_name} from {provider_agent.name}")
        
        # Make payment and get service
        response = await provider_agent.mcp_server.handle_agent_request(
            from_agent=self.name,
            service=service_name,
            params=params,
            payment=None  # In real implementation, would create payment proof
        )
        
        if "result" in response:
            logger.info(f"{self.name} received {service_name} from {provider_agent.name}")
            return response["result"]
        else:
            logger.error(f"{self.name} failed to get {service_name}: {response}")
            return None
    
    def _get_service_price(self, provider: 'MarketplaceAgent', service: str) -> float:
        """Get price for a service from provider"""
        for tool_name, tool in provider.mcp_server.tools.items():
            if tool_name == service:
                return tool.price_usdc
        return 0.0
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get agent information for marketplace listing"""
        return {
            "name": self.name,
            "address": str(self.keypair.pubkey()),
            "specialization": self.specialization,
            "services": self.services_offered,
            "reputation": self.reputation_score,
            "transactions": self.completed_transactions,
            "stats": self.get_stats()
        }


class AgentMarketplace:
    """
    Marketplace where agents can discover and trade services
    """
    
    def __init__(self, network: Network = Network.DEVNET):
        self.network = network
        self.agents: Dict[str, MarketplaceAgent] = {}
        self.transaction_history: List[Dict[str, Any]] = []
    
    def register_agent(self, agent: MarketplaceAgent):
        """Register an agent in the marketplace"""
        self.agents[agent.name] = agent
        logger.info(f"Registered {agent.name} in marketplace")
    
    def list_agents(self) -> List[Dict[str, Any]]:
        """List all agents and their services"""
        return [agent.get_agent_info() for agent in self.agents.values()]
    
    def find_service_providers(self, service_type: str) -> List[MarketplaceAgent]:
        """Find agents offering a specific service"""
        providers = []
        for agent in self.agents.values():
            if any(service_type in s for s in agent.services_offered):
                providers.append(agent)
        return providers
    
    async def facilitate_transaction(
        self,
        buyer: MarketplaceAgent,
        seller: MarketplaceAgent,
        service: str,
        params: Dict[str, Any]
    ) -> bool:
        """Facilitate a transaction between two agents"""
        result = await buyer.request_service(seller, service, params)
        
        if result:
            self.transaction_history.append({
                "timestamp": datetime.now().isoformat(),
                "buyer": buyer.name,
                "seller": seller.name,
                "service": service,
                "success": True
            })
            return True
        return False
    
    def get_market_stats(self) -> Dict[str, Any]:
        """Get marketplace statistics"""
        total_services = sum(len(a.services_offered) for a in self.agents.values())
        avg_reputation = sum(a.reputation_score for a in self.agents.values()) / len(self.agents) if self.agents else 0
        
        return {
            "total_agents": len(self.agents),
            "total_services": total_services,
            "total_transactions": len(self.transaction_history),
            "average_reputation": avg_reputation,
            "network": self.network.value
        }


async def simulate_marketplace():
    """
    Simulate an agent marketplace with multiple agents trading services
    """
    # Create marketplace
    marketplace = AgentMarketplace(Network.DEVNET)
    
    # Create specialized agents
    
    # 1. Data Analysis Agent
    analyst_wallet = create_wallet()
    analyst = MarketplaceAgent(
        keypair=analyst_wallet,
        name="DataAnalyst",
        specialization="Data Analysis and Visualization"
    )
    
    # Offer analysis service
    async def analyze_data(data: str) -> dict:
        return {
            "summary": f"Analysis of {len(data)} characters",
            "insights": ["Pattern A detected", "Trend B observed"],
            "confidence": 0.85
        }
    
    analyst.offer_service(
        service_name="analyze_data",
        price_usdc=0.10,
        description="Comprehensive data analysis",
        handler=analyze_data
    )
    
    # 2. Content Writer Agent
    writer_wallet = create_wallet()
    writer = MarketplaceAgent(
        keypair=writer_wallet,
        name="ContentWriter",
        specialization="Content Creation and Writing"
    )
    
    # Offer writing service
    async def write_content(topic: str, length: int) -> dict:
        return {
            "title": f"Article about {topic}",
            "content": f"This is a {length}-word article about {topic}...",
            "keywords": [topic, "technology", "innovation"]
        }
    
    writer.offer_service(
        service_name="write_article",
        price_usdc=0.15,
        description="Professional article writing",
        handler=write_content
    )
    
    # 3. Research Agent
    researcher_wallet = create_wallet()
    researcher = MarketplaceAgent(
        keypair=researcher_wallet,
        name="Researcher",
        specialization="Research and Information Gathering"
    )
    
    # Offer research service
    async def research_topic(topic: str) -> dict:
        return {
            "topic": topic,
            "sources": ["Source A", "Source B", "Source C"],
            "summary": f"Comprehensive research on {topic}",
            "citations": 15
        }
    
    researcher.offer_service(
        service_name="research",
        price_usdc=0.08,
        description="In-depth research service",
        handler=research_topic
    )
    
    # 4. Translation Agent
    translator_wallet = create_wallet()
    translator = MarketplaceAgent(
        keypair=translator_wallet,
        name="Translator",
        specialization="Language Translation"
    )
    
    # Offer translation service
    async def translate_text(text: str, target_lang: str) -> dict:
        return {
            "original": text,
            "translated": f"[{target_lang}] {text}",
            "language": target_lang,
            "confidence": 0.92
        }
    
    translator.offer_service(
        service_name="translate",
        price_usdc=0.05,
        description="Multi-language translation",
        handler=translate_text
    )
    
    # Register all agents
    marketplace.register_agent(analyst)
    marketplace.register_agent(writer)
    marketplace.register_agent(researcher)
    marketplace.register_agent(translator)
    
    print("\n🏪 Agent Marketplace Initialized")
    print("="*60)
    
    # Show marketplace
    print("\n📋 Available Agents:")
    for agent_info in marketplace.list_agents():
        print(f"\n  {agent_info['name']} ({agent_info['specialization']})")
        print(f"    Address: {agent_info['address'][:20]}...")
        print(f"    Services: {', '.join(agent_info['services'])}")
        print(f"    Reputation: {agent_info['reputation']}")
    
    print("\n💱 Simulating Agent Transactions...")
    print("="*60)
    
    # Simulate transactions between agents
    
    # Writer needs research for an article
    print("\n1. Writer requests research from Researcher")
    await marketplace.facilitate_transaction(
        buyer=writer,
        seller=researcher,
        service="research",
        params={"topic": "AI in Healthcare"}
    )
    
    # Analyst needs content written
    print("\n2. Analyst requests article from Writer")
    await marketplace.facilitate_transaction(
        buyer=analyst,
        seller=writer,
        service="write_article",
        params={"topic": "Data Science Trends", "length": 500}
    )
    
    # Researcher needs translation
    print("\n3. Researcher requests translation from Translator")
    await marketplace.facilitate_transaction(
        buyer=researcher,
        seller=translator,
        service="translate",
        params={"text": "Important research findings", "target_lang": "Spanish"}
    )
    
    # Translator needs data analysis
    print("\n4. Translator requests analysis from Analyst")
    await marketplace.facilitate_transaction(
        buyer=translator,
        seller=analyst,
        service="analyze_data",
        params={"data": "Translation performance metrics"}
    )
    
    # Show final marketplace stats
    print("\n📊 Marketplace Statistics:")
    print("="*60)
    stats = marketplace.get_market_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Show agent earnings
    print("\n💰 Agent Statistics:")
    for agent in marketplace.agents.values():
        agent_stats = agent.get_stats()
        print(f"\n  {agent.name}:")
        print(f"    Completed: {agent.completed_transactions} transactions")
        print(f"    Reputation: {agent.reputation_score}")
        print(f"    Spent: ${agent_stats['total_spent']:.2f}")


def main():
    """
    Run the agent marketplace simulation
    """
    print("\n🤖 x402 Agent-to-Agent Marketplace Demo")
    print("="*60)
    print("This demonstrates how AI agents can autonomously trade services")
    print("using x402 payments on Solana.")
    print("="*60)
    
    # Run simulation
    asyncio.run(simulate_marketplace())
    
    print("\n✅ Simulation complete!")
    print("\nKey Takeaways:")
    print("  1. Agents can offer specialized services")
    print("  2. Agents can discover and purchase services from others")
    print("  3. All transactions are settled instantly on Solana")
    print("  4. Reputation system tracks agent reliability")
    print("  5. Budget management prevents overspending")


if __name__ == "__main__":
    main()