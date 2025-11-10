# Changelog (Python SDK)

All notable changes to the Paegents Python SDK.

## Unreleased — 2025-10-26

Added
- Policies & Approvals support
  - get_agent_policies, update_agent_policies
  - list_approvals, approve_approval, reject_approval
- AP2 approval handling
  - ap2_pay returns dict with `{approval_required, request_id, policy}` when approval needed
  - Optional `idempotency_key` param
- Usage Agreements
  - UsageAgreementRequest.cart_items merged into `metadata.cart_items`
  - reject_usage_agreement_with_suggestions(reason, suggested_cart_items, suggested_total_cents)
- Owner Spending Limits (JWT)
  - get_spending_limits_owner, update_spending_limits_owner
- Webhooks Ops
  - list_webhooks, create_webhook, rotate_webhook_secret, pause_webhook, resume_webhook, send_test_webhook
  - list_webhook_deliveries, replay_webhook_delivery

Changed
- Error mapping: raise PolicyDeniedError for `policy_denied:*`, ApiError for other HTTP errors
