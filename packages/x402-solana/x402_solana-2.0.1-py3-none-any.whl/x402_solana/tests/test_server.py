"""
Tests for X402Server
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from x402_solana.server import X402Server, NonceStore, require_payment
from x402_solana.types import PaymentRequirements, PaymentPayload, usdc_to_lamports, Network

TEST_NONCE = "test_unique_nonce_123"
TEST_RECEIVER_ADDRESS = "SomeValidSolanaAddress123"


# --- NonceStore Tests ---

def test_noncestore_is_used_miss(mock_sqlite_connect):
    """Test is_used returns False when nonce is new."""
    mock_cursor = mock_sqlite_connect.return_value.cursor.return_value
    mock_cursor.fetchone.return_value = None
    
    store = NonceStore()
    assert store.is_used(TEST_NONCE) is False


def test_noncestore_is_used_hit(mock_sqlite_connect):
    """Test is_used returns True when nonce is used."""
    mock_cursor = mock_sqlite_connect.return_value.cursor.return_value
    mock_cursor.fetchone.return_value = (1,)
    
    store = NonceStore()
    assert store.is_used(TEST_NONCE) is True


def test_noncestore_mark_used(mock_sqlite_connect):
    """Test marking a nonce as used."""
    store = NonceStore()
    store.mark_used(TEST_NONCE, "sig123", 1234567890)
    
    # Verify insert was called
    mock_cursor = mock_sqlite_connect.return_value.cursor.return_value
    assert mock_cursor.execute.called


# --- X402Server Tests ---

@pytest.mark.parametrize("amount_usdc, expected_valid", [
    (0.01, True),  # Exact match
    (0.02, True),  # Overpayment
    (0.009, False) # Underpayment
])
def test_verify_payment_amount_check(
    mock_solana_sync_client, 
    mock_sqlite_connect,
    server_address, 
    amount_usdc, 
    expected_valid
):
    """Test payment verification checks for sufficient amount."""
    server = X402Server(server_address)
    
    # Create requirements
    requirements = server.create_requirements(
        price_usdc=0.01,
        resource="/test"
    )
    
    # Create payload with test amount
    payment_payload = PaymentPayload(
        signature="test_sig",
        nonce=requirements.nonce,
        from_address="payer_address",
        to_address=server_address,
        amount=usdc_to_lamports(amount_usdc),
        timestamp=1234567890
    )
    
    result = server.verify_payment(payment_payload.to_header(), requirements)
    assert result['valid'] == expected_valid


def test_verify_payment_nonce_mismatch(
    mock_solana_sync_client,
    mock_sqlite_connect,
    server_address
):
    """Test verification fails if nonce in payload doesn't match requirement."""
    server = X402Server(server_address)
    
    requirements = server.create_requirements(
        price_usdc=0.01,
        resource="/test"
    )
    
    # Create payload with different nonce
    payment_payload = PaymentPayload(
        signature="test_sig",
        nonce="wrong_nonce",
        from_address="payer_address",
        to_address=server_address,
        amount=usdc_to_lamports(0.01),
        timestamp=1234567890
    )
    
    result = server.verify_payment(payment_payload.to_header(), requirements)
    assert result['valid'] is False
    assert "Invalid nonce" in result['error']


def test_verify_payment_replay_attack(
    mock_solana_sync_client,
    mock_sqlite_connect,
    server_address
):
    """Test verification fails due to nonce replay (security check)."""
    # Setup mock to indicate nonce is already used
    mock_cursor = mock_sqlite_connect.return_value.cursor.return_value
    mock_cursor.fetchone.return_value = (1,)  # Nonce exists
    
    server = X402Server(server_address)
    
    requirements = server.create_requirements(
        price_usdc=0.01,
        resource="/test"
    )
    
    payment_payload = PaymentPayload(
        signature="test_sig",
        nonce=requirements.nonce,
        from_address="payer_address",
        to_address=server_address,
        amount=usdc_to_lamports(0.01),
        timestamp=1234567890
    )
    
    result = server.verify_payment(payment_payload.to_header(), requirements)
    assert result['valid'] is False
    assert "replay attack" in result['error']


def test_create_requirements_data(mock_sqlite_connect, server_address):
    """Test requirements are created correctly with lamports."""
    server = X402Server(server_address)
    reqs = server.create_requirements(
        price_usdc=0.05,
        resource="/api/test"
    )
    assert reqs.pay_to == server_address
    assert reqs.amount == 50000  # 0.05 USDC in lamports
    assert len(reqs.nonce) > 16  # Nonce should be long and random
    assert reqs.resource == "/api/test"


def test_cleanup_nonces(mock_sqlite_connect, server_address):
    """Test nonce cleanup functionality."""
    mock_cursor = mock_sqlite_connect.return_value.cursor.return_value
    mock_cursor.rowcount = 5
    
    server = X402Server(server_address)
    deleted = server.cleanup_nonces()
    
    assert deleted == 5
    assert mock_cursor.execute.called


# --- Decorator Tests ---

@pytest.mark.asyncio
async def test_require_payment_returns_402(mock_sqlite_connect):
    """Test the decorator returns 402 with requirements when no payment is present."""
    from fastapi import Request
    
    # Mock FastAPI Request
    mock_request = Mock(spec=Request)
    mock_request.headers = Mock()
    mock_request.headers.get = Mock(return_value=None)
    mock_request.url = "http://test/url"
    
    # Mock Response
    mock_response = Mock()
    mock_response.status_code = 200
    
    # Create decorated function
    @require_payment(price_usdc=0.1, wallet_address=TEST_RECEIVER_ADDRESS)
    async def protected_endpoint(request: Request, response: Mock):
        return {"data": "protected"}
    
    # Call the endpoint
    result = await protected_endpoint(request=mock_request, response=mock_response)
    
    # Assert 402 was set
    assert mock_response.status_code == 402
    
    # Result should be JSON with payment requirements
    assert 'pay_to' in result or isinstance(result, str)


@pytest.mark.asyncio  
async def test_require_payment_successful_payment(mock_sqlite_connect, mock_solana_sync_client):
    """Test decorator allows access with valid payment."""
    from fastapi import Request
    
    # Create a valid payment header
    server = X402Server(TEST_RECEIVER_ADDRESS)
    requirements = server.create_requirements(price_usdc=0.1, resource="/test")
    
    payment = PaymentPayload(
        signature="valid_sig",
        nonce=requirements.nonce,
        from_address="payer",
        to_address=TEST_RECEIVER_ADDRESS,
        amount=usdc_to_lamports(0.1),
        timestamp=1234567890
    )
    
    # Mock request with payment
    mock_request = Mock(spec=Request)
    mock_request.headers = Mock()
    mock_request.headers.get = Mock(return_value=payment.to_header())
    mock_request.url = "http://test/url"
    
    mock_response = Mock()
    mock_response.headers = {}
    
    # Mock nonce store to allow payment
    mock_cursor = mock_sqlite_connect.return_value.cursor.return_value
    mock_cursor.fetchone.return_value = None  # Nonce not used
    
    @require_payment(price_usdc=0.1, wallet_address=TEST_RECEIVER_ADDRESS)
    async def protected_endpoint(request: Request, response: Mock):
        return {"data": "success"}
    
    result = await protected_endpoint(request=mock_request, response=mock_response)
    
    assert result == {"data": "success"}