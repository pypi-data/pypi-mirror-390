"""
x402 Server utilities for Solana

Accept payments in your API with simple decorators and utilities.
"""

import secrets
import sqlite3
import time
import logging
from typing import Optional, Dict, Any, Callable
from functools import wraps

from solana.rpc.api import Client
from solders.pubkey import Pubkey

from .types import (
    PaymentRequirements,
    PaymentPayload,
    PaymentReceipt,
    Network,
    usdc_to_lamports,
)

logger = logging.getLogger(__name__)


class NonceStore:
    """
    Persistent nonce storage to prevent replay attacks
    
    Uses SQLite to track used nonces across server restarts.
    """
    
    def __init__(self, db_path: str = "nonces.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize the nonce database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS nonces (
                nonce TEXT PRIMARY KEY,
                signature TEXT NOT NULL,
                timestamp INTEGER NOT NULL,
                created_at INTEGER DEFAULT (strftime('%s', 'now'))
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_created_at ON nonces(created_at)
        """)
        
        conn.commit()
        conn.close()
    
    def is_used(self, nonce: str) -> bool:
        """Check if a nonce has been used"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT 1 FROM nonces WHERE nonce = ?", (nonce,))
        result = cursor.fetchone()
        
        conn.close()
        return result is not None
    
    def mark_used(self, nonce: str, signature: str, timestamp: int):
        """Mark a nonce as used"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "INSERT INTO nonces (nonce, signature, timestamp) VALUES (?, ?, ?)",
                (nonce, signature, timestamp)
            )
            conn.commit()
        except sqlite3.IntegrityError:
            # Nonce already exists
            pass
        finally:
            conn.close()
    
    def cleanup_old(self, older_than_hours: int = 24) -> int:
        """Remove old nonces to prevent database growth"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff = int(time.time()) - (older_than_hours * 3600)
        
        cursor.execute("DELETE FROM nonces WHERE created_at < ?", (cutoff,))
        deleted = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        return deleted


class X402Server:
    """
    Server-side x402 payment handling
    
    Verifies payments and manages payment requirements.
    
    Example:
        >>> server = X402Server(
        ...     wallet_address="YOUR_SOLANA_ADDRESS",
        ...     network=Network.DEVNET
        ... )
        >>> 
        >>> # Create payment requirements
        >>> requirements = server.create_requirements(
        ...     price_usdc=0.01,
        ...     resource="/api/data",
        ...     description="Premium data access"
        ... )
    """
    
    def __init__(
        self,
        wallet_address: str,
        network: Network = Network.DEVNET,
        nonce_db_path: str = "nonces.db"
    ):
        """
        Initialize payment server
        
        Args:
            wallet_address: Your Solana address to receive payments
            network: Solana network
            nonce_db_path: Path to nonce database
        """
        self.wallet_address = wallet_address
        self.network = network
        self.usdc_mint = network.usdc_mint()
        self.nonce_store = NonceStore(nonce_db_path)
        
        # Solana client for verification
        self.solana_client = Client(network.rpc_url())
        
        logger.info(f"X402 server initialized for {wallet_address} on {network.value}")
    
    def create_requirements(
        self,
        price_usdc: float,
        resource: str,
        description: Optional[str] = None,
        expires_in_seconds: int = 300
    ) -> PaymentRequirements:
        """
        Create payment requirements for a resource
        
        Args:
            price_usdc: Price in USDC
            resource: URL of the protected resource
            description: Human-readable description
            expires_in_seconds: How long the requirements are valid
        
        Returns:
            PaymentRequirements to send in 402 response
        """
        nonce = secrets.token_urlsafe(32)
        
        return PaymentRequirements(
            pay_to=self.wallet_address,
            amount=usdc_to_lamports(price_usdc),
            asset=self.usdc_mint,
            network=self.network.value,
            nonce=nonce,
            resource=resource,
            description=description,
            expires_at=int(time.time()) + expires_in_seconds
        )
    
    def verify_payment(
        self,
        payment_header: str,
        requirements: PaymentRequirements
    ) -> Dict[str, Any]:
        """
        Verify a payment proof
        
        Args:
            payment_header: X-PAYMENT header value
            requirements: Original payment requirements
        
        Returns:
            Dict with 'valid' (bool) and optional 'error' (str)
        """
        try:
            # Parse payment proof
            payment = PaymentPayload.from_header(payment_header)
            
            # Check nonce
            if payment.nonce != requirements.nonce:
                return {"valid": False, "error": "Invalid nonce"}
            
            # Check for replay attack
            if self.nonce_store.is_used(payment.nonce):
                return {"valid": False, "error": "Nonce already used (replay attack)"}
            
            # Check recipient
            if payment.to_address != self.wallet_address:
                return {"valid": False, "error": "Incorrect recipient"}
            
            # Check amount
            if payment.amount < requirements.amount:
                return {"valid": False, "error": "Insufficient payment"}
            
            # Verify transaction on-chain
            try:
                tx = self.solana_client.get_transaction(
                    payment.signature,
                    encoding="json",
                    max_supported_transaction_version=0
                )
                
                if not tx.value:
                    return {"valid": False, "error": "Transaction not found"}
                
                # Transaction exists and is confirmed
                # Mark nonce as used
                self.nonce_store.mark_used(
                    payment.nonce,
                    payment.signature,
                    payment.timestamp
                )
                
                return {"valid": True, "signature": payment.signature}
            
            except Exception as e:
                return {"valid": False, "error": f"Failed to verify transaction: {e}"}
        
        except Exception as e:
            return {"valid": False, "error": f"Invalid payment header: {e}"}
    
    def create_receipt(
        self,
        payment: PaymentPayload,
        resource: str
    ) -> PaymentReceipt:
        """
        Create a payment receipt
        
        Args:
            payment: Verified payment
            resource: Resource that was paid for
        
        Returns:
            Receipt to send in response
        """
        return PaymentReceipt(
            signature=payment.signature,
            amount=payment.amount,
            timestamp=payment.timestamp,
            receipt_id=secrets.token_urlsafe(16),
            resource=resource
        )
    
    def cleanup_nonces(self) -> int:
        """Clean up old nonces (run periodically)"""
        return self.nonce_store.cleanup_old()


def require_payment(
    price_usdc: float,
    wallet_address: str,
    network: Network = Network.DEVNET,
    description: Optional[str] = None
):
    """
    Decorator for FastAPI/Flask endpoints requiring payment
    
    Example:
        >>> from fastapi import FastAPI, Request, Response
        >>> app = FastAPI()
        >>> 
        >>> @app.get("/api/data")
        >>> @require_payment(price_usdc=0.01, wallet_address="YOUR_ADDRESS")
        >>> async def get_data(request: Request, response: Response):
        ...     return {"data": "premium content"}
    """
    def decorator(func: Callable) -> Callable:
        server = X402Server(wallet_address, network)
        
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Find request and response objects
            request = None
            response = None
            
            for arg in args:
                if hasattr(arg, "headers"):
                    request = arg
                if hasattr(arg, "status_code"):
                    response = arg
            
            for arg in kwargs.values():
                if hasattr(arg, "headers"):
                    request = arg
                if hasattr(arg, "status_code"):
                    response = arg
            
            if not request:
                raise ValueError("No request object found")
            
            # Check for payment
            payment_header = request.headers.get("X-PAYMENT")
            
            if not payment_header:
                # Return 402 with requirements
                resource = str(request.url) if hasattr(request, "url") else "unknown"
                requirements = server.create_requirements(
                    price_usdc=price_usdc,
                    resource=resource,
                    description=description
                )
                
                if response:
                    response.status_code = 402
                    return requirements.to_json()
                else:
                    # For frameworks without response object
                    from fastapi import Response
                    return Response(
                        content=requirements.to_json(),
                        status_code=402,
                        media_type="application/json"
                    )
            
            # Verify payment
            resource = str(request.url) if hasattr(request, "url") else "unknown"
            requirements = server.create_requirements(
                price_usdc=price_usdc,
                resource=resource,
                description=description
            )
            
            verification = server.verify_payment(payment_header, requirements)
            
            if not verification["valid"]:
                if response:
                    response.status_code = 400
                    return {"error": verification.get("error", "Invalid payment")}
                else:
                    from fastapi import Response
                    return Response(
                        content={"error": verification.get("error")},
                        status_code=400,
                        media_type="application/json"
                    )
            
            # Payment valid, execute original function
            result = await func(*args, **kwargs)
            
            # Add receipt to response
            if response and payment_header:
                payment = PaymentPayload.from_header(payment_header)
                receipt = server.create_receipt(payment, resource)
                response.headers["X-PAYMENT-RECEIPT"] = receipt.to_header()
            
            return result
        
        return wrapper
    return decorator


def verify_payment(
    payment_header: str,
    wallet_address: str,
    price_usdc: float,
    network: Network = Network.DEVNET
) -> bool:
    """
    Simple payment verification utility
    
    Args:
        payment_header: X-PAYMENT header value
        wallet_address: Expected recipient
        price_usdc: Expected price
        network: Solana network
    
    Returns:
        True if payment is valid
    """
    server = X402Server(wallet_address, network)
    
    requirements = server.create_requirements(
        price_usdc=price_usdc,
        resource="verification",
        description="Payment verification"
    )
    
    result = server.verify_payment(payment_header, requirements)
    return result["valid"]