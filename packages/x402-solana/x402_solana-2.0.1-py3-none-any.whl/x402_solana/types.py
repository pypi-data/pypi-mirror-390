"""
x402 Protocol Types for Solana

Core types matching the x402 specification.
"""

from enum import Enum
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict
import json
import base64


class Network(str, Enum):
    """Supported Solana networks"""
    DEVNET = "solana-devnet"
    MAINNET = "solana-mainnet"
    
    def rpc_url(self) -> str:
        """Get RPC endpoint for network"""
        return (
            "https://api.mainnet-beta.solana.com"
            if self == Network.MAINNET
            else "https://api.devnet.solana.com"
        )
    
    def usdc_mint(self) -> str:
        """Get USDC mint address for network"""
        return (
            "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"  # Mainnet USDC
            if self == Network.MAINNET
            else "4zMMC9srt5Ri5X14GAgXhaHii3GnPAEERYPJgZJDncDU"  # Devnet USDC
        )


@dataclass
class PaymentRequirements:
    """
    Payment requirements returned in 402 response
    
    This is what the server sends to tell clients how to pay.
    """
    pay_to: str  # Solana address to pay
    amount: int  # Amount in lamports (USDC has 6 decimals)
    asset: str  # SPL token mint (usually USDC)
    network: str  # Network identifier
    nonce: str  # Unique nonce to prevent replay
    resource: str  # URL of the protected resource
    description: Optional[str] = None
    expires_at: Optional[int] = None  # Unix timestamp
    
    def to_json(self) -> str:
        """Serialize to JSON for 402 response body"""
        return json.dumps(asdict(self))
    
    @classmethod
    def from_json(cls, data: str) -> 'PaymentRequirements':
        """Parse from JSON response"""
        return cls(**json.loads(data))
    
    def to_usdc(self) -> float:
        """Convert lamports to USDC amount"""
        return self.amount / 1_000_000


@dataclass
class PaymentPayload:
    """
    Payment proof sent in X-PAYMENT header
    
    This proves the client made the payment.
    """
    signature: str  # Transaction signature
    nonce: str  # Nonce from requirements
    from_address: str  # Payer's address
    to_address: str  # Recipient's address
    amount: int  # Amount paid in lamports
    timestamp: int  # Unix timestamp
    
    def to_header(self) -> str:
        """Encode as base64 for X-PAYMENT header"""
        data = asdict(self)
        json_str = json.dumps(data)
        return base64.b64encode(json_str.encode()).decode()
    
    @classmethod
    def from_header(cls, header: str) -> 'PaymentPayload':
        """Parse from X-PAYMENT header"""
        decoded = base64.b64decode(header)
        data = json.loads(decoded)
        return cls(**data)


@dataclass
class PaymentReceipt:
    """
    Receipt returned in X-PAYMENT-RECEIPT header
    
    Optional confirmation from server after successful payment.
    """
    signature: str
    amount: int
    timestamp: int
    receipt_id: str
    resource: str
    
    def to_header(self) -> str:
        """Encode for response header"""
        return base64.b64encode(json.dumps(asdict(self)).encode()).decode()


# Helper functions
def usdc_to_lamports(usdc: float) -> int:
    """Convert USDC amount to lamports (6 decimals)"""
    return int(usdc * 1_000_000)


def lamports_to_usdc(lamports: int) -> float:
    """Convert lamports to USDC amount"""
    return lamports / 1_000_000