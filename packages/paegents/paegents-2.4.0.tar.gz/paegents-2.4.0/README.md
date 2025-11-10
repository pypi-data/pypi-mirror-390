# Paegents Python SDK

The official Python SDK for **Paegents** - Payment infrastructure for AI agents.

## Installation

```bash
pip install paegents
```

## Quick Start

```python
from paegents import PaegentsSDK

# Initialize the SDK
sdk = PaegentsSDK(
    api_url="https://api.paegents.com",
    agent_id="my_ai_agent",
    api_key="ak_live_your_api_key_here"
)

# Make an A2A payment to a supplier
response = sdk.pay_supplier(
    supplier="acme-corp.com",
    amount=2500,  # $25.00 in cents
    description="GPU compute credits"
)

print(f"Payment {response.status}: {response.txn_id}")

# Check payment status
status = sdk.check_a2a_status(response.txn_id)
print(f"Current status: {status.status}")
```

## AP2 Mandates & Stablecoin (x402)

Use AP2 to pre-authorize spend via intent/cart mandates and execute payments
across card, ACH, and stablecoin rails.

```python
import os
from paegents import (
    build_card_payment_method,
    build_stablecoin_payment_method,
)

# 1) Create an intent mandate for your agent
intent = sdk.create_ap2_intent_mandate(
    policy={
        "max_amount": {"value": 25_00},  # $25 ceiling
        "currency": "usd"
    }
)

# 2) Attach a cart mandate (invoice/basket)
cart = sdk.create_ap2_cart_mandate(
    intent_mandate_id=intent.id,
    cart={
        "total": 12_50,
        "currency": "usd",
        "description": "Monthly agent hosting"
    }
)

# 3a) Execute a card payment (Stripe/Braintree)
card_payment = sdk.ap2_pay(
    intent_mandate_id=intent.id,
    cart_mandate_id=cart.id,
    payment_method=build_card_payment_method(provider="stripe")
)
print(card_payment.status)

# 3b) Execute a stablecoin payment on Coinbase x402
stablecoin_payment = sdk.ap2_pay(
    intent_mandate_id=intent.id,
    cart_mandate_id=cart.id,
    payment_method=build_stablecoin_payment_method(
        payer_private_key=os.environ["STABLE_COIN_PRIVATE_KEY"],
        destination_wallet=os.environ.get("STABLE_COIN_DESTINATION"),
    )
)
print(stablecoin_payment.onchain_txid)
```

The stablecoin helper accepts optional parameters (`network`, `asset`,
`max_timeout_seconds`, etc.) so you can tune facilitator requests without
hand-crafting JSON payloads.

## A2A (Agent-to-Agent) Payments

The core feature of Paegents is seamless agent-to-agent payments using domain-based supplier resolution.

### Making a Payment

```python
# Pay a supplier by domain
response = sdk.pay_supplier(
    supplier="software-company.io",
    amount=5000,  # $50.00 in cents
    description="API usage charges",
    currency="usd"  # Optional, defaults to USD
)

# Handle different response statuses
if response.status == "paid":
    print(f"Payment successful! Transaction: {response.txn_id}")
elif response.status == "processing":
    print(f"Payment processing... Transaction: {response.txn_id}")
elif response.status == "supplier_onboarding":
    print(f"Supplier needs onboarding: {response.next_action_url}")
elif response.status == "failed":
    print(f"Payment failed: {response.error}")
```

### Checking Payment Status

```python
# Poll for status updates
status = sdk.check_a2a_status("agt_txn_123abc456def")

print(f"Status: {status.status}")
print(f"Events: {status.events}")
```

## Traditional MCP Payments

For payments to specific accounts (legacy method):

### Stripe Payments

```python
from paegents import PaymentRequest

# Pay a Stripe account
payment = PaymentRequest(
    agent_id="my_agent",
    amount=1000,  # $10.00
    currency="usd",
    description="Service payment",
    payment_method="stripe",
    recipient_account_id="acct_stripe_account_id"
)

response = sdk.create_payment(payment)
print(f"Payment intent: {response.payment_intent_id}")
```

### PayPal Payments

```python
from paegents import PayPalPaymentRequest

# Pay via PayPal email
paypal_payment = PayPalPaymentRequest(
    agent_id="my_agent",
    recipient_email="vendor@company.com",
    amount=25.00,  # PayPal uses dollars
    description="Consulting services"
)

response = sdk.create_paypal_payment(paypal_payment)
print(f"PayPal payment: {response.payment_intent_id}")
```

## Account Management

### Check Spending Limits

```python
limits = sdk.check_balance()
print(f"Daily remaining: ${limits.daily_remaining / 100:.2f}")
print(f"Monthly remaining: ${limits.monthly_remaining / 100:.2f}")
```

### Discover Recipients

```python
# Search for payment recipients
results = sdk.search_recipients("acme", payment_method="all")
for result in results.results:
    print(f"Found: {result['business_name']} ({result['payment_method']})")

# Check if email can receive PayPal
discovery = sdk.discover_paypal_email("payments@company.com")
if discovery.can_receive_paypal:
    print(f"✅ {discovery.email} can receive PayPal payments")
```

### Verify Receipts

```python
# Verify payment receipt authenticity
verification = sdk.verify_receipt("receipt_id_here")
if verification['valid']:
    print("✅ Receipt is authentic")
    print(f"Amount: ${verification['receipt']['amount'] / 100:.2f}")
else:
    print("❌ Receipt verification failed")
```

## Error Handling

```python
try:
    response = sdk.pay_supplier("unknown-company.com", 1000, "Test payment")
except Exception as e:
    print(f"Payment failed: {e}")
```

## Policies and Approvals (Owner JWT)

Some endpoints require the human owner (JWT). Pass a JWT per call.

```python
# Get and update policies
pol = sdk.get_agent_policies(agent_id="my-agent", jwt_token=os.environ["OWNER_JWT"])  # returns { agent_id, policy }
sdk.update_agent_policies({
    "rails": {"allowed": ["card", "stablecoin"]},
    "approvals": {"threshold_cents": 2000},
    "recipients": {"whitelist": ["0x1111..."]},
}, agent_id="my-agent", jwt_token=os.environ["OWNER_JWT"])  # returns { updated, policy }

# Approvals queue (after AP2 approval_required)
pending = sdk.list_approvals(status="pending", limit=20, agent_id="my-agent", jwt_token=os.environ["OWNER_JWT"])  # { approvals, count }
if pending.get("approvals"):
    sdk.approve_approval(pending["approvals"][0]["id"], agent_id="my-agent", jwt_token=os.environ["OWNER_JWT"])  # { approved: true }
```

## AP2 Approval Handling

When approval is required, `ap2_pay` returns a dict with `approval_required` rather than raising:

```python
res = sdk.ap2_pay(
    intent_mandate_id=intent.id,
    cart_mandate_id=cart.id,
    payment_method=build_card_payment_method(provider="stripe")
)

if isinstance(res, dict) and res.get("approval_required"):
    print("Approval requested:", res["request_id"])  # approve via SDK or dashboard
```

## Usage Agreements: Cart Itemization and Suggestions

Add cart line items on proposal; sellers can reject with suggestions:

```python
agreement = sdk.create_usage_agreement(UsageAgreementRequest(
    seller_agent_id='seller-123',
    quantity=1000,
    unit='api_calls',
    price_per_unit_cents=10,
    payment_method=build_card_payment_method(provider='stripe').to_dict(),
    cart_items=[{"description": "Requests bundle", "quantity": 1, "amount_cents": 10_000}],
    client_proposal_id='agree_demo_001',
))

# Seller reject with suggestions
sdk.reject_usage_agreement_with_suggestions(
    agreement.agreement_id,
    reason="Offer 2k calls at a discount",
    suggested_total_cents=18_000,
)
```

## Owner Spending Limits (JWT)

Get and update the human account’s daily/monthly limits:

```python
limits = sdk.get_spending_limits_owner(os.environ["OWNER_JWT"])  # { daily_limit, monthly_limit, current_daily_spent, current_monthly_spent }
sdk.update_spending_limits_owner(50, 200, os.environ["OWNER_JWT"])  # daily $50, monthly $200
```

## Webhooks Operations

Manage webhooks and deliveries programmatically:

```python
sdk.create_webhook("https://example.com/hooks", event_types=["agreement.*"], agent_id="my-agent", jwt_token=os.environ["OWNER_JWT"]))
subs = sdk.list_webhooks(agent_id="my-agent", jwt_token=os.environ["OWNER_JWT"])  # { webhooks: [...] }
sdk.rotate_webhook_secret(subs["webhooks"][0]["id"], agent_id="my-agent", jwt_token=os.environ["OWNER_JWT"]))

deliveries = sdk.list_webhook_deliveries(status="failed", limit=10, agent_id="my-agent", jwt_token=os.environ["OWNER_JWT"])  # { deliveries, count }
if deliveries.get("deliveries"):
    sdk.replay_webhook_delivery(deliveries["deliveries"][0]["id"], agent_id="my-agent", jwt_token=os.environ["OWNER_JWT"])  # { replayed: true }
```

## Typed Errors

The SDK raises `PolicyDeniedError` for policy blocks and `ApiError` for other HTTP errors:

```python
from paegents import PolicyDeniedError

try:
    sdk.ap2_pay(intent_mandate_id='i', cart_mandate_id='c', payment_method=build_card_payment_method())
except PolicyDeniedError as e:
    print("Policy blocked payment:", e)
```

## Marketplace: Usage Agreements

Create prepaid usage agreements between buyer and seller agents via the SDK. The dashboard is monitoring-first; creation and acceptance are SDK-only. Provide `client_proposal_id` for idempotency across retries.

```python
from paegents import PaegentsSDK
from paegents import build_card_payment_method

sdk = PaegentsSDK(api_url, agent_id, api_key)

# Buyer proposes an agreement
agreement = sdk.create_usage_agreement(
    request=UsageAgreementRequest(
        seller_agent_id='seller-agent-123',
        quantity=1000,
        unit='api_calls',
        price_per_unit_cents=10,
        payment_method=build_card_payment_method(provider='stripe').to_dict(),
        client_proposal_id='agree_demo_001',  # optional but recommended
        expires_in_hours=24,
    )
)

# Seller lists incoming proposals
incoming = sdk.list_usage_agreements(role='seller', status='proposed', limit=50)

# Seller accepts (idempotent)
accepted = sdk.accept_usage_agreement(agreement.agreement_id)

# Or reject
sdk.reject_usage_agreement(agreement.agreement_id)

# Fetch agreement details
details = sdk.get_usage_agreement(agreement.agreement_id)
```

Notes
- The SDK sets `Idempotency-Key` headers for propose/accept/reject automatically; include a stable `client_proposal_id` to dedupe across process restarts.
- Listing uses your SDK `agent_id` with an optional `role` filter (`buyer` or `seller`).

## Pollable Inbox

Agents can poll for events (e.g., `agreement.proposed`, `agreement.accepted`) without configuring webhooks. Useful for local dev, serverless, or NAT’d environments.

```python
# List recent events for this agent
events = sdk.list_agent_events(types=["agreement.proposed", "agreement.accepted"], limit=50)

for evt in events:
    if evt.type == "agreement.proposed":
        # Inspect evt.payload["agreement_id"], etc.
        pass
    sdk.ack_agent_event(evt.event_id)
```

Notes
- Use the `after` cursor with the last seen `event_id` to paginate.
- Acknowledgement is idempotent and safe to retry.

## Webhook Verification

Verify webhook signatures (HMAC-SHA256) sent by Paegents.

```python
from paegents import verify_webhook_signature

signature = request.headers.get('Paegents-Signature')
raw_body = request.data.decode('utf-8')  # or request.get_data(as_text=True)
secret = os.environ['PAEGENTS_WEBHOOK_SECRET']

try:
    verify_webhook_signature(signature_header=signature, raw_body=raw_body, secret=secret)
    event = json.loads(raw_body)
    # handle event
except Exception as e:
    return ("Invalid signature", 400)
```

Header format: `Paegents-Signature: t=<unix>, v1=<hex(hmac_sha256(secret, f"{t}.{body}"))>`.


## Configuration

### Environment Variables

You can set default configuration via environment variables:

```bash
export PAEGENTS_API_URL="https://api.paegents.com"
export PAEGENTS_API_KEY="ak_live_your_key_here" 
export PAEGENTS_AGENT_ID="my_agent_id"
```

```python
import os
from paegents import PaegentsSDK

# SDK will use environment variables if not provided
sdk = PaegentsSDK(
    api_url=os.getenv("PAEGENTS_API_URL"),
    agent_id=os.getenv("PAEGENTS_AGENT_ID"),
    api_key=os.getenv("PAEGENTS_API_KEY")
)
```

## Service Catalog (Gap 2)

Discover and register services in the Paegents marketplace.

### Register a Service

```python
from paegents import ServiceRegistration

# Register a service as a seller
service = ServiceRegistration(
    service_name="GPT-4 Inference API",
    description="High-quality AI text generation",
    category="ai_inference",
    price_model="per_unit",
    base_price_cents=10,  # $0.10 per token
    unit="tokens",
    min_quantity=100,
    max_quantity=1000000,
    capabilities={
        "models": ["gpt-4", "gpt-4-turbo"],
        "max_context": 128000
    }
)

registered = sdk.register_service(service)
print(f"Service ID: {registered.service_id}")
```

### Search for Services

```python
# Search the catalog
results = sdk.search_services(
    query="gpt inference",
    category="ai_inference",
    max_price=50,  # Up to $0.50 per unit
    limit=10
)

for service in results.results:
    print(f"{service.service_name}: ${service.base_price_cents/100:.2f} per {service.unit}")
```

### Manage Services

```python
# Update a service
sdk.update_service(
    service_id="svc_123",
    base_price_cents=8,  # Lower price to $0.08
    description="Updated description"
)

# List your services
my_services = sdk.list_my_services(limit=50)

# Deactivate a service
sdk.delete_service("svc_123")
```

## Prepaid Usage Escrow (Gap 3)

Create prepaid usage agreements with automatic escrow, payment release, and refunds.

### Create Usage Agreement (Buyer)

```python
from paegents import UsageAgreementRequest

# Buyer creates prepaid agreement
agreement = sdk.create_usage_agreement(
    UsageAgreementRequest(
        seller_agent_id="agent_seller_123",
        quantity=5000,  # 5,000 tokens
        unit="tokens",
        price_per_unit_cents=10,  # $0.10 per token
        payment_method={"rail": "stripe", "type": "card"},
        service_description="GPT-4 inference for chatbot",
        expires_in_hours=24
    )
)

print(f"Agreement ID: {agreement.agreement_id}")
print(f"Total: ${agreement.total_cents / 100:.2f}")
print(f"Status: {agreement.status}")
```

### Accept Agreement (Seller)

```python
# Seller accepts and funds escrow
accepted = sdk.accept_usage_agreement(agreement.agreement_id)
print(f"Escrow funded: ${accepted.total_cents / 100:.2f}")
print(f"Payment ID: {accepted.escrow_payment_id}")
```

### Record Usage (Seller)

```python
from paegents import RecordUsageRequest

# Seller records actual usage
completed = sdk.record_usage(
    agreement.agreement_id,
    RecordUsageRequest(
        units_used=3000,  # Used 3,000 out of 5,000 tokens
        completed=True,
        usage_proof={"logs": "proof_of_usage"}
    )
)

# Automatic payment release and refund
print(f"Released to seller: ${completed.released_cents / 100:.2f}")  # $300
print(f"Refunded to buyer: ${(completed.total_cents - completed.released_cents) / 100:.2f}")  # $200
```

### List and Manage Agreements

```python
# List all agreements (buyer or seller)
agreements = sdk.list_usage_agreements(status="active", limit=50)

# Get agreement details
agreement = sdk.get_usage_agreement("agr_123")

# Cancel before acceptance (buyer only)
sdk.cancel_usage_agreement("agr_123")

# Dispute agreement (buyer)
disputed = sdk.dispute_usage_agreement(
    "agr_123",
    reason="Service not delivered as agreed",
    evidence={"screenshots": ["url1", "url2"]}
)
```

## API Reference

### AgentPaymentsSDK

The main SDK class for interacting with Paegents.

#### Constructor

```python
sdk = PaegentsSDK(api_url, agent_id, api_key)
```

#### A2A Methods

- `pay_supplier(supplier, amount, description, currency="usd", txn_id=None)` → `A2APaymentResponse`
- `check_a2a_status(txn_id)` → `A2AStatusResponse`

#### Service Catalog Methods (Gap 2)

- `register_service(service)` → `ServiceDetails`
- `update_service(service_id, **kwargs)` → `Dict[str, Any]`
- `delete_service(service_id)` → `Dict[str, Any]`
- `get_service(service_id)` → `ServiceDetails`
- `list_my_services(limit=100, offset=0)` → `List[ServiceDetails]`
- `search_services(query=None, category=None, min_price=None, max_price=None, limit=50, offset=0)` → `CatalogSearchResult`

#### Usage Agreement Methods (Gap 3)

- `create_usage_agreement(request)` → `UsageAgreement`
- `get_usage_agreement(agreement_id)` → `UsageAgreement`
- `list_usage_agreements(status=None, limit=100)` → `List[UsageAgreement]`
- `accept_usage_agreement(agreement_id)` → `UsageAgreement`
- `record_usage(agreement_id, request)` → `UsageAgreement`
- `cancel_usage_agreement(agreement_id)` → `Dict[str, Any]`
- `dispute_usage_agreement(agreement_id, reason, evidence=None)` → `UsageAgreement`

#### Legacy MCP Methods

- `create_payment(request)` → `PaymentResponse`
- `create_paypal_payment(request)` → `PaymentResponse`
- `search_recipients(query, payment_method="all")` → `RecipientSearchResult`
- `discover_paypal_email(email)` → `EmailDiscoveryResult`
- `check_balance()` → `SpendingLimits`
- `verify_receipt(receipt_id)` → `Dict[str, Any]`

## Support

- **Documentation**: [docs.paegents.com](https://docs.paegents.com)
- **API Reference**: [docs.paegents.com/api](https://docs.paegents.com/api)  
- **Support**: [support@paegents.com](mailto:support@paegents.com)
- **Issues**: [github.com/paegents/python-sdk/issues](https://github.com/paegents/python-sdk/issues)

## License

MIT License - see [LICENSE](LICENSE) file for details.
