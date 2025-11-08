# x402-solana: Complete x402 Protocol Implementation for Solana

**Version 2.0.0**

The **x402-solana** SDK provides a dominant, end-to-end implementation of the HTTP 402 Payment Required protocol, enabling seamless, autonomous, and instant payments on the **Solana** blockchain using **USDC**.

This library is designed for both clients (autonomous agents) that need to pay for resources and servers (APIs/services) that need to monetize their endpoints.

## ✨ Features and Hackathon Category Coverage

The SDK is structured to address all five hackathon categories:

| Category | Component | Description |
| :--- | :--- | :--- |
| **1. Agent Identity & Reputation** | `AgentRegistry`, `IdentityVerifier` | Decentralized identity and reputation scoring for agents using Solana wallet as the root of trust. |
| **2. Agent-to-Agent Marketplace** | `A2AMarketplace`, `ServiceOrchestrator` | Advanced P2P marketplace for agents to discover, request, and trade services with automatic payment handling. |
| **3. MCP Servers** | `MCPPaymentServer`, `AgentMCPServer` | Model Context Protocol integration, allowing AI models (e.g., GPT, Claude) to use paid tools and services autonomously. |
| **4. SDKs & Infrastructure** | `PaymentRouter`, `PaymentCache`, `BatchProcessor` | High-performance infrastructure components for routing, caching, and batching x402 payments. |
| **5. Practical AI Applications** | `AIToolkit`, `AIAssistant`, `AITrader` | Specialized AI agent frameworks built on the core protocol, demonstrating real-world payment use cases. |

## 🚀 Quick Installation

```bash
pip install x402-solana
# For optional multi-chain support via CDP (Coinbase Developer Platform)
pip install x402-solana[cdp]