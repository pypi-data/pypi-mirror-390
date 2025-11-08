"""
Tests for PaymentAgent and BudgetManager
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from x402_solana.agent import PaymentAgent, BudgetManager
from x402_solana.types import usdc_to_lamports

TEST_URL = "http://api.test/resource"


# --- BudgetManager Tests ---

def test_budget_manager_initial_state():
    """Test default budget limits and empty transactions."""
    bm = BudgetManager()
    assert bm.max_per_request == 1.0
    assert bm.max_per_hour == 10.0
    assert bm.max_per_day == 100.0
    assert bm.get_stats()['total_spent'] == 0.0


@pytest.mark.parametrize("max_per_request, spend_amount, expected_can_spend", [
    (1.0, 0.5, True),   # Within limit
    (1.0, 1.0, True),   # Exact limit
    (1.0, 1.01, False), # Exceeds limit
])
def test_budget_manager_per_request_limit(max_per_request, spend_amount, expected_can_spend):
    """Test the per-request limit enforces constraint."""
    bm = BudgetManager(max_per_request=max_per_request)
    can_spend, _ = bm.can_spend(spend_amount)
    assert can_spend == expected_can_spend


@patch('time.time')
def test_budget_manager_hourly_limit(mock_time):
    """Test the hourly spending limit."""
    mock_time.return_value = 1000
    bm = BudgetManager(max_per_hour=10.0)
    
    # 1. Record transactions up to the limit within the hour
    for i in range(10):
        bm.record_transaction(f"sig{i}", 1.0, "url", True)  # Total spent: $10.0
    
    # 2. Check spending $0.01 more fails
    can_spend, reason = bm.can_spend(0.01)
    assert can_spend is False
    assert "hourly limit" in reason
    
    # 3. Simulate time passing within the hour
    mock_time.return_value = 1500
    can_spend, reason = bm.can_spend(0.01)
    assert can_spend is False
    
    # 4. Simulate time passing past the hour
    mock_time.return_value = 4601  # Just past the hour cutoff
    can_spend, reason = bm.can_spend(0.01)
    assert can_spend is True


@patch('time.time')
def test_budget_manager_daily_limit(mock_time):
    """Test the daily spending limit."""
    mock_time.return_value = 1000
    bm = BudgetManager(max_per_day=5.0, max_per_hour=100.0, max_per_request=1.0)
    
    # Spend up to daily limit
    for i in range(5):
        bm.record_transaction(f"sig{i}", 1.0, "url", True)
    
    # Should fail
    can_spend, reason = bm.can_spend(0.01)
    assert can_spend is False
    assert "daily limit" in reason


def test_budget_manager_get_stats():
    """Test statistics reporting."""
    bm = BudgetManager()
    
    bm.record_transaction("sig1", 0.5, "url1", True)
    bm.record_transaction("sig2", 0.3, "url2", True)
    bm.record_transaction("sig3", 0.1, "url3", False)
    
    stats = bm.get_stats()
    
    assert stats['total_transactions'] == 3
    assert stats['successful'] == 2
    assert stats['failed'] == 1
    assert stats['total_spent'] == 0.8  # Only successful transactions


# --- PaymentAgent Tests ---

@pytest.mark.asyncio
async def test_payment_agent_initialization(client_keypair):
    """Test PaymentAgent initializes correctly."""
    agent = PaymentAgent(
        client_keypair,
        max_per_request=0.5,
        max_per_hour=5.0,
        max_per_day=50.0,
        name="TestAgent"
    )
    
    assert agent.name == "TestAgent"
    assert agent.budget.max_per_request == 0.5
    assert str(agent.keypair.pubkey()) == str(client_keypair.pubkey())


@pytest.mark.asyncio
async def test_payment_agent_fetch_fails_on_budget_exceeded(client_keypair, mock_httpx_client, mock_solana_async_client):
    """Test PaymentAgent prevents fetch if internal budget is exceeded."""
    
    # Set max_per_request low (0.005)
    agent = PaymentAgent(client_keypair, max_per_request=0.005)

    # Attempt to fetch resource with max_price 0.01
    result = await agent.fetch_resource(
        "http://url", max_price=0.01
    )
    
    assert result is None
    
    # Ensure HTTP client was never called
    assert not mock_httpx_client.request.called
    
    # Check transaction failure was recorded in the budget
    stats = agent.get_stats()
    assert stats['failed'] == 1
    assert "exceeds per-request limit" in agent.budget.transactions[0].error


@pytest.mark.asyncio
async def test_payment_agent_records_successful_transaction(
    client_keypair, 
    mock_httpx_client, 
    mock_solana_async_client, 
    mock_requirements
):
    """Test PaymentAgent correctly updates budget after a successful payment flow."""
    
    # Setup mocks for successful 402 flow
    mock_402_response = Mock(status_code=402, text=mock_requirements.to_json())
    mock_200_response = Mock(status_code=200, content=b'{"data": "paid_content"}')
    mock_200_response.json = Mock(return_value={"data": "paid_content"})
    mock_200_response.headers = {}
    mock_httpx_client.request = AsyncMock(side_effect=[mock_402_response, mock_200_response])

    agent = PaymentAgent(client_keypair, max_per_request=0.1)
    
    result = await agent.fetch_resource(TEST_URL, max_price=0.05)
    
    # Assert result is correct
    assert result == {"data": "paid_content"}
    
    # Assert budget reflects the transaction
    stats = agent.get_stats()
    assert stats['successful'] == 1
    assert stats['total_spent'] == 0.05


@pytest.mark.asyncio
async def test_payment_agent_can_afford(client_keypair):
    """Test can_afford method."""
    agent = PaymentAgent(client_keypair, max_per_request=1.0)
    
    assert agent.can_afford(0.5) is True
    assert agent.can_afford(1.0) is True
    assert agent.can_afford(1.1) is False


@pytest.mark.asyncio
async def test_payment_agent_batch_fetch(
    client_keypair,
    mock_httpx_client,
    mock_solana_async_client,
    mock_requirements
):
    """Test batch fetching multiple URLs."""
    # Setup successful responses
    mock_200_response = Mock(status_code=200, content=b'{"data": "content"}')
    mock_200_response.json = Mock(return_value={"data": "content"})
    mock_200_response.headers = {}
    mock_httpx_client.request = AsyncMock(return_value=mock_200_response)
    
    agent = PaymentAgent(client_keypair, max_per_request=1.0)
    
    urls = ["http://url1", "http://url2", "http://url3"]
    results = await agent.batch_fetch(urls, max_price_per_url=0.1)
    
    assert len(results) == 3
    assert all(v == {"data": "content"} for v in results.values())


@pytest.mark.asyncio
async def test_payment_agent_close(client_keypair, mock_httpx_client, mock_solana_async_client):
    """Test agent cleanup."""
    agent = PaymentAgent(client_keypair)
    await agent.close()
    
    # Verify client connections were closed
    mock_httpx_client.aclose.assert_called_once()
    mock_solana_async_client.close.assert_called_once()