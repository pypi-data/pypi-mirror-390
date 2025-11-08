"""
x402-solana: Complete x402 Protocol Implementation for Solana

Dominant SDK for all 5 hackathon categories:
- Agent Identity & Reputation
- Agent-to-Agent Marketplace  
- MCP Servers
- Infrastructure & SDKs
- Practical AI Applications

Simple HTTP 402 payments for APIs and AI agents on Solana.
With CDP integration for multi-chain support.
"""

__version__ = "2.0.0"

# Core client for making payments
from .client import X402Client

# CDP-integrated client (if x402 package installed)
try:
    from .client_cdp import (
        X402UniversalClient,
        create_cdp_client,
        create_native_client,
        create_hybrid_client,
        PaymentMode,
    )
    CDP_AVAILABLE = True
except ImportError:
    CDP_AVAILABLE = False

# Server utilities for accepting payments
from .server import (
    X402Server,
    require_payment,
    verify_payment,
)

# Agent with budget management
from .agent import (
    PaymentAgent,
    BudgetManager,
    AgentCoordinator,
)

# Agent Identity & Reputation (Category 1)
from .identity import (
    AgentIdentity,
    AgentRegistry,
    ReputationScore,
    IdentityVerifier,
)

# Agent-to-Agent Marketplace (Category 2)
from .marketplace import (
    A2AMarketplace,
    ServiceListing,
    ServiceCategory,
    ServiceOrchestrator,
    AgentDAO,
)

# MCP Servers (Category 3)
from .mcp import (
    MCPPaymentServer,
    MCPTool,
    DataMCPServer,
    AgentMCPServer,
)

# Infrastructure (Category 4)
from .infrastructure import (
    PaymentRouter,
    PaymentCache,
    PaymentPool,
    BatchProcessor,
    MetricsCollector,
    WebhookManager,
    RateLimiter,
)

# AI Tools & Applications (Category 5)
from .ai_tools import (
    AIToolkit,
    AIAgentFramework,
    AIAssistant,
    AIDataAnalyst,
    AIContentCreator,
    AITrader,
)

# Essential types
from .types import (
    PaymentRequirements,
    PaymentPayload,
    PaymentReceipt,
    Network,
)

# Wallet utilities
from .wallet import (
    create_wallet,
    load_wallet,
    save_wallet,
)

__all__ = [
    # Core
    "X402Client",
    "X402Server",
    "require_payment",
    "verify_payment",
    
    # CDP Integration
    "X402UniversalClient",
    "create_cdp_client",
    "create_native_client",
    "create_hybrid_client",
    "PaymentMode",
    
    # Agents
    "PaymentAgent",
    "BudgetManager",
    "AgentCoordinator",
    
    # Identity & Reputation
    "AgentIdentity",
    "AgentRegistry",
    "ReputationScore",
    "IdentityVerifier",
    
    # Marketplace
    "A2AMarketplace",
    "ServiceListing",
    "ServiceCategory",
    "ServiceOrchestrator",
    "AgentDAO",
    
    # MCP
    "MCPPaymentServer",
    "MCPTool",
    "DataMCPServer",
    "AgentMCPServer",
    
    # Infrastructure
    "PaymentRouter",
    "PaymentCache",
    "PaymentPool",
    "BatchProcessor",
    "MetricsCollector",
    "WebhookManager",
    "RateLimiter",
    
    # AI Tools
    "AIToolkit",
    "AIAgentFramework",
    "AIAssistant",
    "AIDataAnalyst",
    "AIContentCreator",
    "AITrader",
    
    # Types
    "PaymentRequirements",
    "PaymentPayload",
    "PaymentReceipt",
    "Network",
    
    # Wallet
    "create_wallet",
    "load_wallet",
    "save_wallet",
]