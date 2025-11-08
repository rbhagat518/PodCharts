# Local Stripe Testing Guide

## 🧪 Testing Stripe Webhooks Locally

For **local development**, you should **NOT** set up a webhook endpoint in the Stripe Dashboard. Instead, use the **Stripe CLI** to forward webhooks to your local server.

---

## ✅ Local Testing Setup (No Dashboard Endpoint Needed)

### Step 1: Install Stripe CLI

```bash
# macOS
brew install stripe/stripe-cli/stripe

# Or download from: https://stripe.com/docs/stripe-cli
```

### Step 2: Login to Stripe

```bash
stripe login
```

This will open your browser to authenticate with Stripe.

### Step 3: Start Your Backend Server

```bash
cd backend
# Make sure your backend is running on port 8000
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 4: Forward Webhooks to Local Server

In a **separate terminal**, run:

```bash
stripe listen --forward-to localhost:8000/api/subscriptions/webhook
```

This will:
- Forward all Stripe webhook events to your local server
- Display the webhook secret you need to use
- Show you all webhook events in real-time

### Step 5: Get Webhook Secret for Local Testing

The `stripe listen` command will output something like:

```
> Ready! Your webhook signing secret is whsec_xxxxxxxxxxxxx (^C to quit)
```

**Copy this secret** and add it to your `.env` file:

```bash
STRIPE_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxx
```

**Important**: This secret is different from production! Use this one only for local testing.

### Step 6: Restart Your Backend

After adding the webhook secret, restart your backend server so it picks up the new environment variable.

---

## 🧪 Testing Webhook Events Locally

### Trigger Test Events

In another terminal, you can trigger test events:

```bash
# Test checkout completion
stripe trigger checkout.session.completed

# Test subscription update
stripe trigger customer.subscription.updated

# Test subscription deletion
stripe trigger customer.subscription.deleted

# Test payment success
stripe trigger invoice.payment_succeeded

# Test payment failure
stripe trigger invoice.payment_failed
```

You'll see the events in:
1. The `stripe listen` terminal (showing the event being sent)
2. Your backend logs (showing the event being received and processed)

---

## 🚀 Production Setup (Dashboard Endpoint Required)

**Only when deploying to production**, you'll need to:

1. **Set up webhook endpoint in Stripe Dashboard**:
   - Go to [Stripe Dashboard → Webhooks](https://dashboard.stripe.com/webhooks)
   - Click "Add endpoint"
   - Enter your production URL: `https://your-domain.com/api/subscriptions/webhook`
   - Select the 5 essential events (see `STRIPE_WEBHOOK_SETUP.md`)
   - Copy the webhook secret (starts with `whsec_`)

2. **Add production webhook secret to your environment**:
   ```bash
   STRIPE_WEBHOOK_SECRET=whsec_your_production_secret
   ```

3. **Update your `.env` file** with the production secret

---

## 📋 Quick Reference

### Local Development
- ✅ Use `stripe listen --forward-to localhost:8000/api/subscriptions/webhook`
- ✅ Use the webhook secret from `stripe listen` output
- ❌ Don't create an endpoint in Stripe Dashboard

### Production
- ✅ Create webhook endpoint in Stripe Dashboard
- ✅ Use production webhook secret
- ❌ Don't use `stripe listen` (that's for local only)

---

## 🔍 Verifying It Works

### Check Webhook Reception

1. **Watch the `stripe listen` terminal** - You should see events being forwarded
2. **Watch your backend logs** - You should see the webhook handler processing events
3. **Check your database** - After triggering `checkout.session.completed`, check if user subscription was updated

### Test Flow

1. Start backend: `uvicorn app.main:app --reload`
2. Start Stripe CLI: `stripe listen --forward-to localhost:8000/api/subscriptions/webhook`
3. Trigger test event: `stripe trigger checkout.session.completed`
4. Check backend logs for webhook processing
5. Verify database was updated

---

## 🐛 Troubleshooting

### Webhook Not Received

- **Check Stripe CLI is running**: Make sure `stripe listen` is active
- **Check backend is running**: Make sure your backend is on port 8000
- **Check webhook secret**: Ensure `STRIPE_WEBHOOK_SECRET` matches the one from `stripe listen`
- **Check URL**: Make sure the webhook URL in `stripe listen` matches your backend route

### Webhook Secret Mismatch

- **Local**: Use the secret from `stripe listen` output
- **Production**: Use the secret from Stripe Dashboard
- **Never mix them**: Local secret won't work in production, and vice versa

### Events Not Processing

- **Check logs**: Look for errors in your backend logs
- **Check database**: Verify user records exist
- **Check event type**: Ensure the event type is handled in your webhook handler

---

## 📝 Summary

**For Local Testing:**
- ✅ Use Stripe CLI: `stripe listen --forward-to localhost:8000/api/subscriptions/webhook`
- ✅ Use webhook secret from CLI output
- ❌ Don't create endpoint in Stripe Dashboard

**For Production:**
- ✅ Create endpoint in Stripe Dashboard
- ✅ Use production webhook secret
- ❌ Don't use Stripe CLI

---

## 🎯 Next Steps

1. Install Stripe CLI: `brew install stripe/stripe-cli/stripe`
2. Login: `stripe login`
3. Start forwarding: `stripe listen --forward-to localhost:8000/api/subscriptions/webhook`
4. Copy webhook secret to `.env`
5. Test with: `stripe trigger checkout.session.completed`

Happy testing! 🚀

