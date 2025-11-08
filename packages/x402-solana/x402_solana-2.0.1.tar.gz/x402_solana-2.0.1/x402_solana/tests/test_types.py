"""
Tests for x402 protocol types
"""

import json
import base64
import pytest
from x402_solana.types import (
    PaymentRequirements, 
    PaymentPayload, 
    PaymentReceipt,
    Network, 
    usdc_to_lamports,
    lamports_to_usdc
)


def test_usdc_to_lamports_conversion():
    """Test USDC to lamports conversion (6 decimals)."""
    assert usdc_to_lamports(1.0) == 1_000_000
    assert usdc_to_lamports(0.01) == 10_000
    assert usdc_to_lamports(123.456789) == 123456789


def test_lamports_to_usdc_conversion():
    """Test lamports to USDC conversion."""
    assert lamports_to_usdc(1_000_000) == 1.0
    assert lamports_to_usdc(10_000) == 0.01
    assert lamports_to_usdc(123456789) == 123.456789


def test_network_enum():
    """Test Network enum values."""
    assert Network.DEVNET.value == "solana-devnet"
    assert Network.MAINNET.value == "solana-mainnet"
    
    # Test RPC URLs
    assert "devnet" in Network.DEVNET.rpc_url()
    assert "mainnet" in Network.MAINNET.rpc_url()
    
    # Test USDC mint addresses are different
    assert Network.DEVNET.usdc_mint() != Network.MAINNET.usdc_mint()


def test_payment_requirements_creation():
    """Test creating PaymentRequirements."""
    reqs = PaymentRequirements(
        pay_to="SomeAddress",
        amount=10000,
        asset="USDCMint",
        network="solana-devnet",
        nonce="nonce123",
        resource="/api/data",
        description="Test payment",
        expires_at=1234567890
    )
    
    assert reqs.pay_to == "SomeAddress"
    assert reqs.amount == 10000
    assert reqs.to_usdc() == 0.01


def test_payment_requirements_serialization(mock_requirements):
    """Test PaymentRequirements can serialize to JSON and back."""
    json_str = mock_requirements.to_json()
    data = json.loads(json_str)
    
    assert data['pay_to'] == mock_requirements.pay_to
    assert data['amount'] == mock_requirements.amount
    assert data['network'] == Network.DEVNET.value
    
    new_reqs = PaymentRequirements.from_json(json_str)
    assert new_reqs.pay_to == mock_requirements.pay_to
    assert new_reqs.amount == mock_requirements.amount
    assert new_reqs.nonce == mock_requirements.nonce


def test_payment_payload_creation():
    """Test creating PaymentPayload."""
    payload = PaymentPayload(
        signature="sig123",
        nonce="nonce456",
        from_address="from_addr",
        to_address="to_addr",
        amount=50000,
        timestamp=1234567890
    )
    
    assert payload.signature == "sig123"
    assert payload.nonce == "nonce456"
    assert payload.amount == 50000


def test_payment_payload_header_encoding(mock_payment_payload):
    """Test PaymentPayload can encode to a base64 header string and decode back."""
    header_str = mock_payment_payload.to_header()
    
    # Verify it is base64 encoded
    decoded_bytes = base64.b64decode(header_str)
    decoded_json = json.loads(decoded_bytes)
    
    assert decoded_json['signature'] == mock_payment_payload.signature
    assert decoded_json['nonce'] == mock_payment_payload.nonce
    
    # Test round-trip
    new_payload = PaymentPayload.from_header(header_str)
    assert new_payload.signature == mock_payment_payload.signature
    assert new_payload.nonce == mock_payment_payload.nonce
    assert new_payload.amount == mock_payment_payload.amount


def test_payment_receipt_creation():
    """Test creating PaymentReceipt."""
    receipt = PaymentReceipt(
        signature="sig789",
        amount=100000,
        timestamp=1234567890,
        receipt_id="receipt_123",
        resource="/api/data"
    )
    
    assert receipt.signature == "sig789"
    assert receipt.amount == 100000
    assert receipt.receipt_id == "receipt_123"


def test_payment_receipt_header_encoding():
    """Test PaymentReceipt encoding to header."""
    receipt = PaymentReceipt(
        signature="sig789",
        amount=100000,
        timestamp=1234567890,
        receipt_id="receipt_123",
        resource="/api/data"
    )
    
    header_str = receipt.to_header()
    
    # Verify it's base64 encoded JSON
    decoded_bytes = base64.b64decode(header_str)
    decoded_json = json.loads(decoded_bytes)
    
    assert decoded_json['signature'] == "sig789"
    assert decoded_json['receipt_id'] == "receipt_123"
    assert decoded_json['resource'] == "/api/data"


def test_payment_requirements_to_usdc():
    """Test conversion from lamports to USDC in requirements."""
    reqs = PaymentRequirements(
        pay_to="addr",
        amount=50000,  # 0.05 USDC
        asset="mint",
        network="solana-devnet",
        nonce="nonce",
        resource="/test"
    )
    
    assert reqs.to_usdc() == 0.05