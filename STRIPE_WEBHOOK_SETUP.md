# Stripe Webhook Setup Guide

## 📋 Events to Configure in Stripe Dashboard

When setting up your Stripe webhook endpoint, you should listen for these events:

### ✅ Essential Events (Required)

1. **`checkout.session.completed`**
   - **When**: User completes checkout and subscription is created
   - **Action**: Activate subscription, upgrade user tier
   - **Status**: ✅ Implemented

2. **`customer.subscription.updated`**
   - **When**: Subscription is updated (plan change, renewal, etc.)
   - **Action**: Update subscription status and tier
   - **Status**: ✅ Implemented

3. **`customer.subscription.deleted`**
   - **When**: Subscription is cancelled or deleted
   - **Action**: Downgrade user to free tier
   - **Status**: ✅ Implemented

4. **`invoice.payment_succeeded`**
   - **When**: Subscription payment succeeds (renewal)
   - **Action**: Ensure subscription is active
   - **Status**: ✅ Implemented

5. **`invoice.payment_failed`**
   - **When**: Subscription payment fails
   - **Action**: Mark subscription as past_due
   - **Status**: ✅ Implemented

### 📊 Recommended Events (Optional but Useful)

6. **`customer.subscription.created`**
   - **When**: New subscription is created
   - **Action**: Can be used as backup to checkout.session.completed
   - **Status**: ⚠️ Not fully implemented (handled by checkout.session.completed)

7. **`customer.updated`**
   - **When**: Customer information is updated
   - **Action**: Sync customer data if needed
   - **Status**: ⚠️ Placeholder only

8. **`invoice.created`**
   - **When**: New invoice is created
   - **Action**: Log invoice creation for analytics
   - **Status**: ❌ Not implemented

9. **`invoice.finalized`**
   - **When**: Invoice is finalized
   - **Action**: Send invoice to customer
   - **Status**: ❌ Not implemented

10. **`customer.subscription.trial_will_end`**
    - **When**: Trial period is ending soon
    - **Action**: Send reminder email
    - **Status**: ❌ Not implemented

---

## 🔧 How to Configure in Stripe Dashboard

> **⚠️ Important**: For **local testing**, you should **NOT** create an endpoint in the Stripe Dashboard. Instead, use the **Stripe CLI** (see `LOCAL_STRIPE_TESTING.md`). Only create a dashboard endpoint when deploying to **production**.

### Step 1: Create Webhook Endpoint (Production Only)

1. Go to [Stripe Dashboard](https://dashboard.stripe.com/webhooks)
2. Click **"Add endpoint"**
3. Enter your **production** webhook URL:
   ```
   https://your-domain.com/api/subscriptions/webhook
   ```
   **Do NOT use** `http://localhost:8000` - that's for local testing only!

### Step 2: Select Events

Select these events:

**Essential Events:**
- ✅ `checkout.session.completed`
- ✅ `customer.subscription.updated`
- ✅ `customer.subscription.deleted`
- ✅ `invoice.payment_succeeded`
- ✅ `invoice.payment_failed`

**Optional Events:**
- ⚠️ `customer.subscription.created`
- ⚠️ `customer.updated`

### Step 3: Get Webhook Secret

1. After creating the endpoint, click on it
2. Click **"Reveal"** next to "Signing secret"
3. Copy the webhook secret (starts with `whsec_`)
4. Add it to your `.env` file:
   ```
   STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here
   ```

---

## 🧪 Testing Webhooks Locally

### Using Stripe CLI

1. **Install Stripe CLI**:
   ```bash
   brew install stripe/stripe-cli/stripe
   ```

2. **Login to Stripe**:
   ```bash
   stripe login
   ```

3. **Forward webhooks to local server**:
   ```bash
   stripe listen --forward-to localhost:8000/api/subscriptions/webhook
   ```

4. **Get webhook secret for local testing**:
   ```bash
   stripe listen --print-secret
   ```
   Use this secret in your `.env` for local development.

5. **Trigger test events**:
   ```bash
   stripe trigger checkout.session.completed
   stripe trigger customer.subscription.updated
   stripe trigger customer.subscription.deleted
   stripe trigger invoice.payment_succeeded
   stripe trigger invoice.payment_failed
   ```

---

## 📝 Event Handling Details

### `checkout.session.completed`
- **Triggered**: When user completes checkout
- **Data**: Session object with `client_reference_id` (user_id) and `subscription` ID
- **Action**: Activate subscription, upgrade user tier, set quota

### `customer.subscription.updated`
- **Triggered**: When subscription is updated (plan change, renewal, etc.)
- **Data**: Subscription object with status and metadata
- **Action**: Update subscription status, tier, and quota

### `customer.subscription.deleted`
- **Triggered**: When subscription is cancelled or deleted
- **Data**: Subscription object
- **Action**: Downgrade user to free tier, reset quota to 1000

### `invoice.payment_succeeded`
- **Triggered**: When subscription payment succeeds (renewal)
- **Data**: Invoice object with subscription ID
- **Action**: Ensure subscription is marked as active

### `invoice.payment_failed`
- **Triggered**: When subscription payment fails
- **Data**: Invoice object with subscription ID
- **Action**: Mark subscription as past_due

---

## 🔐 Security

### Webhook Signature Verification

The webhook handler automatically verifies the webhook signature using `STRIPE_WEBHOOK_SECRET`. This ensures the webhook is actually from Stripe.

**Important**: Never skip signature verification in production!

---

## 🐛 Troubleshooting

### Webhook Not Receiving Events

1. **Check webhook URL**: Ensure it's accessible from the internet
2. **Check webhook secret**: Verify `STRIPE_WEBHOOK_SECRET` is correct
3. **Check logs**: Look for errors in your application logs
4. **Test with Stripe CLI**: Use `stripe listen` to test locally

### Events Not Being Handled

1. **Check event type**: Ensure the event type is in the handler
2. **Check database**: Verify user records exist
3. **Check logs**: Look for exceptions in the webhook handler

### Subscription Not Updating

1. **Check user_id**: Ensure `client_reference_id` is set in checkout session
2. **Check subscription_id**: Verify subscription ID is stored correctly
3. **Check database**: Verify user record exists and can be updated

---

## 📊 Monitoring

### Stripe Dashboard

- View webhook delivery status in Stripe Dashboard
- See failed deliveries and retry them
- View webhook logs and responses

### Application Logs

- Log all webhook events for debugging
- Track subscription changes
- Monitor payment failures

---

## ✅ Checklist

- [ ] Webhook endpoint created in Stripe Dashboard
- [ ] All essential events selected
- [ ] Webhook secret added to `.env`
- [ ] Webhook URL is accessible
- [ ] Tested with Stripe CLI locally
- [ ] Tested checkout flow end-to-end
- [ ] Tested subscription cancellation
- [ ] Tested payment failure handling
- [ ] Monitoring set up for webhook failures

---

## 🚀 Production Checklist

- [ ] Webhook endpoint uses HTTPS
- [ ] Webhook secret is secure (not in git)
- [ ] Error handling is robust
- [ ] Logging is comprehensive
- [ ] Monitoring is set up
- [ ] Retry logic is implemented (Stripe handles this)
- [ ] Idempotency is handled (Stripe handles this)

---

## 📚 Resources

- [Stripe Webhooks Documentation](https://stripe.com/docs/webhooks)
- [Stripe CLI Documentation](https://stripe.com/docs/stripe-cli)
- [Stripe Webhook Events Reference](https://stripe.com/docs/api/events/types)

