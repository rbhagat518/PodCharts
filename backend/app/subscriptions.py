"""Subscription and payment handling."""
from __future__ import annotations

import os
from typing import Any
from uuid import UUID

import stripe
from dotenv import load_dotenv

load_dotenv()

STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET")

if STRIPE_SECRET_KEY:
    stripe.api_key = STRIPE_SECRET_KEY


def create_checkout_session(user_id: UUID, tier: str = "pro") -> dict[str, Any]:
    """Create Stripe checkout session for subscription."""
    if not STRIPE_SECRET_KEY:
        raise RuntimeError("STRIPE_SECRET_KEY not configured")
    
    price_id = os.environ.get(f"STRIPE_PRICE_ID_{tier.upper()}")
    if not price_id:
        raise RuntimeError(f"STRIPE_PRICE_ID_{tier.upper()} not configured")
    
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[
            {
                "price": price_id,
                "quantity": 1,
            }
        ],
        mode="subscription",
        success_url=f"{os.environ.get('FRONTEND_URL', 'http://localhost:3000')}/dashboard?success=true",
        cancel_url=f"{os.environ.get('FRONTEND_URL', 'http://localhost:3000')}/pricing?canceled=true",
        client_reference_id=str(user_id),
        metadata={"tier": tier},
    )
    
    return {"checkout_url": session.url, "session_id": session.id}


def handle_webhook(payload: bytes, signature: str) -> dict[str, Any]:
    """Handle Stripe webhook event."""
    if not STRIPE_WEBHOOK_SECRET:
        raise RuntimeError("STRIPE_WEBHOOK_SECRET not configured")
    
    try:
        event = stripe.Webhook.construct_event(payload, signature, STRIPE_WEBHOOK_SECRET)
    except ValueError:
        raise ValueError("Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise ValueError("Invalid signature")
    
    return event


def update_user_subscription(user_id: UUID, subscription_id: str, tier: str, status: str) -> None:
    """Update user subscription in database."""
    from app.db import get_connection
    from datetime import datetime, timedelta
    
    # Get subscription details from Stripe
    expires_at = None
    if STRIPE_SECRET_KEY and subscription_id:
        try:
            subscription = stripe.Subscription.retrieve(subscription_id)
            expires_at = datetime.fromtimestamp(subscription.current_period_end)
        except Exception:
            expires_at = datetime.now() + timedelta(days=30)
    else:
        expires_at = datetime.now() + timedelta(days=30)
    
    with get_connection() as conn:
        with conn.cursor() as cursor:
            # Update quota based on tier
            quota = {"free": 1000, "pro": 10000, "enterprise": 100000}.get(tier, 1000)
            
            # First, ensure user exists
            cursor.execute("SELECT id FROM users WHERE id = %s", (user_id,))
            if not cursor.fetchone():
                # Create user if doesn't exist (shouldn't happen, but safety check)
                cursor.execute(
                    """
                    INSERT INTO users (id, subscription_tier, subscription_status, subscription_id, subscription_expires_at, api_quota_monthly)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (user_id, tier, status, subscription_id, expires_at, quota),
                )
            else:
                # Update existing user
                cursor.execute(
                    """
                    UPDATE users
                    SET subscription_tier = %s,
                        subscription_status = %s,
                        subscription_id = %s,
                        subscription_expires_at = %s,
                        api_quota_monthly = %s,
                        updated_at = now()
                    WHERE id = %s
                    """,
                    (tier, status, subscription_id, expires_at, quota, user_id),
                )
            conn.commit()

