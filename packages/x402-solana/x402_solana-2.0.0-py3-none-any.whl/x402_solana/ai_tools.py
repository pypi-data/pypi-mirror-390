"""
x402 AI Tools & Applications

Practical AI agent applications with autonomous payment capabilities.
Built for Hackathon Category 5: Practical Applications ($10k prize)
"""

import json
import asyncio
import time
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum
import logging

from .agent import PaymentAgent
from .marketplace import A2AMarketplace, ServiceCategory
from .mcp import MCPPaymentServer

logger = logging.getLogger(__name__)


class AIToolkit:
    """
    Suite of AI-powered tools that agents can use with x402 payments
    """
    
    def __init__(self, payment_agent: PaymentAgent):
        self.agent = payment_agent
        self.tools_used = 0
        self.total_spent = 0.0
    
    async def generate_image(
        self,
        prompt: str,
        style: str = "realistic",
        api_url: str = "https://api.stability.ai/v1/generation"
    ) -> Optional[str]:
        """
        Generate an image using Stable Diffusion API
        
        Automatically handles payment for API access
        """
        response = await self.agent.fetch_resource(
            url=f"{api_url}/text-to-image",
            max_price=0.02,  # $0.02 per image
            method="POST",
            json={
                "prompt": prompt,
                "style": style,
                "width": 1024,
                "height": 1024
            }
        )
        
        if response and "image_url" in response:
            self.tools_used += 1
            self.total_spent += 0.02
            return response["image_url"]
        return None
    
    async def analyze_code(
        self,
        code: str,
        language: str = "python"
    ) -> Dict[str, Any]:
        """
        Analyze code for bugs, security issues, and improvements
        
        Uses paid code analysis service
        """
        response = await self.agent.fetch_resource(
            url="https://api.codeanalysis.ai/analyze",
            max_price=0.05,
            method="POST",
            json={
                "code": code,
                "language": language,
                "checks": ["bugs", "security", "performance", "style"]
            }
        )
        
        if response:
            self.tools_used += 1
            self.total_spent += 0.05
            return response
        return {}
    
    async def generate_content(
        self,
        topic: str,
        content_type: str = "article",
        length: int = 500
    ) -> Optional[str]:
        """
        Generate content using AI
        
        Pays for high-quality content generation
        """
        response = await self.agent.fetch_resource(
            url="https://api.contentai.com/generate",
            max_price=0.10,
            method="POST",
            json={
                "topic": topic,
                "type": content_type,
                "length": length,
                "quality": "high"
            }
        )
        
        if response and "content" in response:
            self.tools_used += 1
            self.total_spent += 0.10
            return response["content"]
        return None
    
    async def translate_document(
        self,
        text: str,
        target_language: str,
        source_language: str = "auto"
    ) -> Optional[str]:
        """
        Translate documents using premium translation API
        """
        response = await self.agent.fetch_resource(
            url="https://api.deepl.com/v2/translate",
            max_price=0.01,
            method="POST",
            json={
                "text": text,
                "target_lang": target_language,
                "source_lang": source_language
            }
        )
        
        if response and "translation" in response:
            self.tools_used += 1
            self.total_spent += 0.01
            return response["translation"]
        return None
    
    async def research_topic(
        self,
        topic: str,
        depth: str = "comprehensive"
    ) -> Dict[str, Any]:
        """
        Conduct research on a topic using multiple paid sources
        """
        sources = []
        total_cost = 0.0
        
        # Search academic papers
        papers = await self.agent.fetch_resource(
            url="https://api.semanticscholar.org/search",
            max_price=0.05,
            method="GET",
            params={"query": topic, "limit": 10}
        )
        if papers:
            sources.append({"type": "academic", "data": papers})
            total_cost += 0.05
        
        # Search news
        news = await self.agent.fetch_resource(
            url="https://api.newsapi.org/everything",
            max_price=0.02,
            method="GET",
            params={"q": topic, "pageSize": 20}
        )
        if news:
            sources.append({"type": "news", "data": news})
            total_cost += 0.02
        
        # Get market data if relevant
        if any(keyword in topic.lower() for keyword in ["stock", "crypto", "market"]):
            market = await self.agent.fetch_resource(
                url="https://api.marketdata.com/search",
                max_price=0.10,
                method="GET",
                params={"query": topic}
            )
            if market:
                sources.append({"type": "market", "data": market})
                total_cost += 0.10
        
        self.tools_used += len(sources)
        self.total_spent += total_cost
        
        return {
            "topic": topic,
            "sources": sources,
            "cost": total_cost,
            "timestamp": int(time.time())
        }
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get tool usage statistics"""
        return {
            "tools_used": self.tools_used,
            "total_spent": self.total_spent,
            "agent_budget_remaining": self.agent.budget.max_per_day - self.agent.get_stats()["daily_spent"]
        }


class AIAgentFramework:
    """
    Framework for building practical AI agent applications
    """
    
    def __init__(
        self,
        agent: PaymentAgent,
        marketplace: A2AMarketplace,
        mcp_server: Optional[MCPPaymentServer] = None
    ):
        self.agent = agent
        self.marketplace = marketplace
        self.mcp_server = mcp_server
        self.toolkit = AIToolkit(agent)
        
        # Task queue for autonomous operation
        self.task_queue: List[Dict[str, Any]] = []
        self.completed_tasks: List[Dict[str, Any]] = []
    
    async def autonomous_loop(self):
        """
        Main autonomous operation loop
        
        Continuously processes tasks, discovers services, and executes jobs
        """
        while True:
            try:
                # Process task queue
                if self.task_queue:
                    task = self.task_queue.pop(0)
                    result = await self.execute_task(task)
                    self.completed_tasks.append({
                        "task": task,
                        "result": result,
                        "timestamp": int(time.time())
                    })
                
                # Discover new opportunities
                opportunities = await self.discover_opportunities()
                for opp in opportunities:
                    if self.should_pursue(opp):
                        self.task_queue.append(opp)
                
                # Sleep before next iteration
                await asyncio.sleep(10)
                
            except Exception as e:
                logger.error(f"Autonomous loop error: {e}")
                await asyncio.sleep(30)
    
    async def execute_task(self, task: Dict[str, Any]) -> Any:
        """Execute a single task"""
        task_type = task.get("type")
        
        if task_type == "image_generation":
            return await self.toolkit.generate_image(
                prompt=task["prompt"],
                style=task.get("style", "realistic")
            )
        
        elif task_type == "content_creation":
            return await self.toolkit.generate_content(
                topic=task["topic"],
                content_type=task.get("content_type", "article")
            )
        
        elif task_type == "research":
            return await self.toolkit.research_topic(
                topic=task["topic"],
                depth=task.get("depth", "comprehensive")
            )
        
        elif task_type == "service_request":
            return await self.marketplace.request_service(
                requester=self.agent,
                service_id=task["service_id"],
                parameters=task["parameters"]
            )
        
        else:
            logger.warning(f"Unknown task type: {task_type}")
            return None
    
    async def discover_opportunities(self) -> List[Dict[str, Any]]:
        """
        Discover profitable opportunities in the marketplace
        """
        opportunities = []
        
        # Find underpriced services
        services = await self.marketplace.discover_services(max_price=0.10)
        for service in services[:5]:  # Top 5 cheapest
            expected_value = self.estimate_value(service.category)
            if expected_value > service.price_usdc * 1.5:  # 50% profit margin
                opportunities.append({
                    "type": "service_request",
                    "service_id": service.id,
                    "parameters": {},
                    "expected_profit": expected_value - service.price_usdc
                })
        
        return opportunities
    
    def should_pursue(self, opportunity: Dict[str, Any]) -> bool:
        """Decide whether to pursue an opportunity"""
        # Check if we can afford it
        if not self.agent.can_afford(opportunity.get("price", 0.10)):
            return False
        
        # Check expected profit
        if opportunity.get("expected_profit", 0) < 0.01:
            return False
        
        # Check task queue isn't too full
        if len(self.task_queue) > 10:
            return False
        
        return True
    
    def estimate_value(self, category: ServiceCategory) -> float:
        """Estimate the value of a service category"""
        value_map = {
            ServiceCategory.DATA_ANALYSIS: 0.20,
            ServiceCategory.IMAGE_GENERATION: 0.15,
            ServiceCategory.CODE_GENERATION: 0.25,
            ServiceCategory.RESEARCH: 0.30,
            ServiceCategory.ORACLE: 0.50,
        }
        return value_map.get(category, 0.10)


class AIAssistant:
    """
    Practical AI assistant that can be deployed for users
    """
    
    def __init__(self, framework: AIAgentFramework):
        self.framework = framework
        self.conversations: Dict[str, List[Dict]] = {}
    
    async def handle_user_request(
        self,
        user_id: str,
        message: str
    ) -> str:
        """
        Handle a user request, automatically using paid services as needed
        """
        # Store conversation
        if user_id not in self.conversations:
            self.conversations[user_id] = []
        
        self.conversations[user_id].append({
            "role": "user",
            "content": message,
            "timestamp": int(time.time())
        })
        
        # Determine intent and required actions
        actions = self.parse_intent(message)
        
        # Execute required paid services
        results = []
        for action in actions:
            if action["type"] == "research":
                research = await self.framework.toolkit.research_topic(action["topic"])
                results.append(f"Research completed on {action['topic']}")
            
            elif action["type"] == "image":
                image_url = await self.framework.toolkit.generate_image(action["prompt"])
                results.append(f"Generated image: {image_url}")
            
            elif action["type"] == "translate":
                translation = await self.framework.toolkit.translate_document(
                    action["text"],
                    action["target_language"]
                )
                results.append(f"Translation: {translation}")
        
        response = "\n".join(results) if results else "I can help you with that. What specific service do you need?"
        
        self.conversations[user_id].append({
            "role": "assistant",
            "content": response,
            "timestamp": int(time.time()),
            "cost": self.framework.toolkit.total_spent
        })
        
        return response
    
    def parse_intent(self, message: str) -> List[Dict[str, Any]]:
        """Parse user intent to determine required actions"""
        actions = []
        message_lower = message.lower()
        
        # Simple keyword-based parsing (in production, use NLP)
        if "research" in message_lower or "find information" in message_lower:
            # Extract topic (simple approach)
            words = message.split()
            topic = " ".join(words[-3:])  # Last 3 words as topic
            actions.append({"type": "research", "topic": topic})
        
        if "image" in message_lower or "picture" in message_lower or "generate" in message_lower:
            actions.append({"type": "image", "prompt": message})
        
        if "translate" in message_lower:
            # Extract language (simple approach)
            if "spanish" in message_lower:
                target = "ES"
            elif "french" in message_lower:
                target = "FR"
            elif "german" in message_lower:
                target = "DE"
            else:
                target = "EN"
            
            actions.append({
                "type": "translate",
                "text": message,
                "target_language": target
            })
        
        return actions


# Specialized AI Applications

class AIDataAnalyst(AIAgentFramework):
    """Specialized agent for data analysis tasks"""
    
    async def analyze_dataset(self, data: List[Dict]) -> Dict[str, Any]:
        """Analyze a dataset using paid analysis services"""
        # Use multiple analysis services
        statistical = await self.agent.fetch_resource(
            url="https://api.statsai.com/analyze",
            max_price=0.10,
            method="POST",
            json={"data": data, "analysis_type": "statistical"}
        )
        
        visualization = await self.agent.fetch_resource(
            url="https://api.chartsai.com/visualize",
            max_price=0.05,
            method="POST",
            json={"data": data, "chart_types": ["bar", "line", "scatter"]}
        )
        
        return {
            "statistical_analysis": statistical,
            "visualizations": visualization,
            "cost": 0.15
        }


class AIContentCreator(AIAgentFramework):
    """Specialized agent for content creation"""
    
    async def create_blog_post(
        self,
        topic: str,
        keywords: List[str]
    ) -> Dict[str, Any]:
        """Create a complete blog post with images"""
        # Research topic
        research = await self.toolkit.research_topic(topic)
        
        # Generate content
        content = await self.toolkit.generate_content(
            topic=topic,
            content_type="blog",
            length=1000
        )
        
        # Generate header image
        image = await self.toolkit.generate_image(
            prompt=f"Blog header image for {topic}, professional",
            style="photorealistic"
        )
        
        return {
            "title": f"Complete Guide to {topic}",
            "content": content,
            "image": image,
            "research": research,
            "keywords": keywords,
            "total_cost": self.toolkit.total_spent
        }


class AITrader(AIAgentFramework):
    """Specialized agent for trading and market analysis"""
    
    async def analyze_market(self, symbol: str) -> Dict[str, Any]:
        """Analyze market conditions for a symbol"""
        # Get market data
        market_data = await self.agent.fetch_resource(
            url=f"https://api.polygon.io/v2/aggs/ticker/{symbol}",
            max_price=0.01
        )
        
        # Get sentiment analysis
        sentiment = await self.agent.fetch_resource(
            url="https://api.sentimentai.com/analyze",
            max_price=0.05,
            method="POST",
            json={"symbol": symbol, "sources": ["news", "social", "reddit"]}
        )
        
        # Get technical analysis
        technical = await self.agent.fetch_resource(
            url="https://api.taapi.io/indicators",
            max_price=0.02,
            method="POST",
            json={"symbol": symbol, "indicators": ["RSI", "MACD", "BB"]}
        )
        
        return {
            "symbol": symbol,
            "market_data": market_data,
            "sentiment": sentiment,
            "technical": technical,
            "recommendation": self.generate_recommendation(market_data, sentiment, technical)
        }
    
    def generate_recommendation(self, market, sentiment, technical) -> str:
        """Generate trading recommendation based on analysis"""
        # Simple logic (in production, use ML)
        if sentiment and sentiment.get("overall", 0) > 0.7:
            if technical and technical.get("RSI", 50) < 70:
                return "BUY"
        elif sentiment and sentiment.get("overall", 0) < 0.3:
            return "SELL"
        return "HOLD"