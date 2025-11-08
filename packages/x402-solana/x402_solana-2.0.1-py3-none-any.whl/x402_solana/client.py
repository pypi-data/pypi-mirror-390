"""
x402 Client for Solana

Makes HTTP requests with automatic 402 payment handling.
"""

import time
import httpx
import asyncio
import logging
from typing import Optional, Dict, Any

from solana.rpc.async_api import AsyncClient
from solders.transaction import Transaction
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from spl.token.instructions import transfer_checked, TransferCheckedParams
from spl.token.client import Token
from spl.token.constants import TOKEN_PROGRAM_ID

from .types import (
    PaymentRequirements,
    PaymentPayload,
    PaymentReceipt,
    Network,
    usdc_to_lamports,
)

logger = logging.getLogger(__name__)


class X402Client:
    """
    Client for making x402 payments on Solana
    
    Automatically handles the 402 flow:
    1. Make request
    2. Receive 402 with payment requirements
    3. Create and send payment transaction
    4. Retry request with payment proof
    
    Example:
        >>> keypair = Keypair()
        >>> client = X402Client(keypair)
        >>> 
        >>> # Automatically pays if needed
        >>> response = await client.fetch(
        ...     "https://api.example.com/data",
        ...     max_price_usdc=0.01
        ... )
    """
    
    def __init__(
        self,
        keypair: Keypair,
        network: Network = Network.DEVNET,
        timeout: float = 30.0
    ):
        """
        Initialize x402 client
        
        Args:
            keypair: Solana keypair for signing transactions
            network: Solana network to use
            timeout: HTTP request timeout
        """
        self.keypair = keypair
        self.network = network
        self.http_client = httpx.AsyncClient(timeout=timeout)
        self.solana_client = AsyncClient(network.rpc_url())
        self.usdc_mint = Pubkey.from_string(network.usdc_mint())
        
        logger.info(f"X402 client initialized on {network.value}")
    
    async def fetch(
        self,
        url: str,
        max_price_usdc: float = 1.0,
        method: str = "GET",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Fetch a resource, automatically paying if required
        
        Args:
            url: Resource URL
            max_price_usdc: Maximum willing to pay in USDC
            method: HTTP method
            **kwargs: Additional request parameters
        
        Returns:
            Response data
        
        Raises:
            ValueError: If price exceeds max_price_usdc
            Exception: If payment or request fails
        """
        # Step 1: Try to fetch normally
        response = await self.http_client.request(method, url, **kwargs)
        
        # If not 402, return the response
        if response.status_code != 402:
            return response.json() if response.content else None
        
        # Step 2: Parse payment requirements
        requirements = PaymentRequirements.from_json(response.text)
        logger.info(f"Payment required: {requirements.to_usdc()} USDC")
        
        # Check price limit
        if requirements.to_usdc() > max_price_usdc:
            raise ValueError(
                f"Price {requirements.to_usdc()} USDC exceeds max {max_price_usdc} USDC"
            )
        
        # Step 3: Create and send payment
        payment_proof = await self._make_payment(requirements)
        
        # Step 4: Retry with payment proof
        headers = kwargs.get("headers", {})
        headers["X-PAYMENT"] = payment_proof.to_header()
        kwargs["headers"] = headers
        
        response = await self.http_client.request(method, url, **kwargs)
        
        if response.status_code == 200:
            logger.info("Payment successful!")
            
            # Extract receipt if provided
            receipt_header = response.headers.get("X-PAYMENT-RECEIPT")
            if receipt_header:
                logger.info(f"Receipt: {receipt_header[:50]}...")
            
            return response.json() if response.content else None
        else:
            raise Exception(f"Payment failed: {response.status_code} {response.text}")
    
    async def _make_payment(self, requirements: PaymentRequirements) -> PaymentPayload:
        """
        Create and send payment transaction on Solana
        
        Args:
            requirements: Payment requirements from server
        
        Returns:
            Payment proof to send in X-PAYMENT header
        """
        payer = self.keypair.pubkey()
        recipient = Pubkey.from_string(requirements.pay_to)
        
        # Get token accounts
        from spl.token.instructions import get_associated_token_address
        
        payer_token_account = get_associated_token_address(
            payer,
            self.usdc_mint
        )
        
        recipient_token_account = get_associated_token_address(
            recipient,
            self.usdc_mint
        )
        
        # Check if recipient token account exists, create if not
        account_info = await self.solana_client.get_account_info(recipient_token_account)
        
        instructions = []
        
        if account_info.value is None:
            # Need to create recipient's token account
            from spl.token.instructions import create_associated_token_account
            
            create_ix = create_associated_token_account(
                payer=payer,
                owner=recipient,
                mint=self.usdc_mint
            )
            instructions.append(create_ix)
            logger.info("Creating recipient token account")
        
        # Create transfer instruction
        transfer_ix = transfer_checked(
            TransferCheckedParams(
                program_id=TOKEN_PROGRAM_ID,
                source=payer_token_account,
                mint=self.usdc_mint,
                dest=recipient_token_account,
                owner=payer,
                amount=requirements.amount,
                decimals=6  # USDC has 6 decimals
            )
        )
        instructions.append(transfer_ix)
        
        # Build transaction
        recent_blockhash = await self.solana_client.get_latest_blockhash()
        
        transaction = Transaction()
        transaction.recent_blockhash = recent_blockhash.value.blockhash
        transaction.fee_payer = payer
        
        for ix in instructions:
            transaction.add(ix)
        
        # Sign and send
        transaction.sign(self.keypair)
        
        result = await self.solana_client.send_transaction(
            transaction,
            self.keypair
        )
        
        signature = str(result.value)
        logger.info(f"Transaction sent: {signature}")
        
        # Wait for confirmation
        await self._confirm_transaction(signature)
        
        # Create payment proof
        return PaymentPayload(
            signature=signature,
            nonce=requirements.nonce,
            from_address=str(payer),
            to_address=requirements.pay_to,
            amount=requirements.amount,
            timestamp=int(time.time())
        )
    
    async def _confirm_transaction(self, signature: str, max_retries: int = 30):
        """Wait for transaction confirmation"""
        for i in range(max_retries):
            response = await self.solana_client.get_signature_statuses([signature])
            
            if response.value and response.value[0]:
                status = response.value[0]
                if status.confirmation_status in ["confirmed", "finalized"]:
                    if status.err:
                        raise Exception(f"Transaction failed: {status.err}")
                    logger.info("Transaction confirmed")
                    return
            
            await asyncio.sleep(1)
        
        raise Exception("Transaction confirmation timeout")
    
    async def close(self):
        """Close client connections"""
        await self.http_client.aclose()
        await self.solana_client.close()