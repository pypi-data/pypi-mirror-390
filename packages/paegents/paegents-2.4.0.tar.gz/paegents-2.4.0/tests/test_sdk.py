import unittest
from unittest.mock import Mock, patch
import json
from agent_payments import (
    AgentPaymentsSDK,
    PaymentRequest,
    A2APaymentRequest,
    PaymentResponse,
    A2APaymentResponse,
    build_card_payment_method,
    build_braintree_payment_method,
    build_stablecoin_payment_method,
    PolicyDeniedError,
)


class TestAgentPaymentsSDK(unittest.TestCase):
    def setUp(self):
        self.sdk = AgentPaymentsSDK(
            api_url="https://api.example.com",
            agent_id="test-agent",
            api_key="test-key"
        )

    def test_init(self):
        """Test SDK initialization"""
        self.assertEqual(self.sdk.api_url, "https://api.example.com")
        self.assertEqual(self.sdk.agent_id, "test-agent")
        self.assertEqual(self.sdk.api_key, "test-key")
        self.assertEqual(
            self.sdk.session.headers["Authorization"],
            "Bearer test-key"
        )

    @patch('requests.Session.request')
    def test_make_request_success(self, mock_request):
        """Test successful API request"""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {"success": True}
        mock_request.return_value = mock_response

        result = self.sdk._make_request("GET", "/test")

        self.assertEqual(result, {"success": True})
        mock_request.assert_called_once_with(
            "GET", "https://api.example.com/test"
        )

    @patch('requests.Session.request')
    def test_make_request_failure(self, mock_request):
        """Test failed API request"""
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_request.return_value = mock_response

        with self.assertRaises(Exception) as context:
            self.sdk._make_request("GET", "/test")

        self.assertIn("API request failed: 400", str(context.exception))

    @patch('requests.Session.request')
    def test_create_payment(self, mock_request):
        """Test payment creation"""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {
            "payment_intent": {
                "id": "pi_123",
                "client_secret": "secret_123",
                "status": "requires_payment_method"
            },
            "receipt": {"receipt_id": "rec_123"}
        }
        mock_request.return_value = mock_response

        request = PaymentRequest(
            agent_id="test-agent",
            amount=1000,
            description="Test payment",
            recipient_email="test@example.com"
        )

        result = self.sdk.create_payment(request)

        self.assertIsInstance(result, PaymentResponse)
        self.assertEqual(result.payment_intent_id, "pi_123")
        self.assertEqual(result.client_secret, "secret_123")
        self.assertEqual(result.status, "requires_payment_method")

    @patch('requests.Session.request')
    def test_pay_supplier_a2a(self, mock_request):
        """Test A2A supplier payment"""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {
            "txn_id": "agt_txn_123",
            "status": "processing",
            "msg": "PayResponse"
        }
        mock_request.return_value = mock_response

        result = self.sdk.pay_supplier(
            supplier="supplier.com",
            amount=5000,
            description="Payment for services",
            agent_owner_email="owner@example.com",
            agent_id="agent-123"
        )

        self.assertIsInstance(result, A2APaymentResponse)
        self.assertEqual(result.txn_id, "agt_txn_123")
        self.assertEqual(result.status, "processing")

        # Verify the request was made correctly
        call_args = mock_request.call_args
        self.assertEqual(call_args[0][0], "POST")
        self.assertEqual(call_args[0][1], "https://api.example.com/a2a/pay")
        
        # Check the request body
        body = call_args[1]["json"]
        self.assertEqual(body["supplier"], "supplier.com")
        self.assertEqual(body["amount"], 5000)
        self.assertEqual(body["agent_owner_email"], "owner@example.com")

    @patch('requests.Session.request')
    def test_ap2_payment_flow(self, mock_request):
        """Test complete AP2 payment flow"""
        # Mock intent creation
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {
            "intent_mandate": {
                "id": "intent_123",
                "status": "active",
                "policy": {"max_amount": {"value": 1000}},
                "subject": {"user_id": "user_123", "agent_id": "agent_123"}
            }
        }
        mock_request.return_value = mock_response

        intent = self.sdk.create_ap2_intent_mandate(
            policy={"max_amount": {"value": 1000}},
            agent_id="agent_123"
        )

        self.assertEqual(intent.id, "intent_123")
        self.assertEqual(intent.status, "active")

        # Mock cart creation
        mock_response.json.return_value = {
            "cart_mandate": {
                "id": "cart_123",
                "status": "active",
                "cart": {"total": 500, "currency": "usd"},
                "links": {"intent_mandate_id": "intent_123"}
            }
        }

        cart = self.sdk.create_ap2_cart_mandate(
            intent_mandate_id="intent_123",
            cart={"total": 500, "currency": "usd"}
        )

        self.assertEqual(cart.id, "cart_123")
        self.assertEqual(cart.status, "active")

        # Mock payment execution
        mock_response.json.return_value = {
            "status": "succeeded",
            "rail": "card",
            "processor": "stripe",
            "processor_ref": "pi_123",
            "receipt": {"receipt_id": "rec_123"}
        }

        payment_method = build_card_payment_method(provider="stripe")
        result = self.sdk.ap2_pay(
            intent_mandate_id="intent_123",
            cart_mandate_id="cart_123",
            payment_method=payment_method
        )

        self.assertEqual(result.status, "succeeded")
        self.assertEqual(result.rail, "card")
        self.assertEqual(result.processor, "stripe")

    @patch('requests.Session.request')
    def test_ap2_payment_approval_required(self, mock_request):
        """AP2 should return approval_required without raising"""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {
            "approval_required": True,
            "request_id": "appr_123",
            "policy": {"decision": "require_approval", "reason": "approval_threshold:3000>=2000", "rule": "approvals.threshold_cents"}
        }
        mock_request.return_value = mock_response

        res = self.sdk.ap2_pay(
            intent_mandate_id="intent_123",
            cart_mandate_id="cart_123",
            payment_method=build_card_payment_method()
        )
        self.assertIsInstance(res, dict)
        self.assertTrue(res.get("approval_required"))
        self.assertEqual(res.get("request_id"), "appr_123")

    @patch('requests.Session.request')
    def test_check_balance(self, mock_request):
        """Test balance checking"""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {
            "daily_limit": 10000,
            "monthly_limit": 100000,
            "daily_spent": 1000,
            "monthly_spent": 5000,
            "daily_remaining": 9000,
            "monthly_remaining": 95000
        }
        mock_request.return_value = mock_response

        result = self.sdk.check_balance()

        self.assertEqual(result.daily_limit, 10000)
        self.assertEqual(result.daily_spent, 1000)
        self.assertEqual(result.daily_remaining, 9000)

    @patch('requests.Session.request')
    def test_policies_owner_jwt_headers(self, mock_request):
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {"agent_id": "agent1", "policy": {}}
        mock_request.return_value = mock_response

        self.sdk.get_agent_policies(agent_id="agent1", jwt_token="jwt-token-123")
        call = mock_request.call_args
        headers = call[1].get('headers')
        self.assertEqual(headers.get('Authorization'), 'Bearer jwt-token-123')

    @patch('requests.Session.request')
    def test_usage_agreement_cart_items_merge(self, mock_request):
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {"agreement_id": "agr_1"}
        mock_request.return_value = mock_response

        from agent_payments import UsageAgreementRequest
        req = UsageAgreementRequest(
            seller_agent_id="seller",
            quantity=1,
            unit="api_calls",
            price_per_unit_cents=100,
            payment_method={"rail": "card"},
            cart_items=[{"description": "item", "quantity": 1, "amount_cents": 100}]
        )
        self.sdk.create_usage_agreement(req)
        call = mock_request.call_args
        body = call[1]['json']
        self.assertIn('metadata', body)
        self.assertIn('cart_items', body['metadata'])
        self.assertEqual(body['metadata']['cart_items'][0]['description'], 'item')

    @patch('requests.Session.request')
    def test_reject_usage_agreement_with_suggestions(self, mock_request):
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {"agreementId": "agr_1", "status": "rejected"}
        mock_request.return_value = mock_response

        self.sdk.reject_usage_agreement_with_suggestions(
            "agr_1",
            reason="Too expensive",
            suggested_total_cents=500
        )
        call = mock_request.call_args
        self.assertEqual(call[0][0], 'PUT')
        self.assertIn('/usage-agreements/agr_1/reject', call[0][1])
        headers = call[1]['headers']
        self.assertIn('Idempotency-Key', headers)
        body = call[1]['json']
        self.assertEqual(body['reason'], 'Too expensive')
        self.assertEqual(body['suggested_total_cents'], 500)

    @patch('requests.Session.request')
    def test_policy_denied_error_mapping(self, mock_request):
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 400
        mock_response.json.return_value = {"detail": "policy_denied:outside_allowed_schedule"}
        mock_request.return_value = mock_response

        with self.assertRaises(PolicyDeniedError):
            self.sdk.ap2_pay(
                intent_mandate_id="intent",
                cart_mandate_id="cart",
                payment_method=build_card_payment_method()
            )

    @patch('requests.Session.request')
    def test_approvals_and_spending_limits_owner(self, mock_request):
        # list approvals
        mock_response = Mock(); mock_response.ok = True; mock_response.json.return_value = {"approvals": [], "count": 0}
        mock_request.return_value = mock_response
        self.sdk.list_approvals(status='pending', limit=10, agent_id='agent1', jwt_token='jwt')
        call = mock_request.call_args
        self.assertIn('/agents/agent1/approvals', call[0][1])
        self.assertEqual(call[1]['headers'].get('Authorization'), 'Bearer jwt')

        # approve
        mock_response.json.return_value = {"approved": True}
        self.sdk.approve_approval('appr_1', agent_id='agent1', jwt_token='jwt')
        call = mock_request.call_args
        self.assertIn('/agents/agent1/approvals/appr_1/approve', call[0][1])

        # owner spending limits get/put
        mock_response.json.return_value = {"daily_limit": 25, "monthly_limit": 100, "current_daily_spent": 5, "current_monthly_spent": 20}
        res = self.sdk.get_spending_limits_owner('jwt')
        self.assertEqual(res['daily_limit'], 25)
        mock_response.json.return_value = {"daily_limit": 30, "monthly_limit": 120}
        self.sdk.update_spending_limits_owner(30, 120, 'jwt')
        call = mock_request.call_args
        self.assertEqual(call[0][0], 'PUT')
        self.assertIn('/spending/limits', call[0][1])

    @patch('requests.Session.request')
    def test_webhooks_ops(self, mock_request):
        mock_response = Mock(); mock_response.ok = True; mock_response.json.return_value = {"webhooks": []}
        mock_request.return_value = mock_response
        self.sdk.list_webhooks('agent1', jwt_token='jwt')
        call = mock_request.call_args
        self.assertIn('/agents/agent1/webhooks', call[0][1])

        mock_response.json.return_value = {"deliveries": [], "count": 0}
        self.sdk.list_webhook_deliveries(status='failed', limit=5, agent_id='agent1', jwt_token='jwt')
        call = mock_request.call_args
        self.assertIn('/agents/agent1/webhooks/deliveries', call[0][1])

        mock_response.json.return_value = {"replayed": True}
        self.sdk.replay_webhook_delivery('dlv_1', agent_id='agent1', jwt_token='jwt')
        call = mock_request.call_args
        self.assertIn('/agents/agent1/webhooks/deliveries/dlv_1/replay', call[0][1])

    @patch('requests.Session.request')
    def test_get_ap2_signing_digest(self, mock_request):
      mock_response = Mock(); mock_response.ok = True; mock_response.json.return_value = {"digest": "ap2:stablecoin:intent:cart:100:usd:0xabc"}
      mock_request.return_value = mock_response
      res = self.sdk.get_ap2_signing_digest(intent_mandate_id='intent', cart_mandate_id='cart', destination_wallet='0xabc')
      self.assertIn('digest', res)
      call = mock_request.call_args
      self.assertIn('/ap2/signing-digest', call[0][1])

    @patch('requests.Session.request')
    def test_verify_receipt(self, mock_request):
        """Test receipt verification"""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {
            "valid": True,
            "receipt": {
                "receipt_id": "rec_123",
                "agent_id": "agent_123",
                "amount": 1000
            }
        }
        mock_request.return_value = mock_response

        result = self.sdk.verify_receipt("rec_123")

        self.assertTrue(result["valid"])
        self.assertEqual(result["receipt"]["receipt_id"], "rec_123")

        mock_request.assert_called_once_with(
            "GET", "https://api.example.com/receipts/verify/rec_123"
        )


if __name__ == '__main__':
    unittest.main()
