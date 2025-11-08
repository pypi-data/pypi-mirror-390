"""
Test configuration and fixtures for x402-solana tests
IMPROVED VERSION - Fixes all async mock issues
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, Mock, patch
import time
import json
import base64

# Dependencies from your project
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from x402_solana.types import Network, PaymentRequirements, PaymentPayload, usdc_to_lamports

# --- Constants and Test Data ---

TEST_PAYER_KEYPAIR = Keypair()
TEST_RECEIVER_PUBKEY = Pubkey.new_unique()
TEST_RECEIVER_ADDRESS = str(TEST_RECEIVER_PUBKEY)
TEST_URL = "http://api.test/resource"
TEST_PRICE_USDC = 0.01
TEST_PRICE_LAMPORTS = usdc_to_lamports(TEST_PRICE_USDC)
TEST_NONCE = "test_unique_nonce_123"
TEST_SIGNATURE = "5Jd3xZf7tC4rM3R2s2X6r7M4tG7c9h2e8U1b0Y5p0K1w7D9k2R4q8L0v6N3u8j5i2T4v8y0z6Q1x3R"
TEST_TIMESTAMP = int(time.time())

# --- Event Loop Fixture ---

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# --- Mock Fixtures ---

@pytest.fixture
def mock_httpx_client(monkeypatch):
    """Mocks the internal httpx.AsyncClient used by X402Client."""
    mock_client = Mock()
    mock_client.aclose = AsyncMock()
    mock_client.request = AsyncMock()
    
    # Create a mock class that returns our mock_client
    mock_class = Mock(return_value=mock_client)
    monkeypatch.setattr('httpx.AsyncClient', mock_class)
    
    return mock_client


@pytest.fixture
def mock_solana_async_client(monkeypatch):
    """Mocks the solana.rpc.async_api.AsyncClient used by X402Client - IMPROVED VERSION."""
    mock_client = Mock()
    mock_client.close = AsyncMock()
    
    # Mock get_latest_blockhash with proper structure
    mock_blockhash_response = Mock()
    mock_blockhash_response.value = Mock(blockhash=Pubkey.new_unique())
    mock_client.get_latest_blockhash = AsyncMock(return_value=mock_blockhash_response)
    
    # Mock send_transaction
    mock_tx_response = Mock()
    mock_tx_response.value = TEST_SIGNATURE
    mock_client.send_transaction = AsyncMock(return_value=mock_tx_response)
    
    # Mock get_signature_statuses for confirmation
    mock_status_response = Mock()
    mock_status_response.value = [Mock(confirmation_status='confirmed', err=None)]
    mock_client.get_signature_statuses = AsyncMock(return_value=mock_status_response)
    
    # FIXED: Mock get_account_info with proper awaitable response
    mock_account_response = Mock()
    mock_account_response.value = Mock(
        data=b'some_data',
        owner=Pubkey.new_unique(),
        lamports=1000000
    )
    mock_client.get_account_info = AsyncMock(return_value=mock_account_response)
    
    # Create a mock class that returns our mock_client
    mock_class = Mock(return_value=mock_client)
    monkeypatch.setattr('solana.rpc.async_api.AsyncClient', mock_class)
    
    return mock_client


@pytest.fixture
def mock_solana_sync_client(monkeypatch):
    """Mocks the solana.rpc.api.Client used by X402Server - IMPROVED VERSION."""
    mock_client = Mock()
    
    # FIXED: Mock transaction verification with proper structure
    mock_tx_response = Mock()
    mock_tx_response.value = Mock()
    # The transaction object structure
    mock_tx_response.value.transaction = Mock()
    mock_tx_response.value.transaction.meta = Mock(err=None)
    
    mock_client.get_transaction = Mock(return_value=mock_tx_response)
    
    # Create a mock class that returns our mock_client
    mock_class = Mock(return_value=mock_client)
    monkeypatch.setattr('solana.rpc.api.Client', mock_class)
    
    return mock_client


@pytest.fixture(autouse=True)
def mock_sqlite_connect(monkeypatch):
    """Mocks sqlite3.connect for NonceStore isolation."""
    mock_conn = Mock()
    mock_cursor = Mock()
    mock_cursor.fetchone = Mock(return_value=None)
    mock_cursor.fetchall = Mock(return_value=[])
    mock_cursor.rowcount = 0
    mock_cursor.execute = Mock()
    mock_conn.cursor = Mock(return_value=mock_cursor)
    mock_conn.commit = Mock()
    mock_conn.close = Mock()
    
    mock_connect = Mock(return_value=mock_conn)
    monkeypatch.setattr('sqlite3.connect', mock_connect)
    
    return mock_connect


# --- Project-Specific Fixtures ---

@pytest.fixture
def client_keypair():
    """Returns the Keypair for the X402Client (the payer)."""
    return TEST_PAYER_KEYPAIR


@pytest.fixture
def server_address():
    """Returns the receiver's address for the X402Server."""
    return TEST_RECEIVER_ADDRESS


@pytest.fixture
def mock_requirements():
    """Returns a PaymentRequirements object expected by the Client."""
    return PaymentRequirements(
        pay_to=TEST_RECEIVER_ADDRESS,
        amount=TEST_PRICE_LAMPORTS,
        asset=Network.DEVNET.usdc_mint(),
        network=Network.DEVNET.value,
        nonce=TEST_NONCE,
        resource=TEST_URL,
        description="Test Access",
        expires_at=TEST_TIMESTAMP + 300
    )


@pytest.fixture
def mock_payment_payload():
    """Returns a PaymentPayload object used by the Server for verification."""
    return PaymentPayload(
        signature=TEST_SIGNATURE,
        nonce=TEST_NONCE,
        from_address=str(TEST_PAYER_KEYPAIR.pubkey()),
        to_address=TEST_RECEIVER_ADDRESS,
        amount=TEST_PRICE_LAMPORTS,
        timestamp=TEST_TIMESTAMP
    )


@pytest.fixture
def mock_payment_header(mock_payment_payload):
    """Returns the base64 encoded header string."""
    return mock_payment_payload.to_header()