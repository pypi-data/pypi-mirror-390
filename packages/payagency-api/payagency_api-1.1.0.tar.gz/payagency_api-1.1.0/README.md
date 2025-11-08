# PayAgency API Python SDK

A comprehensive Python SDK for PayAgency payment processing platform, supporting multiple payment methods including card payments, cryptocurrency transactions, payouts, and payment links.

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [API Reference](#api-reference)
  - [Payment](#payment)
  - [Payout](#payout)
  - [Payment Links](#payment-links)
  - [Cryptocurrency](#cryptocurrency)
  - [Transactions](#transactions)
  - [Refunds](#refunds)
- [Error Handling](#error-handling)
- [Security](#security)
- [Environment](#environment)
- [Type Hints Support](#type-hints-support)
- [License](#license)

## Installation

```bash
pip install payagency-api
```

## Quick Start

```python
from payagency_api import PayAgencyApi

# Initialize the SDK with minimal configuration
pay_agency = PayAgencyApi(
    encryption_key="89ca59fb3b49ada55851021df12cfbc5",  # 32-character encryption key
    secret_key="PA_TEST_your-secret-key",  # or PA_LIVE_ for production
    # base_url is optional - defaults to https://backend.pay.agency
)

# Or with custom base URL
pay_agency = PayAgencyApi(
    encryption_key="89ca59fb3b49ada55851021df12cfbc5",
    secret_key="PA_TEST_your-secret-key",
    base_url="https://CUSTOM_SUB_DOMAIN.pay.agency"
)

# Make a payment
payment = pay_agency.payment.s2s({
    "first_name": "James",
    "last_name": "Dean",
    "email": "james@gmail.com",
    "address": "64 Hertingfordbury Rd",
    "country": "GB",
    "city": "Newport",
    "state": "GB",
    "zip": "TF10 8DF",
    "ip_address": "127.0.0.1",
    "phone_number": "7654233212",
    "amount": 100,
    "currency": "GBP",
    "card_number": "4111111111111111",
    "card_expiry_month": "12",
    "card_expiry_year": "2027",
    "card_cvv": "029",
    "redirect_url": "https://pay.agency",
    "webhook_url": "https://pay.agency/webhook",
    "terminal_id": "T12345",  # optional
})
```

## Configuration

### PayAgencyClientOptions

| Parameter        | Type | Required | Description                                                       |
| ---------------- | ---- | -------- | ----------------------------------------------------------------- |
| `encryption_key` | str  | Yes      | 32-character encryption key for payload encryption                |
| `secret_key`     | str  | Yes      | Your API secret key (PA_TEST for test, PA_LIVE for live)          |
| `base_url`       | str  | No       | PayAgency API base URL (defaults to `https://backend.pay.agency`) |

### Environment Detection

The SDK automatically detects the environment based on your secret key:

- Keys starting with `PA_LIVE_` use live endpoints
- Keys starting with `PA_TEST_` use test endpoints

## API Reference

### Payment

The Payment module supports multiple payment methods:

#### Server-to-Server (S2S) Card Payments

```python
result = pay_agency.payment.s2s({
    "first_name": "James",
    "last_name": "Dean",
    "email": "james@gmail.com",
    "address": "64 Hertingfordbury Rd",
    "country": "GB",
    "city": "Newport",
    "state": "GB",
    "zip": "TF10 8DF",
    "ip_address": "127.0.0.1",
    "phone_number": "7654233212",
    "amount": 100,
    "currency": "GBP",
    "card_number": "4111111111111111",
    "card_expiry_month": "12",
    "card_expiry_year": "2027",
    "card_cvv": "029",
    "redirect_url": "https://pay.agency",
    "webhook_url": "https://pay.agency/webhook",  # optional
    "order_id": "ORDER_123",  # optional
    "terminal_id": "T12345",  # optional
})

# Response format (Python dict):
{
    "status": "SUCCESS" | "REDIRECT" | "FAILED",
    "message": str,
    "data": {
        "amount": int,
        "currency": str,
        "order_id": str | None,
        "transaction_id": str,
        "customer": {
            "first_name": str,
            "last_name": str,
            "email": str,
        },
        "refund": {
            "status": bool,
            "refund_date": str | None,
        },
        "chargeback": {
            "status": bool,
            "chargeback_date": str | None,
        },
    },
    "redirect_url": str  # Present for REDIRECT status
}
```

#### Hosted Payment

```python
hosted_payment = pay_agency.payment.hosted({
    "first_name": "James",
    "last_name": "Dean",
    "email": "james@gmail.com",
    "address": "64 Hertingfordbury Rd",
    "country": "GB",
    "city": "Newport",
    "state": "GB",
    "zip": "TF10 8DF",
    "ip_address": "127.0.0.1",
    "phone_number": "7654233212",
    "amount": 100,
    "currency": "GBP",
    "redirect_url": "https://pay.agency",
    "webhook_url": "https://pay.agency/webhook",  # optional
    "order_id": "ORDER_123",  # optional
    "terminal_id": "T12345",  # optional
})

# Returns the same response format as S2S
```

#### Alternative Payment Methods (APM)

```python
apm_payment = pay_agency.payment.apm({
    "first_name": "James",
    "last_name": "Dean",
    "email": "james@gmail.com",
    "address": "64 Hertingfordbury Rd",
    "country": "GB",
    "city": "Newport",
    "state": "GB",
    "zip": "TF10 8DF",
    "ip_address": "127.0.0.1",
    "phone_number": "7654233212",
    "amount": 100,
    "currency": "GBP",
    "redirect_url": "https://pay.agency",
    "webhook_url": "https://pay.agency/webhook",  # optional
    "order_id": "ORDER_123",  # optional
    "terminal_id": "T12345",  # optional
})

# Returns the same response format as S2S
```

### Payout

Manage payouts and wallet operations:

#### Create Payout

```python
payout = pay_agency.payout.create_payout({
    "wallet_id": "WAL1234567890",
    "first_name": "James",
    "last_name": "Dean",
    "email": "james@gmail.com",
    "address": "64 Hertingfordbury Rd",
    "country": "US",
    "city": "Newport",
    "state": "US",
    "zip": "TF10 8DF",
    "ip_address": "127.0.0.1",
    "phone_number": "7654233212",
    "amount": 100,
    "currency": "USD",
    "card_number": "4222222222222222",
    "card_expiry_month": "10",
    "card_expiry_year": "2030",
    "webhook_url": "https://pay.agency/webhook",  # optional
    "order_id": "ORDER_123",  # optional
})

# Response format:
{
    "status": "SUCCESS" | "BLOCKED" | "PENDING",
    "message": str,
    "data": {
        "amount": int,
        "currency": str,
        "order_id": str | None,
        "transaction_id": str,
        "customer": {
            "first_name": str,
            "last_name": str,
            "email": str,
        },
    },
    "redirect_url": str  # optional
}
```

#### Get Wallets

```python
# Get all wallets
wallets = pay_agency.payout.get_wallets()

# Response format:
{
    "data": [
        {
            "wallet_id": str,
            "currency": str,
            "amount": int,
            "payment_method": str,
            "status": "Active" | "Inactive",
        }
    ]
}
```

#### Estimate Payout Fee

```python
fee_estimate = pay_agency.payout.estimate_fee({
    "wallet_id": "WAL7825818519632620",
    "amount": 200,
    "card_number": "4111111111111111",
})

# Response format:
{
    "data": {
        "amount_required": int,
        "wallet_balance": int,
        "total_fee": int,
    }
}
```

#### Check Payout Status

```python
status = pay_agency.payout.get_payout_status("PAYOUT_REFERENCE_123")

# Response format:
{
    "status": "SUCCESS" | "PENDING" | "FAILED",
    "message": str,
    "data": {
        "amount": int,
        "currency": str,
        "order_id": str | None,
        "transaction_id": str,
        "customer": {
            "first_name": str,
            "last_name": str,
            "email": str,
        },
    }
}
```

### Payment Links

Create and manage payment links:

#### Create Payment Link

```python
payment_link = pay_agency.payment_link.create({
    "payment_template_id": "PLI07435325281394735",  # Required
    "amount": 1000,  # optional
    "currency": "USD",  # optional
    "expiry_date": "2024-12-31",  # optional
    "terminal_id": "T12345",  # optional
    "order_id": "ORDER_123",  # optional
})

# Response format:
{
    "message": str,
    "data": str  # The payment link URL
}
```

#### Get Payment Templates

```python
templates = pay_agency.payment_link.get_templates()

# Response format:
{
    "data": [
        {
            "template_id": str,
            "template_name": str,
            "payment_template_id": str,
            "template_screenshot": str,
            "redirect_url": str,
            "webhook_url": str,
        }
    ]
}
```

### Cryptocurrency

Handle cryptocurrency transactions:

#### Comprehensive Methods

The Crypto module provides both individual convenience methods and comprehensive methods for full control:

##### Full-Featured Payment Method

```python
# Full crypto payment method - handles both OnRamp and OffRamp based on transaction_type
crypto_payment = pay_agency.crypto.payment({
    "transaction_type": "ONRAMP",  # or "OFFRAMP"
    "first_name": "Diana",
    "last_name": "Prince",
    "email": "diana@pay.agency",
    "phone_number": "0123456789",
    "fiat_amount": 200,  # Required for ONRAMP, omit for OFFRAMP
    # "crypto_amount": "0.05",  # Required for OFFRAMP, omit for ONRAMP
    "fiat_currency": "EUR",
    "crypto_currency": "BTC",
    "wallet_address": "1BoatSLRHtKNngkdXEeobR76b53LETtpyT",
    "ip_address": "127.0.0.1",
    "country": "GB",
    "crypto_network": "BITCOIN",
    "redirect_url": "https://pay.agency",
    "webhook_url": "https://pay.agency/webhook",  # optional
    "order_id": "ORDER_123",  # optional
    "terminal_id": "T12345",  # optional
})
```

##### OnRamp (Fiat to Crypto)

```python
# Create OnRamp payment link
on_ramp_link = pay_agency.crypto.on_ramp_link({
    "fiat_amount": 100,
    "fiat_currency": "GBP",
    "crypto_currency": "BTC",
    "payment_template_id": "PLI07435325281394735",
    "order_id": "ORDER_123",  # optional
    "terminal_id": "T12345",  # optional
    "expiry_date": "2024-12-31",  # optional
})

# Direct OnRamp transaction
on_ramp = pay_agency.crypto.on_ramp({
    "first_name": "Diana",
    "last_name": "Prince",
    "email": "diana@pay.agency",
    "phone_number": "0123456789",
    "fiat_amount": 200,
    "fiat_currency": "EUR",
    "crypto_currency": "BTC",
    "wallet_address": "1BoatSLRHtKNngkdXEeobR76b53LETtpyT",
    "ip_address": "127.0.0.1",
    "country": "GB",
    "crypto_network": "BITCOIN",
    "redirect_url": "https://pay.agency",
    "webhook_url": "https://pay.agency/webhook",  # optional
    "order_id": "ORDER_123",  # optional
    "terminal_id": "T12345",  # optional
})

# Response format:
{
    "status": "REDIRECT" | "PENDING" | "FAILED",
    "message": str,
    "redirect_url": str,  # optional
    "data": {
        "transaction_id": str,
        "fiat": str,
        "fiat_amount": int,
        "crypto": str,
        "crypto_amount": int,
        "customer": {
            "first_name": str,
            "last_name": str,
            "email": str,
        },
    }
}
```

##### OffRamp (Crypto to Fiat)

```python
# Create OffRamp payment link
off_ramp_link = pay_agency.crypto.off_ramp_link({
    "fiat_currency": "GBP",
    "crypto_currency": "BTC",
    "crypto_amount": "0.01",
    "payment_template_id": "PLI07435325281394735",
    "order_id": "ORDER_123",  # optional
    "terminal_id": "T12345",  # optional
    "expiry_date": "2024-12-31",  # optional
})

# Direct OffRamp transaction
off_ramp = pay_agency.crypto.off_ramp({
    "first_name": "Ethan",
    "last_name": "Hunt",
    "email": "ethan@pay.agency",
    "phone_number": "0123456789",
    "fiat_currency": "GBP",
    "crypto_currency": "BTC",
    "crypto_amount": "0.05",
    "wallet_address": "1BoatSLRHtKNngkdXEeobR76b53LETtpyT",
    "ip_address": "127.0.0.1",
    "country": "GB",
    "crypto_network": "BITCOIN",
    "redirect_url": "https://pay.agency",
    "webhook_url": "https://pay.agency/webhook",  # optional
    "order_id": "ORDER_123",  # optional
    "terminal_id": "T12345",  # optional
})

# Returns the same response format as OnRamp
```

#### Crypto PayIn

```python
# Get supported currencies
currencies = pay_agency.crypto.get_currencies({
    "country": "GB",  # ISO 3166-1 alpha-2 country code
    "amount": 100,
})

# Response format:
{
    "message": str,
    "data": [
        {
            "name": str,
            "code": str,
            "symbol": str,
        }
    ]
}

# Create PayIn link
payin_link = pay_agency.crypto.payin_link({
    "fiat_amount": 150,
    "fiat_currency": "USD",
    "crypto_currency": "BTC",
    "payment_template_id": "PLI07435325281394735",
    "order_id": "ORDER_123",  # optional
    "terminal_id": "T12345",  # optional
    "expiry_date": "2024-12-31",  # optional
})

# Direct crypto payin
payin = pay_agency.crypto.payin({
    "first_name": "Fiona",
    "last_name": "Gallagher",
    "email": "hello@gmail.com",
    "address": "64 Hertingfordbury Rd",
    "phone_number": "0123456789",
    "ip_address": "127.0.0.1",
    "crypto_currency": "BTC",
    "amount": 300,
    "currency": "USD",
    "crypto_network": "BITCOIN",
    "country": "US",
    "redirect_url": "https://pay.agency",
    "webhook_url": "https://pay.agency/webhook",  # optional
    "order_id": "ORDER_123",  # optional
    "terminal_id": "T12345",  # optional
})

# Response format:
{
    "status": "SUCCESS" | "PENDING" | "FAILED",
    "message": str,
    "redirect_url": str,  # optional
    "data": {
        "amount": int,
        "currency": str,
        "order_id": str | None,
        "transaction_id": str,
        "customer": {
            "first_name": str,
            "last_name": str,
            "email": str,
        },
        "crypto_currency": str,
    }
}
```

### Transactions

Query transaction history:

#### Get Transactions

```python
transactions = pay_agency.txn.get_transactions({
    "transaction_start_date": "2023-01-01",  # optional
    "transaction_end_date": "2023-12-31",  # optional
    "nextCursor": "cursor_value",  # optional - for pagination
    "prevCursor": "cursor_value",  # optional - for pagination
})

# Response format:
{
    "message": str,
    "data": [
        {
            "first_name": str,
            "last_name": str,
            "converted_amount": str,
            "converted_currency": str,
            "transaction_id": str,
            "amount": str,
            "currency": str,
            "status": str,
            "card_type": str | None,
            "card_number": str | None,
            "transaction_type": str,
            "order_id": str | None,
            "country": str,
            "email": str,
            "created_at": str,
            "transaction_date": str,
            "chargeback_date": str | None,
            "refund_date": str | None,
            "suspicious_date": str | None,
            "merchant_connector": {
                "name": str,
            },
            "user": {
                "name": str,
                "user_kyc": {
                    "name": str,
                },
            },
        }
    ],
    "meta": {
        "hasNextPage": bool,
        "hasPreviousPage": bool,
        "nextCursor": str,  # optional
        "prevCursor": str,  # optional
        "totalCount": int,
    }
}
```

#### Get Wallet Transactions

```python
wallet_transactions = pay_agency.txn.get_wallet_transactions({
    "transaction_start_date": "2023-01-01",  # optional
    "transaction_end_date": "2023-12-31",  # optional
    "next_cursor": "cursor_value",  # optional - for pagination
    "prev_cursor": "cursor_value",  # optional - for pagination
})

# Returns the same response format as get_transactions
```

### Refunds

Process refunds:

```python
# Direct refund method
refund = pay_agency.refund({
    "reason": "Customer request",
    "transaction_id": "TXN_123",
})

# Response format:
{
    "status": "SUCCESS",
    "message": str,
    "data": {
        "amount": int,
        "currency": str,
        "order_id": str | None,
        "transaction_id": str,
        "customer": {
            "first_name": str,
            "last_name": str,
            "email": str,
        },
        "refund": {
            "status": bool,
            "refund_date": str | None,
        },
        "chargeback": {
            "status": bool,
            "chargeback_date": str | None,
        },
    }
}
```

## Error Handling

The SDK uses requests for HTTP requests and will raise exceptions for failed requests:

```python
from payagency_api import PayAgencyApi, PayAgencyError

try:
    payment = pay_agency.payment.s2s(payment_data)
    print("Payment successful:", payment)
except PayAgencyError as e:
    # PayAgency API error
    print(f"Payment failed: {e}")
    print(f"Status code: {e.status_code}")
    print(f"Response: {e.response}")
except requests.RequestException as e:
    # Network error
    print(f"Network error: {e}")
except Exception as e:
    # Other error
    print(f"Error: {e}")
```

## Security

### Encryption

The SDK automatically encrypts request payloads using AES-256-CBC encryption with your provided encryption key. Some endpoints (like payment links and refunds) skip encryption as indicated by the `skip_encryption` parameter.

### API Key Security

- Never expose your API keys in client-side code
- Use test keys (`PA_TEST_`) for development
- Use live keys (`PA_LIVE_`) only in production
- Rotate your keys regularly

### Best Practices

1. Store API keys in environment variables
2. Use HTTPS for all webhook URLs
3. Validate webhook signatures on your server
4. Implement proper error handling
5. Log transactions for auditing

## Environment

The SDK supports both test and live environments:

### Test Environment

- Use secret keys starting with `PA_TEST_`
- Returns mock data for certain endpoints (wallets, fee estimation)
- Safe for development and testing

### Live Environment

- Use secret keys starting with `PA_LIVE_`
- Processes real transactions
- Use only in production

## Type Hints Support

The SDK is written with comprehensive type hints for better IDE support and type checking:

```python
from payagency_api import PayAgencyApi
from payagency_api.types import (
    PaymentResponse,
    PayoutResponse,
    CryptoPaymentResponse,
    RefundResponse,
)

# Type hints are included for all methods and responses
def process_payment(pay_agency: PayAgencyApi) -> PaymentResponse:
    return pay_agency.payment.s2s({
        "first_name": "John",
        "last_name": "Doe",
        # ... other fields
    })
```

### Important Notes

- **Payment amounts**: Use actual currency amounts as integers (e.g., 1 for $1.00 or £1.00)
- **Crypto amounts**: For crypto, use string format for precise decimal values (e.g., "0.01" for Bitcoin)
- **Country codes**: Use ISO 3166-1 alpha-2 country codes (e.g., "GB", "US")
- **Currency codes**: Use ISO 4217 currency codes (e.g., "USD", "GBP", "EUR")
- **Crypto networks**: Use uppercase format (e.g., "BITCOIN", "ETHEREUM")
- **Card expiry years**: Use full 4-digit format (e.g., "2027", not "27")
- **Optional fields**: Fields marked as optional can be omitted from the payload

## License

MIT License - see the LICENSE file for details.

## Support

For support and documentation, please visit [PayAgency Documentation](https://docs.pay.agency) or contact support@pay.agency

---

**Version**: 1.0.0

**Author**: PaneruVipin

**Repository**: [payagency-python](https://github.com/vp-payomatix/payagency-python-sdk)
