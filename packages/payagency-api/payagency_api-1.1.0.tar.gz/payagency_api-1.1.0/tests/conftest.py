"""
Test configuration and fixtures
"""

import os
import pytest
from unittest.mock import Mock, patch

from payagency_api import PayAgencyApi


@pytest.fixture
def mock_client():
    """Create a mock PayAgency client for testing"""
    return PayAgencyApi(
        encryption_key="12345678901234567890123456789012",  # 32 chars
        secret_key="PA_TEST_mock_secret_key"
    )


@pytest.fixture 
def mock_response():
    """Create a mock response"""
    mock_resp = Mock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"status": "SUCCESS", "message": "Test success"}
    return mock_resp


@pytest.fixture
def sample_payment_data():
    """Sample payment data for testing"""
    return {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com",
        "address": "123 Test St",
        "country": "US",
        "city": "Test City",
        "state": "CA",
        "zip": "12345",
        "ip_address": "127.0.0.1",
        "phone_number": "1234567890",
        "amount": 100,
        "currency": "USD",
        "card_number": "4111111111111111",
        "card_expiry_month": "12",
        "card_expiry_year": "2027",
        "card_cvv": "123",
        "redirect_url": "https://example.com",
    }


@pytest.fixture
def sample_payout_data():
    """Sample payout data for testing"""
    return {
        "wallet_id": "WAL123456789",
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com",
        "address": "123 Test St",
        "country": "US",
        "city": "Test City",
        "state": "CA",
        "zip": "12345",
        "ip_address": "127.0.0.1",
        "phone_number": "1234567890",
        "amount": 100,
        "currency": "USD",
        "card_number": "4111111111111111",
        "card_expiry_month": "12",
        "card_expiry_year": "2027",
    }
