import requests
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass
from datetime import datetime
import uuid
import hmac
import hashlib

@dataclass
class PaymentRequest:
    agent_id: str
    amount: int
    currency: str = "usd"
    description: Optional[str] = None
    payment_method: str = "stripe"  # "stripe" or "braintree"
    recipient_account_id: Optional[str] = None
    recipient_business_name: Optional[str] = None
    recipient_email: Optional[str] = None


@dataclass
class PaymentResponse:
    payment_intent_id: str
    client_secret: str
    status: str
    receipt: Dict[str, Any]
    payment_method: str = "stripe"


@dataclass
class RecipientSearchResult:
    query: str
    results: list
    total_found: int

@dataclass
class Receipt:
    receipt_id: str
    agent_id: str
    amount: int
    currency: str
    timestamp: str
    signature: str
    verification_url: str

@dataclass
class SpendingLimits:
    daily_limit: int
    monthly_limit: int
    daily_spent: int
    monthly_spent: int
    daily_remaining: int
    monthly_remaining: int

# AP2 / x402 models
@dataclass
class IntentMandate:
    id: str
    status: str
    policy: Dict[str, Any]
    subject: Dict[str, Any]
    hash: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class CartMandate:
    id: str
    status: str
    cart: Dict[str, Any]
    links: Dict[str, Any]
    hash: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class AP2PaymentResult:
    status: str
    rail: str
    processor: str
    processor_ref: str
    receipt: Dict[str, Any]
    onchain_txid: Optional[str] = None


@dataclass
class PaymentMethodPayload:
    rail: str
    provider: Optional[str] = None
    payment_reference: Optional[str] = None
    wallet_address: Optional[str] = None
    extra: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {"rail": self.rail}
        if self.provider:
            payload["provider"] = self.provider
        if self.payment_reference:
            payload["payment_reference"] = self.payment_reference
        if self.wallet_address:
            payload["wallet_address"] = self.wallet_address
        if self.extra:
            payload["extra"] = self.extra
        return payload


class ApiError(Exception):
    def __init__(self, message: str, status: int, body: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.status = status
        self.body = body


class PolicyDeniedError(ApiError):
    pass


def build_card_payment_method(
    *,
    provider: str = "stripe",
    payment_reference: Optional[str] = None,
    extra: Optional[Dict[str, Any]] = None,
) -> PaymentMethodPayload:
    """Helper for AP2 card payments (Stripe or Braintree)."""

    return PaymentMethodPayload(
        rail="card",
        provider=provider,
        payment_reference=payment_reference,
        extra=extra,
    )


def build_braintree_payment_method(
    *,
    customer_id: Optional[str] = None,
    merchant_account_id: Optional[str] = None,
    supplier_domain: Optional[str] = None,
    descriptor: Optional[Dict[str, Any]] = None,
) -> PaymentMethodPayload:
    """Helper for AP2 Braintree payments using stored customer IDs."""

    extra: Dict[str, Any] = {}
    if customer_id:
        extra["customer_id"] = customer_id
    if merchant_account_id:
        extra["merchant_account_id"] = merchant_account_id
    if supplier_domain:
        extra["supplier_domain"] = supplier_domain
    if descriptor:
        extra.update({
            "descriptor_name": descriptor.get("name"),
            "descriptor_phone": descriptor.get("phone"),
        })

    return PaymentMethodPayload(
        rail="braintree",
        provider="braintree",
        extra=extra or None,
    )


def build_stablecoin_payment_method(
    *,
    payer_private_key: str,
    destination_wallet: Optional[str] = None,
    network: str = "base-sepolia",
    asset: Optional[str] = None,
    max_timeout_seconds: Optional[int] = None,
    source_wallet_address: Optional[str] = None,
    additional_extra: Optional[Dict[str, Any]] = None,
) -> PaymentMethodPayload:
    """Helper for AP2 stablecoin payments via Coinbase x402."""

    extra: Dict[str, Any] = {
        "payer_private_key": payer_private_key,
        "network": network,
    }
    if asset:
        extra["asset"] = asset
    if max_timeout_seconds is not None:
        extra["max_timeout_seconds"] = max_timeout_seconds
    if source_wallet_address:
        extra["source_wallet_address"] = source_wallet_address
    if additional_extra:
        extra.update(additional_extra)

    return PaymentMethodPayload(
        rail="stablecoin",
        wallet_address=destination_wallet,
        extra=extra,
    )

# A2A Protocol Models
@dataclass
class A2APaymentRequest:
    """Agent-to-Agent payment request following the A2A protocol"""
    supplier: str  # Domain like "acme-corp.com"
    amount: int  # Amount in cents
    description: str
    currency: str = "usd"
    txn_id: Optional[str] = None  # Client-generated transaction ID
    msg: str = "PayRequest"
    version: str = "1.0"

@dataclass 
class A2APaymentResponse:
    """Agent-to-Agent payment response"""
    txn_id: str
    status: str  # "processing" | "supplier_onboarding" | "paid" | "failed"
    msg: str = "PayResponse"
    provisional_key: Optional[str] = None
    next_action_url: Optional[str] = None
    error: Optional[str] = None

@dataclass
class A2AStatusQuery:
    """Query the status of an A2A transaction"""
    txn_id: str
    msg: str = "StatusQuery"

@dataclass
class A2AStatusResponse:
    """Response to A2A status query"""
    txn_id: str
    status: str
    events: list
    msg: str = "StatusResponse"

# Gap 2: Service Catalog Models
@dataclass
class ServiceRegistration:
    """Service catalog registration request"""
    service_name: str
    description: str
    category: str
    price_model: str  # "per_unit" | "subscription" | "tiered"
    base_price_cents: int
    unit: str
    min_quantity: int = 1
    max_quantity: Optional[int] = None
    capabilities: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class ServiceDetails:
    """Service catalog entry details"""
    service_id: str
    agent_id: str
    service_name: str
    description: str
    category: str
    price_model: str
    base_price_cents: int
    unit: str
    min_quantity: int
    max_quantity: Optional[int]
    capabilities: Optional[Dict[str, Any]]
    metadata: Optional[Dict[str, Any]]
    is_active: bool
    created_at: str
    updated_at: str

@dataclass
class CatalogSearchResult:
    """Service catalog search results"""
    total: int
    results: list  # List of ServiceDetails
    query: Dict[str, Any]
    has_more: bool
    next_offset: Optional[int]

# Gap 3: Usage Agreement / Escrow Models
@dataclass
class UsageAgreementRequest:
    """Create a prepaid usage agreement"""
    seller_agent_id: str
    quantity: int
    unit: str
    price_per_unit_cents: int
    payment_method: Dict[str, Any]
    service_description: Optional[str] = None
    expires_in_hours: int = 24
    client_proposal_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    # Optional cart line items (stored under metadata.cart_items)
    cart_items: Optional[list] = None

@dataclass
class UsageAgreement:
    """Usage agreement details"""
    agreement_id: str
    buyer_agent_id: str
    seller_agent_id: str
    quantity: int
    unit: str
    price_per_unit_cents: int
    total_cents: int
    status: str
    expires_at: str
    payment_method: Optional[Dict[str, Any]] = None
    service_description: Optional[str] = None
    created_at: Optional[str] = None
    units_used: Optional[int] = None
    escrow_payment_id: Optional[str] = None
    released_cents: Optional[int] = None
    seller_receipt_id: Optional[str] = None
    buyer_receipt_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class RecordUsageRequest:
    """Record usage for an agreement"""
    units_used: int
    completed: bool = False
    usage_proof: Optional[Dict[str, Any]] = None


@dataclass
class AgentEvent:
    event_id: str
    type: str
    payload: Dict[str, Any]
    status: str
    attempt_count: int
    created_at: str


def verify_webhook_signature(signature_header: str, raw_body: str, secret: str, tolerance_seconds: int = 300) -> bool:
    """Verify Paegents webhook signature.

    Header format: "t=<unix>, v1=<hex(hmac_sha256(secret, f"{t}.{body}"))>"
    Raises ValueError on failure; returns True on success.
    """
    if not signature_header:
        raise ValueError("Missing Paegents-Signature header")
    try:
        parts = [p.strip() for p in signature_header.split(',')]
        t_part = next(p for p in parts if p.startswith('t='))
        v1_part = next(p for p in parts if p.startswith('v1='))
        t = int(t_part.split('=')[1])
        v1 = v1_part.split('=')[1]
    except Exception:
        raise ValueError("Invalid signature header")

    now = int(datetime.utcnow().timestamp())
    if abs(now - t) > tolerance_seconds:
        raise ValueError("Signature timestamp outside tolerance")

    msg = f"{t}.{raw_body}".encode()
    expected = hmac.new(secret.encode(), msg, hashlib.sha256).hexdigest()
    if not _timing_safe_equal(expected, v1):
        raise ValueError("Signature mismatch")
    return True


def _timing_safe_equal(a: str, b: str) -> bool:
    if len(a) != len(b):
        return False
    result = 0
    for x, y in zip(a.encode(), b.encode()):
        result |= x ^ y
    return result == 0

class AgentPaymentsSDK:
    def __init__(self, api_url: str, agent_id: str, api_key: str):
        self.api_url = api_url.rstrip('/')
        self.agent_id = agent_id
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}',
            'X-API-Key': api_key  # For routes that use X-API-Key header
        })

    def _with_jwt(self, jwt_token: Optional[str]) -> Dict[str, str]:
        headers: Dict[str, str] = {}
        if jwt_token:
            headers['Authorization'] = f'Bearer {jwt_token}'
        return headers

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request to the API"""
        url = f"{self.api_url}{endpoint}"
        response = self.session.request(method, url, **kwargs)
        
        if not response.ok:
            # Try to extract JSON error
            try:
                body = response.json()
                detail = body.get('detail') if isinstance(body, dict) else None
            except Exception:
                body = None
                detail = None
            msg = detail or response.text
            if isinstance(msg, str) and 'policy_denied' in msg.lower():
                raise PolicyDeniedError(msg, response.status_code, body)
            raise ApiError(f"API request failed: {msg}", response.status_code, body)
        
        return response.json()

    def create_payment(self, request: PaymentRequest) -> PaymentResponse:
        """Create a payment for an agent"""
        data = {
            "agent_id": request.agent_id,
            "amount": request.amount,
            "currency": request.currency,
            "description": request.description,
            "payment_method": request.payment_method
        }
        
        # Add recipient information
        if request.recipient_account_id:
            data["recipient_account_id"] = request.recipient_account_id
        elif request.recipient_business_name:
            data["recipient_business_name"] = request.recipient_business_name
        elif request.recipient_email:
            data["recipient_email"] = request.recipient_email
        
        result = self._make_request("POST", "/mcp/payments", json=data)
        
        return PaymentResponse(
            payment_intent_id=result["payment_intent"]["id"] if "payment_intent" in result else result["payment"]["id"],
            client_secret=result["payment_intent"]["client_secret"] if "payment_intent" in result else "",
            status=result["payment_intent"]["status"] if "payment_intent" in result else result["payment"]["state"],
            receipt=result["receipt"],
            payment_method=result.get("payment_method", "stripe")
        )


    def search_recipients(self, query: str, payment_method: str = "all") -> RecipientSearchResult:
        """Search for recipients across all payment methods"""
        params = {"query": query, "payment_method": payment_method}
        result = self._make_request("POST", "/mcp/search-recipients", params=params)
        
        return RecipientSearchResult(
            query=result["query"],
            results=result["results"],
            total_found=result["total_found"]
        )

    def check_balance(self) -> SpendingLimits:
        """Check spending limits and current balance"""
        result = self._make_request("GET", f"/mcp/balance/{self.agent_id}")
        
        return SpendingLimits(
            daily_limit=result["daily_limit"],
            monthly_limit=result["monthly_limit"],
            daily_spent=result["daily_spent"],
            monthly_spent=result["monthly_spent"],
            daily_remaining=result["daily_remaining"],
            monthly_remaining=result["monthly_remaining"]
        )

    def verify_receipt(self, receipt_id: str) -> Dict[str, Any]:
        """Verify a payment receipt"""
        return self._make_request("GET", f"/receipts/verify/{receipt_id}")

    # ---------------- Owner Spending Limits (JWT) ----------------
    def get_spending_limits_owner(self, jwt_token: str) -> Dict[str, Any]:
        headers = self._with_jwt(jwt_token)
        return self._make_request("GET", "/spending/limits", headers=headers)

    def update_spending_limits_owner(self, daily_limit: float, monthly_limit: float, jwt_token: str) -> Dict[str, Any]:
        headers = self._with_jwt(jwt_token)
        body = {"daily_limit": daily_limit, "monthly_limit": monthly_limit}
        return self._make_request("PUT", "/spending/limits", headers=headers, json=body)

    # ---------------- Webhooks Ops (Owner or API key) ----------------
    def list_webhooks(self, agent_id: Optional[str] = None, jwt_token: Optional[str] = None) -> Dict[str, Any]:
        agent = agent_id or self.agent_id
        headers = self._with_jwt(jwt_token)
        return self._make_request("GET", f"/agents/{agent}/webhooks", headers=headers)

    def create_webhook(self, url: str, event_types: Optional[list] = None, secret: Optional[str] = None, agent_id: Optional[str] = None, jwt_token: Optional[str] = None) -> Dict[str, Any]:
        agent = agent_id or self.agent_id
        headers = self._with_jwt(jwt_token)
        body: Dict[str, Any] = {"url": url}
        if secret:
            body["secret"] = secret
        if event_types:
            body["event_types"] = event_types
        return self._make_request("POST", f"/agents/{agent}/webhooks", headers=headers, json=body)

    def rotate_webhook_secret(self, subscription_id: str, agent_id: Optional[str] = None, jwt_token: Optional[str] = None) -> Dict[str, Any]:
        agent = agent_id or self.agent_id
        headers = self._with_jwt(jwt_token)
        return self._make_request("POST", f"/agents/{agent}/webhooks/{subscription_id}/rotate", headers=headers)

    def pause_webhook(self, subscription_id: str, agent_id: Optional[str] = None, jwt_token: Optional[str] = None) -> Dict[str, Any]:
        agent = agent_id or self.agent_id
        headers = self._with_jwt(jwt_token)
        return self._make_request("POST", f"/agents/{agent}/webhooks/{subscription_id}/pause", headers=headers)

    def resume_webhook(self, subscription_id: str, agent_id: Optional[str] = None, jwt_token: Optional[str] = None) -> Dict[str, Any]:
        agent = agent_id or self.agent_id
        headers = self._with_jwt(jwt_token)
        return self._make_request("POST", f"/agents/{agent}/webhooks/{subscription_id}/resume", headers=headers)

    def send_test_webhook(self, agent_id: Optional[str] = None, jwt_token: Optional[str] = None) -> Dict[str, Any]:
        agent = agent_id or self.agent_id
        headers = self._with_jwt(jwt_token)
        return self._make_request("POST", f"/agents/{agent}/webhooks/test", headers=headers)

    def list_webhook_deliveries(self, status: Optional[str] = None, limit: int = 50, agent_id: Optional[str] = None, jwt_token: Optional[str] = None) -> Dict[str, Any]:
        agent = agent_id or self.agent_id
        headers = self._with_jwt(jwt_token)
        params: Dict[str, Any] = {"limit": limit}
        if status:
            params["status"] = status
        return self._make_request("GET", f"/agents/{agent}/webhooks/deliveries", headers=headers, params=params)

    def replay_webhook_delivery(self, delivery_id: str, agent_id: Optional[str] = None, jwt_token: Optional[str] = None) -> Dict[str, Any]:
        agent = agent_id or self.agent_id
        headers = self._with_jwt(jwt_token)
        return self._make_request("POST", f"/agents/{agent}/webhooks/deliveries/{delivery_id}/replay", headers=headers)

    # --------------------------------------------------------------------
    # Pollable inbox helpers
    # --------------------------------------------------------------------
    def list_agent_events(
        self,
        *,
        types: Optional[list] = None,
        after: Optional[str] = None,
        limit: int = 50,
    ) -> list:
        params: Dict[str, Any] = {"limit": limit}
        if types:
            params["types"] = ",".join(types)
        if after:
            params["after"] = after

        result = self._make_request("GET", f"/agents/{self.agent_id}/events", params=params)
        events: list = []
        for e in result:
            events.append(AgentEvent(
                event_id=e["event_id"],
                type=e["type"],
                payload=e.get("payload", {}),
                status=e["status"],
                attempt_count=e.get("attempt_count", 0),
                created_at=e["created_at"] if isinstance(e["created_at"], str) else str(e["created_at"]),
            ))
        return events

    def ack_agent_event(self, event_id: str) -> Dict[str, Any]:
        return self._make_request("POST", f"/agents/{self.agent_id}/events/{event_id}/ack")

    def create_a2a_payment(self, recipient_id: str, amount: int, 
                          currency: str = "usd", memo: Optional[str] = None) -> Dict[str, Any]:
        """Create a legacy agent-to-agent payment (deprecated - use pay_supplier instead)"""
        data = {
            "agent_id": self.agent_id,
            "recipient_id": recipient_id,
            "amount": amount,
            "currency": currency,
            "memo": memo
        }
        
        return self._make_request("POST", "/a2a/payment", json=data)
    
    def pay_supplier(self, supplier: str, amount: int, description: str, 
                    agent_owner_email: str, agent_id: str,
                    currency: str = "usd", txn_id: Optional[str] = None,
                    agent_description: Optional[str] = None,
                    company_name: Optional[str] = None) -> A2APaymentResponse:
        """
        Pay a supplier using the A2A protocol
        
        Args:
            supplier: Domain name of the supplier (e.g., "acme-corp.com")
            amount: Amount in cents
            description: Description of the payment
            agent_owner_email: REQUIRED - Email of agent owner (from SSO)
            agent_id: REQUIRED - Agent identifier (unique per owner)
            currency: Currency code (default: "usd")
            txn_id: Optional client-generated transaction ID
            agent_description: Optional agent description
            company_name: Optional company name
            
        Returns:
            A2APaymentResponse with transaction details
        """
        if txn_id is None:
            txn_id = f"agt_txn_{uuid.uuid4().hex[:12]}"
            
        data = {
            "msg": "PayRequest",
            "version": "1.0",
            "txn_id": txn_id,
            "supplier": supplier,
            "amount": amount,
            "currency": currency,
            "description": description,
            "api_key": self.api_key,
            "agent_owner_email": agent_owner_email,
            "agent_id": agent_id
        }
        
        # Add optional fields if provided
        if agent_description:
            data["agent_description"] = agent_description
        if company_name:
            data["company_name"] = company_name
        
        result = self._make_request("POST", "/a2a/pay", json=data)
        
        return A2APaymentResponse(
            txn_id=result["txn_id"],
            status=result["status"],
            msg=result.get("msg", "PayResponse"),
            provisional_key=result.get("provisional_key"),
            next_action_url=result.get("next_action_url"),
            error=result.get("error")
        )
    
    def check_a2a_status(self, txn_id: str) -> A2AStatusResponse:
        """
        Check the status of an A2A payment transaction
        
        Args:
            txn_id: Transaction ID to check
            
        Returns:
            A2AStatusResponse with current status and events
        """
        data = {
            "msg": "StatusQuery",
            "txn_id": txn_id
        }
        
        result = self._make_request("POST", "/a2a/status", json=data)
        
        return A2AStatusResponse(
            txn_id=result["txn_id"],
            status=result["status"],
            events=result.get("events", []),
            msg=result.get("msg", "StatusResponse")
        ) 

    def create_ap2_intent_mandate(
        self,
        *,
        policy: Dict[str, Any],
        agent_id: Optional[str] = None,
        constraints: Optional[Dict[str, Any]] = None,
        expires_at: Optional[Union[str, datetime]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> IntentMandate:
        """Create an AP2 intent mandate binding a policy to an agent."""

        payload: Dict[str, Any] = {
            "agent_id": agent_id or self.agent_id,
            "policy": policy,
        }
        if constraints:
            payload["constraints"] = constraints
        if metadata:
            payload["metadata"] = metadata
        if expires_at:
            payload["expires_at"] = (
                expires_at.isoformat()
                if isinstance(expires_at, datetime)
                else expires_at
            )

        result = self._make_request("POST", "/ap2/mandates/intent", json=payload)
        mandate = result.get("intent_mandate", {})
        return IntentMandate(
            id=mandate.get("id"),
            status=mandate.get("status", "unknown"),
            policy=mandate.get("policy", {}),
            subject=mandate.get("subject", {}),
            hash=mandate.get("hash"),
            metadata=mandate.get("metadata"),
        )

    def create_ap2_cart_mandate(
        self,
        *,
        intent_mandate_id: str,
        cart: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> CartMandate:
        """Create an AP2 cart mandate that links to an intent."""

        payload: Dict[str, Any] = {
            "intent_mandate_id": intent_mandate_id,
            "cart": cart,
        }
        if metadata:
            payload["metadata"] = metadata

        result = self._make_request("POST", "/ap2/mandates/cart", json=payload)
        cart_mandate = result.get("cart_mandate", {})
        return CartMandate(
            id=cart_mandate.get("id"),
            status=cart_mandate.get("status", "unknown"),
            cart=cart_mandate.get("cart", {}),
            links=cart_mandate.get("links", {}),
            hash=cart_mandate.get("hash"),
            metadata=cart_mandate.get("metadata"),
        )

    def get_ap2_signing_digest(self, *, intent_mandate_id: str, cart_mandate_id: str, destination_wallet: str) -> Dict[str, Any]:
        """Optional zero-trust helper: fetch canonical digest to sign for stablecoin payments."""
        body = {
            "intent_mandate_id": intent_mandate_id,
            "cart_mandate_id": cart_mandate_id,
            "destination_wallet": destination_wallet,
        }
        return self._make_request("POST", "/ap2/signing-digest", json=body)

    def ap2_pay(
        self,
        *,
        intent_mandate_id: str,
        cart_mandate_id: str,
        payment_method: Union[PaymentMethodPayload, Dict[str, Any]],
        idempotency_key: Optional[str] = None,
    ) -> Any:
        """Execute an AP2 payment for the given mandates."""

        if isinstance(payment_method, PaymentMethodPayload):
            method_payload = payment_method.to_dict()
        else:
            method_payload = payment_method

        headers: Dict[str, str] = {}
        if idempotency_key:
            headers["Idempotency-Key"] = idempotency_key

        result = self._make_request(
            "POST",
            "/ap2/pay",
            headers=headers or None,
            json={
                "intent_mandate_id": intent_mandate_id,
                "cart_mandate_id": cart_mandate_id,
                "payment_method": method_payload,
            },
        )
        if isinstance(result, dict) and result.get("approval_required"):
            return {
                "approval_required": True,
                "request_id": result.get("request_id"),
                "policy": result.get("policy"),
            }

        return AP2PaymentResult(
            status=result.get("status", "processing"),
            rail=result.get("rail", method_payload.get("rail", "unknown")),
            processor=result.get("processor", "unknown"),
            processor_ref=result.get("processor_ref"),
            receipt=result.get("receipt", {}),
            onchain_txid=result.get("onchain_txid"),
        )

    # ========================================================================
    # Gap 2: Service Catalog Methods
    # ========================================================================

    def register_service(self, service: ServiceRegistration) -> ServiceDetails:
        """
        Register a new service in the catalog.

        Args:
            service: ServiceRegistration with all service details

        Returns:
            ServiceDetails of the registered service
        """
        data = {
            "service_name": service.service_name,
            "description": service.description,
            "category": service.category,
            "price_model": service.price_model,
            "base_price_cents": service.base_price_cents,
            "unit": service.unit,
            "min_quantity": service.min_quantity
        }

        if service.max_quantity is not None:
            data["max_quantity"] = service.max_quantity
        if service.capabilities:
            data["capabilities"] = service.capabilities
        if service.metadata:
            data["metadata"] = service.metadata

        result = self._make_request("POST", "/agents/services", json=data)

        return ServiceDetails(
            service_id=result["service_id"],
            agent_id=result["agent_id"],
            service_name=result["service_name"],
            description=result["description"],
            category=result["category"],
            price_model=result["price_model"],
            base_price_cents=result["base_price_cents"],
            unit=result["unit"],
            min_quantity=result["min_quantity"],
            max_quantity=result.get("max_quantity"),
            capabilities=result.get("capabilities"),
            metadata=result.get("metadata"),
            is_active=result.get("is_active", True),
            created_at=result["created_at"],
            updated_at=result["updated_at"]
        )

    def update_service(
        self,
        service_id: str,
        service_name: Optional[str] = None,
        description: Optional[str] = None,
        base_price_cents: Optional[int] = None,
        min_quantity: Optional[int] = None,
        max_quantity: Optional[int] = None,
        capabilities: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Update an existing service (partial updates supported).

        Args:
            service_id: ID of service to update
            service_name: New service name (optional)
            description: New description (optional)
            base_price_cents: New price (optional)
            min_quantity: New min quantity (optional)
            max_quantity: New max quantity (optional)
            capabilities: New capabilities (optional)
            metadata: New metadata (optional)

        Returns:
            Update response with success status
        """
        data = {}

        if service_name is not None:
            data["service_name"] = service_name
        if description is not None:
            data["description"] = description
        if base_price_cents is not None:
            data["base_price_cents"] = base_price_cents
        if min_quantity is not None:
            data["min_quantity"] = min_quantity
        if max_quantity is not None:
            data["max_quantity"] = max_quantity
        if capabilities is not None:
            data["capabilities"] = capabilities
        if metadata is not None:
            data["metadata"] = metadata

        return self._make_request("PUT", f"/agents/services/{service_id}", json=data)

    def delete_service(self, service_id: str) -> Dict[str, Any]:
        """
        Deactivate a service (soft delete).

        Args:
            service_id: ID of service to deactivate

        Returns:
            Deletion response with success status
        """
        return self._make_request("DELETE", f"/agents/services/{service_id}")

    def get_service(self, service_id: str) -> ServiceDetails:
        """
        Get details of a specific service.

        Args:
            service_id: ID of service to retrieve

        Returns:
            ServiceDetails of the requested service
        """
        result = self._make_request("GET", f"/agents/services/{service_id}")

        return ServiceDetails(
            service_id=result["service_id"],
            agent_id=result["agent_id"],
            service_name=result["service_name"],
            description=result["description"],
            category=result["category"],
            price_model=result["price_model"],
            base_price_cents=result["base_price_cents"],
            unit=result["unit"],
            min_quantity=result["min_quantity"],
            max_quantity=result.get("max_quantity"),
            capabilities=result.get("capabilities"),
            metadata=result.get("metadata"),
            is_active=result.get("is_active", True),
            created_at=result["created_at"],
            updated_at=result["updated_at"]
        )

    def list_my_services(self, limit: int = 100, offset: int = 0) -> list:
        """
        List all services registered by this agent.

        Args:
            limit: Maximum number of results (default: 100)
            offset: Pagination offset (default: 0)

        Returns:
            List of ServiceDetails
        """
        params = {"limit": limit, "offset": offset}
        result = self._make_request("GET", "/agents/services", params=params)

        return [
            ServiceDetails(
                service_id=s["service_id"],
                agent_id=s["agent_id"],
                service_name=s["service_name"],
                description=s["description"],
                category=s["category"],
                price_model=s["price_model"],
                base_price_cents=s["base_price_cents"],
                unit=s["unit"],
                min_quantity=s["min_quantity"],
                max_quantity=s.get("max_quantity"),
                capabilities=s.get("capabilities"),
                metadata=s.get("metadata"),
                is_active=s.get("is_active", True),
                created_at=s["created_at"],
                updated_at=s["updated_at"]
            )
            for s in result.get("services", [])
        ]

    def search_services(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
        min_price: Optional[int] = None,
        max_price: Optional[int] = None,
        limit: int = 50,
        offset: int = 0
    ) -> CatalogSearchResult:
        """
        Search the service catalog.

        Args:
            query: Full-text search query (optional)
            category: Filter by category (optional)
            min_price: Minimum price in cents (optional)
            max_price: Maximum price in cents (optional)
            limit: Maximum results (default: 50)
            offset: Pagination offset (default: 0)

        Returns:
            CatalogSearchResult with matching services
        """
        data = {
            "limit": limit,
            "offset": offset
        }

        if query:
            data["query"] = query
        if category:
            data["category"] = category
        if min_price is not None:
            data["min_price"] = min_price
        if max_price is not None:
            data["max_price"] = max_price

        result = self._make_request("POST", "/catalog/search", json=data)

        # Convert results to ServiceDetails
        services = []
        for s in result.get("results", []):
            services.append(ServiceDetails(
                service_id=s["service_id"],
                agent_id=s["agent_id"],
                service_name=s["service_name"],
                description=s["description"],
                category=s["category"],
                price_model=s["price_model"],
                base_price_cents=s["base_price_cents"],
                unit=s["unit"],
                min_quantity=s["min_quantity"],
                max_quantity=s.get("max_quantity"),
                capabilities=s.get("capabilities"),
                metadata=s.get("metadata"),
                is_active=s.get("is_active", True),
                created_at=s["created_at"],
                updated_at=s["updated_at"]
            ))

        return CatalogSearchResult(
            total=result["total"],
            results=services,
            query=result["query"],
            has_more=result["has_more"],
            next_offset=result.get("next_offset")
        )

    # ========================================================================
    # Gap 3: Usage Agreement / Escrow Methods
    # ========================================================================

    def create_usage_agreement(self, request: UsageAgreementRequest) -> UsageAgreement:
        """
        Create a prepaid usage agreement (buyer action).

        Args:
            request: UsageAgreementRequest with all agreement details

        Returns:
            UsageAgreement with agreement details
        """
        data = {
            "seller_agent_id": request.seller_agent_id,
            "quantity": request.quantity,
            "unit": request.unit,
            "price_per_unit_cents": request.price_per_unit_cents,
            "payment_method": request.payment_method,
            "expires_in_seconds": int(request.expires_in_hours) * 3600,
        }

        if request.service_description:
            data["service_description"] = request.service_description
        # Merge metadata with cart_items if provided
        meta: Dict[str, Any] = dict(request.metadata or {})
        if request.cart_items:
            meta["cart_items"] = request.cart_items
        if meta:
            data["metadata"] = meta
        if request.client_proposal_id:
            data["client_proposal_id"] = request.client_proposal_id

        idem_key = request.client_proposal_id or f"agree:{uuid.uuid4().hex}"
        headers = {"Idempotency-Key": idem_key}

        result = self._make_request("POST", "/usage-agreements", json=data, headers=headers)

        return self._parse_usage_agreement(result)

    def get_usage_agreement(self, agreement_id: str) -> UsageAgreement:
        """
        Get details of a usage agreement.

        Args:
            agreement_id: ID of agreement to retrieve

        Returns:
            UsageAgreement details
        """
        result = self._make_request("GET", f"/usage-agreements/{agreement_id}")
        return self._parse_usage_agreement(result)

    def list_usage_agreements(
        self,
        role: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100
    ) -> list:
        """
        List usage agreements for this agent (as buyer or seller).

        Args:
            status: Filter by status (optional)
            limit: Maximum results (default: 100)

        Returns:
            List of UsageAgreement objects
        """
        params = {"limit": limit}
        if status:
            params["status"] = status
        if role:
            params["role"] = role

        path = f"/usage-agreements/agents/{self.agent_id}/agreements"
        result = self._make_request("GET", path, params=params)
        return [self._parse_usage_agreement(a) for a in result]

    def accept_usage_agreement(self, agreement_id: str) -> UsageAgreement:
        """
        Accept a usage agreement and fund escrow (seller action).

        This triggers:
        1. Agreement marked as accepted
        2. A2A payment from buyer to escrow
        3. Agreement marked as active/funded

        Args:
            agreement_id: ID of agreement to accept

        Returns:
            Updated UsageAgreement
        """
        headers = {"Idempotency-Key": f"accept:{agreement_id}"}
        self._make_request("PUT", f"/usage-agreements/{agreement_id}/accept", headers=headers)
        return self.get_usage_agreement(agreement_id)

    def reject_usage_agreement(self, agreement_id: str) -> Dict[str, Any]:
        """Reject a usage agreement (seller action)."""
        headers = {"Idempotency-Key": f"reject:{agreement_id}"}
        return self._make_request("PUT", f"/usage-agreements/{agreement_id}/reject", headers=headers)

    def record_usage(
        self,
        agreement_id: str,
        request: RecordUsageRequest
    ) -> UsageAgreement:
        """
        Record usage and optionally complete agreement (seller action).

        If completed=True, triggers:
        - Proportional payment release to seller
        - Automatic refund for unused portion

        Args:
            agreement_id: ID of agreement
            request: RecordUsageRequest with usage details

        Returns:
            Updated UsageAgreement
        """
        data = {
            "units_used": request.units_used,
            "completed": request.completed
        }

        if request.usage_proof:
            data["usage_proof"] = request.usage_proof

        result = self._make_request(
            "POST",
            f"/usage-agreements/{agreement_id}/record-usage",
            json=data
        )

        return self._parse_usage_agreement(result)

    def cancel_usage_agreement(self, agreement_id: str) -> Dict[str, Any]:
        """
        Cancel a usage agreement before acceptance (buyer only).

        Only works if status is 'proposed'.

        Args:
            agreement_id: ID of agreement to cancel

        Returns:
            Cancellation response
        """
        return self._make_request("POST", f"/usage-agreements/{agreement_id}/cancel")

    def dispute_usage_agreement(
        self,
        agreement_id: str,
        reason: str,
        evidence: Optional[Dict[str, Any]] = None
    ) -> UsageAgreement:
        """
        Dispute a usage agreement (buyer action).

        Holds escrow until admin resolves.

        Args:
            agreement_id: ID of agreement to dispute
            reason: Dispute reason (min 10 characters)
            evidence: Optional evidence dict

        Returns:
            Updated UsageAgreement
        """
        data = {"reason": reason}
        if evidence:
            data["evidence"] = evidence

        result = self._make_request(
            "POST",
            f"/usage-agreements/{agreement_id}/dispute",
            json=data
        )

        return self._parse_usage_agreement(result)

    def reject_usage_agreement_with_suggestions(
        self,
        agreement_id: str,
        *,
        reason: Optional[str] = None,
        suggested_cart_items: Optional[list] = None,
        suggested_total_cents: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Reject an agreement with optional suggestions (seller action)."""
        headers = {"Idempotency-Key": f"reject:{agreement_id}"}
        body: Dict[str, Any] = {}
        if reason:
            body["reason"] = reason
        if suggested_cart_items:
            body["suggested_cart_items"] = suggested_cart_items
        if suggested_total_cents is not None:
            body["suggested_total_cents"] = suggested_total_cents
        return self._make_request("PUT", f"/usage-agreements/{agreement_id}/reject", headers=headers, json=body)

    # ---------------- Policies & Approvals (owner JWT) ----------------
    def get_agent_policies(self, agent_id: Optional[str] = None, jwt_token: Optional[str] = None) -> Dict[str, Any]:
        agent = agent_id or self.agent_id
        headers = {"Authorization": f"Bearer {jwt_token}"} if jwt_token else None
        return self._make_request("GET", f"/agents/{agent}/policies", headers=headers)

    def update_agent_policies(self, policy: Dict[str, Any], agent_id: Optional[str] = None, jwt_token: Optional[str] = None) -> Dict[str, Any]:
        agent = agent_id or self.agent_id
        headers = {"Authorization": f"Bearer {jwt_token}"} if jwt_token else None
        return self._make_request("PUT", f"/agents/{agent}/policies", headers=headers, json=policy)

    def list_approvals(self, status: Optional[str] = None, limit: int = 50, agent_id: Optional[str] = None, jwt_token: Optional[str] = None) -> Dict[str, Any]:
        agent = agent_id or self.agent_id
        params: Dict[str, Any] = {"limit": limit}
        if status:
            params["status"] = status
        headers = {"Authorization": f"Bearer {jwt_token}"} if jwt_token else None
        return self._make_request("GET", f"/agents/{agent}/approvals", headers=headers, params=params)

    def approve_approval(self, request_id: str, agent_id: Optional[str] = None, jwt_token: Optional[str] = None) -> Dict[str, Any]:
        agent = agent_id or self.agent_id
        headers = {"Authorization": f"Bearer {jwt_token}"} if jwt_token else None
        return self._make_request("POST", f"/agents/{agent}/approvals/{request_id}/approve", headers=headers)

    def reject_approval(self, request_id: str, agent_id: Optional[str] = None, jwt_token: Optional[str] = None, reason: Optional[str] = None) -> Dict[str, Any]:
        agent = agent_id or self.agent_id
        headers = {"Authorization": f"Bearer {jwt_token}"} if jwt_token else None
        path = f"/agents/{agent}/approvals/{request_id}/reject"
        if reason:
            return self._make_request("POST", f"{path}?reason={requests.utils.quote(reason)}", headers=headers)
        return self._make_request("POST", path, headers=headers)

    def _parse_usage_agreement(self, data: Dict[str, Any]) -> UsageAgreement:
        """Helper to parse API response into UsageAgreement object"""
        return UsageAgreement(
            agreement_id=data["agreement_id"],
            buyer_agent_id=data["buyer_agent_id"],
            seller_agent_id=data["seller_agent_id"],
            quantity=data["quantity"],
            unit=data["unit"],
            price_per_unit_cents=data["price_per_unit_cents"],
            total_cents=data["total_cents"],
            payment_method=data.get("payment_method"),
            status=data["status"],
            service_description=data.get("service_description"),
            expires_at=data["expires_at"],
            created_at=data.get("created_at"),
            units_used=data.get("units_used"),
            escrow_payment_id=data.get("escrow_payment_id"),
            released_cents=data.get("released_cents"),
            seller_receipt_id=data.get("seller_receipt_id"),
            buyer_receipt_id=data.get("buyer_receipt_id"),
            metadata=data.get("metadata")
        )

    # ========================================================================
    # Metered Proxy Client
    # ========================================================================

    def create_metered_client(self, agreement_id: str) -> 'MeteredClient':
        """
        Create a metered API client for automatic usage tracking.

        This client wraps buyer requests to seller APIs, automatically tracking
        usage and capturing payments through Paegents' metered proxy.

        Features:
        - Automatic usage tracking (tamper-proof)
        - Custom usage units support (via X-Usage-Units header)
        - Response caching for GET requests
        - Replay protection with nonces
        - All existing security features (auth, rate limiting, escrow caps)

        Args:
            agreement_id: The usage agreement ID to track usage against

        Returns:
            MeteredClient instance for making metered API calls

        Example:
            ```python
            # Create metered client
            client = sdk.create_metered_client("agr_123")

            # Make requests (automatically tracked)
            result = client.post("/generate", json={"prompt": "hello"})

            # Check usage
            status = client.get_usage_status()
            print(f"Used: {status['units_used']}/{status['units_total']}")
            ```
        """
        return MeteredClient(self, agreement_id)


@dataclass
class MeteredUsageStatus:
    """Usage status for a metered agreement"""
    agreement_id: str
    units_used: int
    units_total: int
    units_remaining: int
    status: str
    escrow_status: str
    unit: str
    price_per_unit_cents: int


class MeteredClient:
    """
    HTTP client for metered API usage with automatic tracking.

    Proxies requests through Paegents to automatically track usage
    and capture payments based on actual API consumption.
    """

    def __init__(self, sdk: AgentPaymentsSDK, agreement_id: str):
        """
        Initialize metered client.

        Args:
            sdk: Parent AgentPaymentsSDK instance
            agreement_id: Usage agreement ID
        """
        self.sdk = sdk
        self.agreement_id = agreement_id
        self.base_url = f"{sdk.api_url}/metered-proxy/{agreement_id}"

    def get(self, path: str, **kwargs) -> Any:
        """
        Make a GET request through the metered proxy.

        GET requests are cached for 5 seconds and only charge once.

        Args:
            path: Path on seller's API (e.g., "/search")
            **kwargs: Additional arguments passed to requests.request()

        Returns:
            Response data (JSON)

        Example:
            ```python
            results = client.get("/search", params={"query": "test", "limit": 10})
            ```
        """
        return self._request("GET", path, **kwargs)

    def post(self, path: str, json: Optional[Dict[str, Any]] = None, **kwargs) -> Any:
        """
        Make a POST request through the metered proxy.

        Args:
            path: Path on seller's API (e.g., "/generate")
            json: JSON request body
            **kwargs: Additional arguments passed to requests.request()

        Returns:
            Response data (JSON)

        Example:
            ```python
            result = client.post("/generate", json={
                "prompt": "a cat wearing a hat",
                "max_tokens": 100
            })
            ```
        """
        if json is not None:
            kwargs["json"] = json
        return self._request("POST", path, **kwargs)

    def put(self, path: str, json: Optional[Dict[str, Any]] = None, **kwargs) -> Any:
        """
        Make a PUT request through the metered proxy.

        Args:
            path: Path on seller's API
            json: JSON request body
            **kwargs: Additional arguments passed to requests.request()

        Returns:
            Response data (JSON)
        """
        if json is not None:
            kwargs["json"] = json
        return self._request("PUT", path, **kwargs)

    def delete(self, path: str, **kwargs) -> Any:
        """
        Make a DELETE request through the metered proxy.

        Args:
            path: Path on seller's API
            **kwargs: Additional arguments passed to requests.request()

        Returns:
            Response data (JSON)
        """
        return self._request("DELETE", path, **kwargs)

    def patch(self, path: str, json: Optional[Dict[str, Any]] = None, **kwargs) -> Any:
        """
        Make a PATCH request through the metered proxy.

        Args:
            path: Path on seller's API
            json: JSON request body
            **kwargs: Additional arguments passed to requests.request()

        Returns:
            Response data (JSON)
        """
        if json is not None:
            kwargs["json"] = json
        return self._request("PATCH", path, **kwargs)

    def get_usage_status(self) -> MeteredUsageStatus:
        """
        Get current usage status for this agreement.

        Returns:
            MeteredUsageStatus with usage details

        Example:
            ```python
            status = client.get_usage_status()
            print(f"Used {status.units_used} of {status.units_total} {status.unit}s")
            print(f"Remaining: {status.units_remaining}")
            ```
        """
        url = f"{self.base_url}/status"
        nonce = self._generate_nonce()

        headers = {
            "Content-Type": "application/json",
            "X-Request-Nonce": nonce,
            "Authorization": f"Bearer {self.sdk.api_key}",
        }

        response = requests.get(url, headers=headers)

        if not response.ok:
            try:
                body = response.json()
                detail = body.get("detail") if isinstance(body, dict) else None
            except Exception:
                detail = None
            msg = detail or response.text
            raise ApiError(f"Failed to get usage status: {msg}", response.status_code)

        data = response.json()

        return MeteredUsageStatus(
            agreement_id=data["agreement_id"],
            units_used=data["units_used"],
            units_total=data["units_total"],
            units_remaining=data["units_remaining"],
            status=data["status"],
            escrow_status=data["escrow_status"],
            unit=data["unit"],
            price_per_unit_cents=data["price_per_unit_cents"]
        )

    def _request(self, method: str, path: str, **kwargs) -> Any:
        """
        Internal method to make proxied requests with automatic nonce generation.

        Args:
            method: HTTP method
            path: Path on seller's API
            **kwargs: Additional arguments passed to requests.request()

        Returns:
            Response data (JSON)
        """
        # Build URL
        clean_path = path.lstrip("/")
        url = f"{self.base_url}/{clean_path}"

        # Generate nonce for replay protection
        nonce = self._generate_nonce()

        # Prepare headers
        headers = kwargs.pop("headers", {})
        headers.update({
            "Content-Type": "application/json",
            "X-Request-Nonce": nonce,
            "Authorization": f"Bearer {self.sdk.api_key}",
        })

        # Make request
        response = requests.request(method, url, headers=headers, **kwargs)

        # Handle errors
        if not response.ok:
            try:
                body = response.json()
                detail = body.get("detail") if isinstance(body, dict) else None
            except Exception:
                body = None
                detail = None
            msg = detail or response.text
            raise ApiError(f"Metered proxy request failed: {msg}", response.status_code, body)

        # Return JSON response
        try:
            return response.json()
        except Exception:
            # Some endpoints may return non-JSON
            return response.text

    def _generate_nonce(self) -> str:
        """Generate a unique nonce for replay protection"""
        return str(uuid.uuid4())
