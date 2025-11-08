"""
x402 Client with CDP Integration

Supports both native Solana transactions and CDP-facilitated payments.
"""

import time
import httpx
import asyncio
import logging
from typing import Optional, Dict, Any, Union, TYPE_CHECKING
from enum import Enum

from .types import (
    PaymentRequirements,
    PaymentPayload,
    PaymentReceipt,
    Network,
    usdc_to_lamports,
)

# Type hints for optional dependencies
if TYPE_CHECKING:
    from solders.keypair import Keypair

logger = logging.getLogger(__name__)


# CDP Integration
try:
    # Try to import official x402 CDP SDK
    from x402 import Client as CDPClient
    CDP_AVAILABLE = True
except ImportError:
    CDP_AVAILABLE = False
    logger.info("Official x402 CDP SDK not installed. Install with: pip install x402")


class PaymentMode(str, Enum):
    """Payment execution modes"""
    NATIVE = "native"  # Direct Solana transaction
    CDP = "cdp"        # CDP-facilitated payment


class X402UniversalClient:
    """
    Universal x402 client supporting multiple payment modes:
    1. Native Solana transactions (direct, no facilitator)
    2. CDP-facilitated payments (KYC/compliance, multi-chain)
    
    Automatically selects the best mode based on requirements.
    """
    
    def __init__(
        self,
        # For native mode
        keypair: Optional['Keypair'] = None,
        
        # For CDP mode
        cdp_api_key: Optional[str] = None,
        cdp_private_key: Optional[str] = None,
        
        # Common settings
        network: Network = Network.DEVNET,
        timeout: float = 30.0,
        preferred_mode: PaymentMode = PaymentMode.CDP
    ):
        """
        Initialize universal client
        
        Args:
            keypair: Solana keypair for native transactions
            cdp_api_key: CDP API key for facilitated payments
            cdp_private_key: CDP private key for signing
            network: Target network
            timeout: HTTP timeout
            preferred_mode: Preferred payment mode when both available
        """
        self.network = network
        self.timeout = timeout
        self.preferred_mode = preferred_mode
        self.http_client = httpx.AsyncClient(timeout=timeout)
        
        # Initialize native client if keypair provided
        self.native_client = None
        if keypair:
            from .client import X402Client
            self.native_client = X402Client(keypair, network, timeout)
            logger.info("Native Solana client initialized")
        
        # Initialize CDP client if credentials provided
        self.cdp_client = None
        if cdp_api_key and cdp_private_key and CDP_AVAILABLE:
            self.cdp_client = CDPClient(
                api_key_name=cdp_api_key,
                private_key=cdp_private_key
            )
            logger.info("CDP client initialized")
        elif cdp_api_key and not CDP_AVAILABLE:
            logger.warning("CDP credentials provided but x402 package not installed")
        
        if not self.native_client and not self.cdp_client:
            raise ValueError("Must provide either keypair or CDP credentials")
    
    async def fetch(
        self,
        url: str,
        max_price_usdc: float = 1.0,
        method: str = "GET",
        force_mode: Optional[PaymentMode] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Fetch a resource with automatic 402 payment handling
        
        Intelligently routes payments through the best available method:
        - CDP for compliance/multi-chain requirements
        - Native for direct Solana transactions
        
        Args:
            url: Resource URL
            max_price_usdc: Maximum willing to pay
            method: HTTP method
            force_mode: Force specific payment mode
            **kwargs: Additional request parameters
        
        Returns:
            Response data
        """
        # Step 1: Try initial request
        response = await self.http_client.request(method, url, **kwargs)
        
        if response.status_code != 402:
            return response.json() if response.content else None
        
        # Step 2: Parse payment requirements
        requirements = PaymentRequirements.from_json(response.text)
        logger.info(f"Payment required: {requirements.to_usdc()} USDC on {requirements.network}")
        
        # Step 3: Check price
        if requirements.to_usdc() > max_price_usdc:
            raise ValueError(
                f"Price {requirements.to_usdc()} USDC exceeds max {max_price_usdc} USDC"
            )
        
        # Step 4: Determine payment mode
        mode = self._select_payment_mode(requirements, force_mode)
        logger.info(f"Using payment mode: {mode}")
        
        # Step 5: Execute payment
        if mode == PaymentMode.CDP:
            payment_proof = await self._make_cdp_payment(requirements)
        else:
            payment_proof = await self._make_native_payment(requirements)
        
        # Step 6: Retry with payment proof
        headers = kwargs.get("headers", {})
        headers["X-PAYMENT"] = payment_proof.to_header()
        kwargs["headers"] = headers
        
        response = await self.http_client.request(method, url, **kwargs)
        
        if response.status_code == 200:
            logger.info("Payment successful!")
            
            # Extract receipt if provided
            receipt_header = response.headers.get("X-PAYMENT-RECEIPT")
            if receipt_header:
                logger.info("Receipt received")
            
            return response.json() if response.content else None
        else:
            raise Exception(f"Payment failed: {response.status_code} {response.text}")
    
    def _select_payment_mode(
        self,
        requirements: PaymentRequirements,
        force_mode: Optional[PaymentMode] = None
    ) -> PaymentMode:
        """
        Select the best payment mode based on requirements
        
        Decision logic:
        1. If mode forced, use it (if available)
        2. If requirements specify facilitator, use CDP
        3. If multi-chain network, use CDP
        4. Otherwise use preferred mode
        """
        if force_mode:
            if force_mode == PaymentMode.CDP and not self.cdp_client:
                raise ValueError("CDP mode requested but not available")
            if force_mode == PaymentMode.NATIVE and not self.native_client:
                raise ValueError("Native mode requested but not available")
            return force_mode
        
        # Check if requirements indicate facilitator needed
        if hasattr(requirements, 'facilitator') and requirements.facilitator:
            if not self.cdp_client:
                raise ValueError("Server requires facilitator but CDP not configured")
            return PaymentMode.CDP
        
        # Check network - CDP supports multi-chain
        network_str = requirements.network
        if "base" in network_str or "ethereum" in network_str:
            if not self.cdp_client:
                raise ValueError(f"Network {network_str} requires CDP client")
            return PaymentMode.CDP
        
        # Use preferred mode if available
        if self.preferred_mode == PaymentMode.CDP and self.cdp_client:
            return PaymentMode.CDP
        elif self.preferred_mode == PaymentMode.NATIVE and self.native_client:
            return PaymentMode.NATIVE
        
        # Use whatever is available
        if self.cdp_client:
            return PaymentMode.CDP
        elif self.native_client:
            return PaymentMode.NATIVE
        else:
            raise ValueError("No payment method available")
    
    async def _make_cdp_payment(self, requirements: PaymentRequirements) -> PaymentPayload:
        """
        Make payment through CDP facilitator
        
        CDP handles:
        - Multi-chain support (Solana, Base, Ethereum)
        - KYC/compliance checks
        - Gas fee abstraction
        - Transaction signing
        """
        if not self.cdp_client:
            raise ValueError("CDP client not initialized")
        
        logger.info(f"Making CDP payment to {requirements.pay_to}")
        
        try:
            # Use official CDP SDK to create payment
            # CDP SDK handles all the complexity internally
            result = await self.cdp_client.pay(
                to=requirements.pay_to,
                amount=requirements.to_usdc(),
                asset="USDC",
                network=requirements.network,
                nonce=requirements.nonce,
                memo=requirements.description
            )
            
            # Convert CDP response to our PaymentPayload format
            return PaymentPayload(
                signature=result.signature,
                nonce=requirements.nonce,
                from_address=result.from_address,
                to_address=requirements.pay_to,
                amount=requirements.amount,
                timestamp=int(time.time())
            )
            
        except Exception as e:
            logger.error(f"CDP payment failed: {e}")
            raise
    
    async def _make_native_payment(self, requirements: PaymentRequirements) -> PaymentPayload:
        """
        Make native Solana payment (no facilitator)
        
        Direct on-chain transaction for:
        - No KYC requirements
        - Solana-only
        - User controls keys
        """
        if not self.native_client:
            raise ValueError("Native client not initialized")
        
        logger.info(f"Making native Solana payment to {requirements.pay_to}")
        
        # Delegate to original native client
        return await self.native_client._make_payment(requirements)
    
    async def close(self):
        """Close client connections"""
        await self.http_client.aclose()
        if self.native_client:
            await self.native_client.close()


# Convenience functions for different use cases

def create_cdp_client(
    api_key: str,
    private_key: str,
    network: Network = Network.MAINNET
) -> X402UniversalClient:
    """
    Create a CDP-only client for production use
    
    Best for:
    - Production applications
    - Multi-chain support needed
    - Compliance requirements
    
    Args:
        api_key: CDP API key from dashboard.coinbase.com/developer
        private_key: CDP private key
        network: Target network
    
    Example:
        >>> client = create_cdp_client(
        ...     api_key="organizations/xxx/apiKeys/yyy",
        ...     private_key="-----BEGIN EC PRIVATE KEY-----..."
        ... )
        >>> data = await client.fetch(url, max_price_usdc=0.01)
    """
    return X402UniversalClient(
        cdp_api_key=api_key,
        cdp_private_key=private_key,
        network=network,
        preferred_mode=PaymentMode.CDP
    )


def create_native_client(
    keypair: Any,  # Keypair from solders
    network: Network = Network.DEVNET
) -> X402UniversalClient:
    """
    Create a native Solana-only client
    
    Best for:
    - Development/testing
    - User-controlled wallets
    - No facilitator needed
    
    Args:
        keypair: Solana keypair (from solders.keypair.Keypair)
        network: Solana network
    
    Example:
        >>> from solders.keypair import Keypair
        >>> keypair = Keypair()
        >>> client = create_native_client(keypair)
        >>> data = await client.fetch(url, max_price_usdc=0.01)
    """
    return X402UniversalClient(
        keypair=keypair,
        network=network,
        preferred_mode=PaymentMode.NATIVE
    )


def create_hybrid_client(
    keypair: Any,  # Keypair from solders
    cdp_api_key: str,
    cdp_private_key: str,
    network: Network = Network.MAINNET
) -> X402UniversalClient:
    """
    Create a hybrid client supporting both modes
    
    Best for:
    - Maximum flexibility
    - Fallback options
    - Multi-environment support
    
    The client will intelligently choose between CDP and native
    based on the payment requirements.
    """
    return X402UniversalClient(
        keypair=keypair,
        cdp_api_key=cdp_api_key,
        cdp_private_key=cdp_private_key,
        network=network,
        preferred_mode=PaymentMode.CDP  # Prefer CDP for compliance
    )