"""
Tests for X402Client
"""

import pytest
import httpx
from unittest.mock import AsyncMock, Mock
from x402_solana.client import X402Client
from x402_solana.types import Network, PaymentPayload, PaymentRequirements, usdc_to_lamports

TEST_URL = "http://api.test/resource"


@pytest.mark.asyncio
async def test_client_initialization(client_keypair, mock_solana_async_client, mock_httpx_client):
    """Test X402Client initializes correctly."""
    client = X402Client(client_keypair)
    assert str(client.keypair.pubkey()) == str(client_keypair.pubkey())
    assert client.network == Network.DEVNET
    await client.close()
    mock_httpx_client.aclose.assert_called_once()
    mock_solana_async_client.close.assert_called_once()


@pytest.mark.asyncio
async def test_fetch_success_no_payment(client_keypair, mock_httpx_client, mock_solana_async_client):
    """Test successful fetch when no 402 is returned."""
    mock_response = Mock(status_code=200, content=b'{"data": "free"}')
    mock_response.json = Mock(return_value={"data": "free"})
    mock_httpx_client.request = AsyncMock(return_value=mock_response)
    
    client = X402Client(client_keypair)
    result = await client.fetch("http://test.url", max_price_usdc=0.1)
    
    assert result == {"data": "free"}
    mock_httpx_client.request.assert_called_once()


@pytest.mark.asyncio
async def test_fetch_402_payment_flow(client_keypair, mock_httpx_client, mock_solana_async_client, mock_requirements):
    """Test the full 4-step payment flow (402 -> Pay -> Retry -> 200)."""
    
    # Step 1: Mock initial 402 response
    mock_402_response = Mock(status_code=402, text=mock_requirements.to_json())
    
    # Step 2: Mock successful 200 response on retry
    mock_200_response = Mock(status_code=200, content=b'{"data": "paid_content"}')
    mock_200_response.json = Mock(return_value={"data": "paid_content"})
    mock_200_response.headers = {"X-PAYMENT-RECEIPT": "receipt_data"}
    
    # Setup mock to return 402 first, then 200
    mock_httpx_client.request = AsyncMock(side_effect=[mock_402_response, mock_200_response])
    
    client = X402Client(client_keypair)
    result = await client.fetch(TEST_URL, max_price_usdc=0.1)
    
    # Assertions
    assert result == {"data": "paid_content"}
    
    # 1. Assert payment transaction was sent and confirmed
    mock_solana_async_client.send_transaction.assert_called_once()
    mock_solana_async_client.get_signature_statuses.assert_called_once()

    # 2. Assert retry request included X-PAYMENT header
    assert mock_httpx_client.request.call_count == 2
    
    # Verify X-PAYMENT header was present in the second call
    retry_call_args = mock_httpx_client.request.call_args_list[1]
    headers = retry_call_args[1].get('headers', {})
    payment_header = headers.get('X-PAYMENT')
    
    assert payment_header is not None
    assert isinstance(payment_header, str)
    
    # Check if header can be decoded into a PaymentPayload
    payload = PaymentPayload.from_header(payment_header)
    assert payload.nonce == mock_requirements.nonce
    assert payload.to_address == mock_requirements.pay_to


@pytest.mark.asyncio
async def test_fetch_fails_on_price_exceeds_max(client_keypair, mock_httpx_client, mock_solana_async_client, mock_requirements):
    """Test fetch fails if required price is > max_price_usdc."""
    # Create requirement with price higher than agent's max
    high_price_reqs = PaymentRequirements(
        pay_to=mock_requirements.pay_to,
        amount=usdc_to_lamports(5.0),  # $5.00
        asset=mock_requirements.asset,
        network=mock_requirements.network,
        nonce=mock_requirements.nonce,
        resource=mock_requirements.resource,
        description=mock_requirements.description,
        expires_at=mock_requirements.expires_at
    )
    
    mock_402_response = Mock(status_code=402, text=high_price_reqs.to_json())
    mock_httpx_client.request = AsyncMock(return_value=mock_402_response)

    client = X402Client(client_keypair)

    with pytest.raises(ValueError, match="Price 5.0 USDC exceeds max 1.0 USDC"):
        await client.fetch(TEST_URL, max_price_usdc=1.0)
    
    # Ensure send_transaction was never called
    assert not mock_solana_async_client.send_transaction.called