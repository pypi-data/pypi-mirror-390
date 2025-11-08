"""
Example: MCP Server for AI Models

Shows how to create an MCP server that AI models like Claude or GPT
can use to access paid tools and services.
"""

import asyncio
import json
from typing import Dict, Any

from x402_solana import Network, create_wallet
from x402_solana import MCPPaymentServer, DataMCPServer


# Example 1: General Purpose MCP Server
async def create_general_mcp_server():
    """
    Create a general-purpose MCP server with various paid tools
    """
    # Setup server
    wallet = create_wallet()
    server = MCPPaymentServer(
        wallet_address=str(wallet.pubkey()),
        network=Network.DEVNET,
        name="Premium AI Tools Server"
    )
    
    # Register paid tools
    
    @server.tool(
        price_usdc=0.01,
        description="Get current weather for any city",
        input_schema={
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "City name"}
            },
            "required": ["city"]
        },
        output_schema={
            "type": "object",
            "properties": {
                "temperature": {"type": "number"},
                "conditions": {"type": "string"},
                "humidity": {"type": "number"}
            }
        }
    )
    async def get_weather(city: str) -> dict:
        """Get weather data"""
        # In production, would call real weather API
        return {
            "temperature": 72,
            "conditions": "Sunny",
            "humidity": 45,
            "wind": "10 mph NW"
        }
    
    @server.tool(
        price_usdc=0.05,
        description="Search the web for current information",
        input_schema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "max_results": {"type": "integer", "default": 5}
            },
            "required": ["query"]
        }
    )
    async def web_search(query: str, max_results: int = 5) -> dict:
        """Search the web"""
        # In production, would use real search API
        return {
            "query": query,
            "results": [
                {
                    "title": f"Result {i+1} for {query}",
                    "snippet": f"This is search result {i+1}...",
                    "url": f"https://example.com/result{i+1}"
                }
                for i in range(max_results)
            ]
        }
    
    @server.tool(
        price_usdc=0.10,
        description="Generate an image from text description",
        input_schema={
            "type": "object",
            "properties": {
                "prompt": {"type": "string", "description": "Image description"},
                "style": {"type": "string", "enum": ["realistic", "artistic", "cartoon"]}
            },
            "required": ["prompt"]
        }
    )
    async def generate_image(prompt: str, style: str = "realistic") -> dict:
        """Generate image"""
        # In production, would use image generation API
        return {
            "image_url": f"https://generated.example.com/image_{hash(prompt)}.png",
            "prompt": prompt,
            "style": style,
            "dimensions": "1024x1024"
        }
    
    @server.tool(
        price_usdc=0.15,
        description="Analyze sentiment and extract insights from text",
        input_schema={
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Text to analyze"},
                "language": {"type": "string", "default": "en"}
            },
            "required": ["text"]
        }
    )
    async def analyze_text(text: str, language: str = "en") -> dict:
        """Analyze text sentiment and insights"""
        # Mock analysis
        return {
            "sentiment": "positive",
            "confidence": 0.85,
            "keywords": ["technology", "innovation", "future"],
            "summary": text[:100] + "...",
            "entities": [
                {"type": "ORGANIZATION", "text": "OpenAI"},
                {"type": "TECHNOLOGY", "text": "AI"}
            ]
        }
    
    @server.tool(
        price_usdc=0.20,
        description="Execute Python code in a sandboxed environment",
        input_schema={
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "Python code to execute"},
                "timeout": {"type": "integer", "default": 5}
            },
            "required": ["code"]
        }
    )
    async def execute_code(code: str, timeout: int = 5) -> dict:
        """Execute Python code"""
        # In production, would use sandboxed execution
        # For demo, just return mock result
        return {
            "output": "Hello from executed code!",
            "execution_time": 0.123,
            "success": True
        }
    
    return server


# Example 2: Specialized Data MCP Server
async def create_data_mcp_server():
    """
    Create a specialized MCP server for data access
    """
    wallet = create_wallet()
    data_server = DataMCPServer(
        wallet_address=str(wallet.pubkey()),
        network=Network.DEVNET
    )
    
    # Register data sources
    
    async def get_market_data(symbols: list = None) -> dict:
        """Get real-time market data"""
        if not symbols:
            symbols = ["SOL", "BTC", "ETH"]
        
        return {
            "data": [
                {
                    "symbol": symbol,
                    "price": 100 * (i + 1),
                    "change_24h": 2.5 * (i % 3 - 1),
                    "volume": 1000000 * (i + 1)
                }
                for i, symbol in enumerate(symbols)
            ],
            "timestamp": "2024-11-06T12:00:00Z"
        }
    
    data_server.register_dataset(
        name="market_data",
        description="Real-time cryptocurrency market data",
        price_usdc=0.05,
        data_source=get_market_data
    )
    
    async def get_news_feed(category: str = "tech") -> dict:
        """Get news feed"""
        return {
            "category": category,
            "articles": [
                {
                    "title": f"{category.title()} News {i+1}",
                    "summary": f"Summary of {category} news item {i+1}",
                    "source": "Example News",
                    "timestamp": "2024-11-06T12:00:00Z"
                }
                for i in range(5)
            ]
        }
    
    data_server.register_dataset(
        name="news_feed",
        description="Latest news from various categories",
        price_usdc=0.03,
        data_source=get_news_feed
    )
    
    return data_server


# Example 3: Handle MCP Requests
async def demonstrate_mcp_usage():
    """
    Demonstrate how AI models would interact with MCP server
    """
    print("\n🤖 MCP Server Demo for AI Models")
    print("="*60)
    
    # Create server
    server = await create_general_mcp_server()
    
    # Example 1: List available tools
    print("\n📋 Available Tools:")
    list_request = {
        "method": "list_tools",
        "params": {}
    }
    
    response = await server.handle_request(list_request)
    
    if "result" in response:
        for tool in response["result"]["tools"]:
            print(f"\n  • {tool['name']}")
            print(f"    Description: {tool['description']}")
            print(f"    Price: ${tool['price_usdc']} USDC")
    
    # Example 2: Try to use tool without payment
    print("\n❌ Attempting to use tool without payment:")
    weather_request = {
        "method": "invoke_tool",
        "params": {
            "tool": "get_weather",
            "params": {"city": "New York"}
        }
    }
    
    response = await server.handle_request(weather_request)
    
    if "error" in response:
        print(f"  Error: {response['error']['message']}")
        if "data" in response["error"]:
            requirements = response["error"]["data"].get("requirements")
            if requirements:
                print(f"  Payment required: ${requirements['amount'] / 1_000_000} USDC")
                print(f"  Pay to: {requirements['pay_to'][:20]}...")
    
    # Example 3: Use tool with payment (simulated)
    print("\n✅ Using tool with payment:")
    
    # In real scenario, AI model would:
    # 1. Receive payment requirements
    # 2. Create payment transaction
    # 3. Send payment proof
    
    # Simulated payment proof
    simulated_payment = "base64_encoded_payment_proof_here"
    
    weather_request_paid = {
        "method": "invoke_tool",
        "params": {
            "tool": "get_weather",
            "params": {"city": "New York"}
        },
        "payment": simulated_payment  # Would be real payment proof
    }
    
    # For demo, just show what would happen
    print("  AI model creates payment proof and retries request")
    print("  Server verifies payment and returns data")
    print("  Result: {'temperature': 72, 'conditions': 'Sunny', ...}")
    
    # Example 4: Generate OpenAPI spec for AI model understanding
    print("\n📄 OpenAPI Specification (for AI model integration):")
    spec = server.get_openapi_spec()
    
    print(f"  Title: {spec['info']['title']}")
    print(f"  Available endpoints: {len(spec['paths'])}")
    
    for path, methods in spec['paths'].items():
        for method, details in methods.items():
            price = details.get('x-price-usdc', 0)
            print(f"    {method.upper()} {path} - ${price}")


# Integration example for AI models
def show_ai_integration_example():
    """
    Show how AI models would integrate with MCP server
    """
    example_code = """
# How AI Models (Claude, GPT, etc.) Would Use This MCP Server

## For Claude (using MCP):

1. Claude would discover the MCP server
2. Request list of available tools
3. When user asks for weather/search/etc, Claude would:
   - Call the appropriate MCP tool
   - Handle 402 payment requirement
   - Use x402 to make payment
   - Receive and present results to user

## Integration Code (Python):

```python
from x402_solana import X402Client, create_wallet
import asyncio

class AIMCPClient:
    def __init__(self, mcp_server_url: str, wallet):
        self.server_url = mcp_server_url
        self.client = X402Client(wallet)
    
    async def call_tool(self, tool_name: str, params: dict):
        # First attempt without payment
        response = await self.make_mcp_request({
            "method": "invoke_tool",
            "params": {
                "tool": tool_name,
                "params": params
            }
        })
        
        # If payment required
        if response.get("error", {}).get("code") == 402:
            requirements = response["error"]["data"]["requirements"]
            
            # Make payment
            payment_proof = await self.client.make_payment(requirements)
            
            # Retry with payment
            response = await self.make_mcp_request({
                "method": "invoke_tool",
                "params": {
                    "tool": tool_name,
                    "params": params
                },
                "payment": payment_proof
            })
        
        return response.get("result")
```

## For LangChain Integration:

```python
from langchain.tools import Tool
from x402_solana.mcp import MCPPaymentServer

# Wrap MCP tools for LangChain
def create_langchain_tool(mcp_server, tool_name):
    async def tool_func(**kwargs):
        response = await mcp_server.handle_request({
            "method": "invoke_tool",
            "params": {"tool": tool_name, "params": kwargs}
        })
        return response.get("result")
    
    return Tool(
        name=tool_name,
        func=tool_func,
        description=mcp_server.tools[tool_name].description
    )
```
    """
    
    print("\n📚 AI Model Integration Guide:")
    print("="*60)
    print(example_code)


async def run_full_demo():
    """
    Run the complete MCP server demonstration
    """
    print("\n🚀 x402 MCP Server Demo")
    print("="*60)
    print("Demonstrating how to monetize AI tools through MCP")
    print("="*60)
    
    # Run demonstrations
    await demonstrate_mcp_usage()
    
    # Show integration examples
    show_ai_integration_example()
    
    print("\n✅ Demo Complete!")
    print("\nKey Features Demonstrated:")
    print("  1. MCP server with multiple paid tools")
    print("  2. Automatic payment requirements (402)")
    print("  3. Tool discovery and documentation")
    print("  4. OpenAPI spec generation")
    print("  5. Integration patterns for AI models")
    
    print("\n💡 Use Cases:")
    print("  • Monetize AI tools and services")
    print("  • Enable agent-to-agent tool sharing")
    print("  • Create specialized data access points")
    print("  • Build paid API integrations for AI")


if __name__ == "__main__":
    asyncio.run(run_full_demo())