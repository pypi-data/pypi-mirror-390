# Paegents Python SDK
from .agent_payments import (
    # Main SDK class
    AgentPaymentsSDK,
    
    # Legacy MCP models
    PaymentRequest,
    PaymentResponse,
    RecipientSearchResult,
    Receipt,
    SpendingLimits,
    
    # A2A Protocol models
    A2APaymentRequest,
    A2APaymentResponse, 
    A2AStatusQuery,
    A2AStatusResponse,

    # AP2 / x402 helpers
    IntentMandate,
    CartMandate,
    AP2PaymentResult,
    PaymentMethodPayload,
    build_card_payment_method,
    build_braintree_payment_method,
    build_stablecoin_payment_method,
    # Errors
    ApiError,
    PolicyDeniedError,
)

__version__ = "2.1.0"
__author__ = "Paegents Inc"
__email__ = "support@paegents.com"

# Convenience alias
PaegentsSDK = AgentPaymentsSDK

__all__ = [
    "AgentPaymentsSDK",
    "PaegentsSDK",
    "PaymentRequest",
 
    "PaymentResponse",
    "RecipientSearchResult",
    "Receipt",
    "SpendingLimits",
    "A2APaymentRequest",
    "A2APaymentResponse",
    "A2AStatusQuery", 
    "A2AStatusResponse",
    "IntentMandate",
    "CartMandate",
    "AP2PaymentResult",
    "PaymentMethodPayload",
    "build_card_payment_method",
    "build_braintree_payment_method",
    "build_stablecoin_payment_method",
    "ApiError",
    "PolicyDeniedError",
]
