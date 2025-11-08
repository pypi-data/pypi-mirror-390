"""
x402 MCP (Model Context Protocol) Server

Connect AI agents to x402 payments through MCP.
This enables Claude, GPT, and other AI models to make autonomous payments.
"""

import json
import logging
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass

from .server import X402Server, NonceStore
from .types import (
    PaymentRequirements,
    PaymentPayload,
    Network,
    usdc_to_lamports,
)

logger = logging.getLogger(__name__)


@dataclass
class MCPTool:
    """Definition of an MCP tool that requires payment"""
    name: str
    description: str
    price_usdc: float
    handler: Callable
    input_schema: Optional[Dict[str, Any]] = None
    output_schema: Optional[Dict[str, Any]] = None


class MCPPaymentServer:
    """
    MCP server with x402 payment integration
    
    This allows AI models to access paid tools and services through
    the Model Context Protocol, with automatic payment handling.
    
    Example:
        >>> # Create MCP server
        >>> mcp = MCPPaymentServer(
        ...     wallet_address="YOUR_ADDRESS",
        ...     network=Network.DEVNET
        ... )
        >>> 
        >>> # Register a paid tool
        >>> @mcp.tool(price_usdc=0.01, description="Get weather data")
        >>> async def get_weather(city: str) -> dict:
        ...     return {"city": city, "temp": 72, "conditions": "sunny"}
        >>> 
        >>> # Handle MCP requests from AI agents
        >>> response = await mcp.handle_request(mcp_request)
    """
    
    def __init__(
        self,
        wallet_address: str,
        network: Network = Network.DEVNET,
        name: str = "x402 MCP Server"
    ):
        """
        Initialize MCP payment server
        
        Args:
            wallet_address: Solana address to receive payments
            network: Solana network
            name: Server name for identification
        """
        self.wallet_address = wallet_address
        self.network = network
        self.name = name
        
        self.server = X402Server(wallet_address, network)
        self.tools: Dict[str, MCPTool] = {}
        
        logger.info(f"MCP Payment Server initialized: {name}")
    
    def tool(
        self,
        price_usdc: float,
        description: str,
        input_schema: Optional[Dict[str, Any]] = None,
        output_schema: Optional[Dict[str, Any]] = None
    ):
        """
        Decorator to register a paid MCP tool
        
        Args:
            price_usdc: Price in USDC to use this tool
            description: Human-readable description
            input_schema: JSON schema for inputs
            output_schema: JSON schema for outputs
        
        Example:
            >>> @mcp.tool(price_usdc=0.05, description="Analyze data")
            >>> async def analyze(data: str) -> dict:
            ...     return {"summary": "Analysis of " + data}
        """
        def decorator(func: Callable) -> Callable:
            tool = MCPTool(
                name=func.__name__,
                description=description,
                price_usdc=price_usdc,
                handler=func,
                input_schema=input_schema,
                output_schema=output_schema
            )
            
            self.tools[tool.name] = tool
            logger.info(f"Registered MCP tool: {tool.name} (${price_usdc})")
            
            return func
        
        return decorator
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle MCP request from an AI agent
        
        Args:
            request: MCP request with method, params, and optional payment
        
        Returns:
            MCP response with result or payment requirements
        """
        method = request.get("method")
        params = request.get("params", {})
        payment_header = request.get("payment")
        
        # Handle tool listing
        if method == "list_tools":
            return self._list_tools_response()
        
        # Handle tool invocation
        if method == "invoke_tool":
            tool_name = params.get("tool")
            tool_params = params.get("params", {})
            
            if tool_name not in self.tools:
                return {
                    "error": {
                        "code": -32601,
                        "message": f"Tool not found: {tool_name}"
                    }
                }
            
            tool = self.tools[tool_name]
            
            # Check for payment
            if not payment_header:
                # Return payment requirements
                requirements = self.server.create_requirements(
                    price_usdc=tool.price_usdc,
                    resource=f"mcp://{tool.name}",
                    description=f"Payment for {tool.name}: {tool.description}"
                )
                
                return {
                    "error": {
                        "code": 402,
                        "message": "Payment Required",
                        "data": {
                            "requirements": json.loads(requirements.to_json())
                        }
                    }
                }
            
            # Verify payment
            requirements = self.server.create_requirements(
                price_usdc=tool.price_usdc,
                resource=f"mcp://{tool.name}",
                description=tool.description
            )
            
            verification = self.server.verify_payment(payment_header, requirements)
            
            if not verification["valid"]:
                return {
                    "error": {
                        "code": 402,
                        "message": "Invalid payment",
                        "data": {"reason": verification.get("error")}
                    }
                }
            
            # Execute tool
            try:
                result = await tool.handler(**tool_params)
                
                return {
                    "result": result,
                    "payment": {
                        "signature": verification.get("signature"),
                        "amount": tool.price_usdc
                    }
                }
            
            except Exception as e:
                logger.error(f"Tool execution failed: {e}")
                return {
                    "error": {
                        "code": -32603,
                        "message": "Internal error",
                        "data": {"error": str(e)}
                    }
                }
        
        # Unknown method
        return {
            "error": {
                "code": -32601,
                "message": f"Method not found: {method}"
            }
        }
    
    def _list_tools_response(self) -> Dict[str, Any]:
        """Generate response for list_tools request"""
        tools_list = []
        
        for name, tool in self.tools.items():
            tools_list.append({
                "name": name,
                "description": tool.description,
                "price_usdc": tool.price_usdc,
                "input_schema": tool.input_schema,
                "output_schema": tool.output_schema,
                "requires_payment": True
            })
        
        return {
            "result": {
                "tools": tools_list,
                "server": {
                    "name": self.name,
                    "network": self.network.value,
                    "wallet": self.wallet_address
                }
            }
        }
    
    def get_openapi_spec(self) -> Dict[str, Any]:
        """
        Generate OpenAPI specification for the MCP server
        
        This helps AI models understand available tools.
        """
        paths = {}
        
        for name, tool in self.tools.items():
            paths[f"/tools/{name}"] = {
                "post": {
                    "summary": tool.description,
                    "description": f"Requires ${tool.price_usdc} USDC payment",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": tool.input_schema or {"type": "object"}
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Success",
                            "content": {
                                "application/json": {
                                    "schema": tool.output_schema or {"type": "object"}
                                }
                            }
                        },
                        "402": {
                            "description": "Payment Required",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "requirements": {"type": "object"}
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "x-price-usdc": tool.price_usdc
                }
            }
        
        return {
            "openapi": "3.0.0",
            "info": {
                "title": self.name,
                "version": "1.0.0",
                "description": f"MCP server with x402 payments on {self.network.value}"
            },
            "servers": [
                {
                    "url": f"mcp://{self.wallet_address}",
                    "description": f"MCP server on {self.network.value}"
                }
            ],
            "paths": paths
        }


# Specialized MCP servers for common use cases
class DataMCPServer(MCPPaymentServer):
    """
    MCP server specialized for data access
    
    Example:
        >>> data_server = DataMCPServer(wallet_address="YOUR_ADDRESS")
        >>> 
        >>> # Register data sources
        >>> data_server.register_dataset(
        ...     name="market_data",
        ...     description="Real-time market data",
        ...     price_usdc=0.10,
        ...     data_source=market_data_api
        ... )
    """
    
    def __init__(self, wallet_address: str, network: Network = Network.DEVNET):
        super().__init__(wallet_address, network, "Data MCP Server")
        self.data_sources: Dict[str, Callable] = {}
    
    def register_dataset(
        self,
        name: str,
        description: str,
        price_usdc: float,
        data_source: Callable
    ):
        """Register a paid data source"""
        @self.tool(
            price_usdc=price_usdc,
            description=description,
            output_schema={"type": "object"}
        )
        async def fetch_data(**params):
            return await data_source(**params)
        
        # Rename the function to match dataset name
        fetch_data.__name__ = f"fetch_{name}"
        self.data_sources[name] = fetch_data


class AgentMCPServer(MCPPaymentServer):
    """
    MCP server for agent-to-agent services
    
    Enables agents to offer services to other agents for payment.
    
    Example:
        >>> agent_server = AgentMCPServer(
        ...     wallet_address="AGENT_ADDRESS",
        ...     agent_name="AnalysisAgent"
        ... )
        >>> 
        >>> @agent_server.service(price_usdc=0.50, description="Analyze document")
        >>> async def analyze_document(text: str) -> dict:
        ...     return {"summary": summarize(text), "sentiment": analyze_sentiment(text)}
    """
    
    def __init__(
        self,
        wallet_address: str,
        agent_name: str,
        network: Network = Network.DEVNET
    ):
        super().__init__(wallet_address, network, f"Agent: {agent_name}")
        self.agent_name = agent_name
    
    def service(self, price_usdc: float, description: str):
        """Register an agent service (alias for tool)"""
        return self.tool(price_usdc, description)
    
    async def handle_agent_request(
        self,
        from_agent: str,
        service: str,
        params: Dict[str, Any],
        payment: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Handle request from another agent
        
        Args:
            from_agent: Requesting agent identifier
            service: Service name
            params: Service parameters
            payment: Payment proof
        
        Returns:
            Service result or payment requirements
        """
        request = {
            "method": "invoke_tool",
            "params": {
                "tool": service,
                "params": params
            },
            "payment": payment,
            "metadata": {
                "from_agent": from_agent,
                "to_agent": self.agent_name
            }
        }
        
        response = await self.handle_request(request)
        
        # Log agent-to-agent transaction
        if "result" in response:
            logger.info(f"Agent {from_agent} used service {service} from {self.agent_name}")
        
        return response