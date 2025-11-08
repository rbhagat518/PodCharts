"use client";

import { useState } from "react";
import Link from "next/link";

export default function PricingClient() {
  const [loading, setLoading] = useState(false);

  const handleSubscribe = async (tier: string) => {
    setLoading(true);
    // TODO: Implement Stripe checkout
    alert(`Stripe checkout for ${tier} tier - Coming soon!`);
    setLoading(false);
  };

  const plans = [
    {
      name: "Free",
      price: "$0",
      period: "forever",
      features: [
        "View leaderboards",
        "Search podcasts",
        "Basic charts",
        "1,000 API calls/month",
        "Community support",
      ],
      cta: "Current Plan",
      disabled: false,
    },
    {
      name: "Pro",
      price: "$29",
      period: "per month",
      features: [
        "Everything in Free",
        "Advanced analytics",
        "Export to CSV/PDF",
        "10,000 API calls/month",
        "Email alerts",
        "Watchlist (unlimited)",
        "Priority support",
      ],
      cta: "Upgrade to Pro",
      disabled: false,
      popular: true,
    },
    {
      name: "Enterprise",
      price: "Custom",
      period: "",
      features: [
        "Everything in Pro",
        "100,000+ API calls/month",
        "Custom integrations",
        "Dedicated support",
        "SLA guarantee",
        "Custom reports",
        "White-label options",
      ],
      cta: "Contact Sales",
      disabled: false,
    },
  ];

  return (
    <div className="space-y-8">
      <div className="text-center space-y-4">
        <h1 className="text-3xl font-bold">Pricing</h1>
        <p className="text-neutral-400 max-w-2xl mx-auto">
          Choose the plan that fits your needs. All plans include access to our comprehensive podcast
          analytics platform.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-5xl mx-auto">
        {plans.map((plan) => (
          <div
            key={plan.name}
            className={`border rounded-lg p-6 space-y-4 ${
              plan.popular
                ? "border-blue-500 bg-blue-950/20"
                : "border-neutral-800 bg-neutral-900/30"
            }`}
          >
            {plan.popular && (
              <div className="text-xs font-semibold text-blue-400 text-center mb-2">MOST POPULAR</div>
            )}
            <div>
              <h3 className="text-xl font-semibold">{plan.name}</h3>
              <div className="mt-2">
                <span className="text-3xl font-bold">{plan.price}</span>
                {plan.period && <span className="text-neutral-400 ml-2">{plan.period}</span>}
              </div>
            </div>
            <ul className="space-y-2">
              {plan.features.map((feature, idx) => (
                <li key={idx} className="flex items-start gap-2 text-sm">
                  <span className="text-green-400 mt-0.5">✓</span>
                  <span>{feature}</span>
                </li>
              ))}
            </ul>
            <button
              onClick={() => handleSubscribe(plan.name.toLowerCase())}
              disabled={plan.disabled || loading}
              className={`w-full py-2 rounded font-medium transition ${
                plan.popular
                  ? "bg-white text-black hover:bg-neutral-200"
                  : "bg-neutral-800 border border-neutral-700 hover:bg-neutral-700"
              } disabled:opacity-50`}
            >
              {plan.cta}
            </button>
          </div>
        ))}
      </div>

      <div className="border-t border-neutral-800 pt-8 mt-12">
        <h2 className="text-xl font-semibold mb-4 text-center">Frequently Asked Questions</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-3xl mx-auto">
          <div>
            <h3 className="font-semibold mb-2">What's included in the API?</h3>
            <p className="text-sm text-neutral-400">
              Access to all leaderboard, trending, podcast detail, and comparison endpoints. Rate
              limits vary by plan.
            </p>
          </div>
          <div>
            <h3 className="font-semibold mb-2">Can I change plans later?</h3>
            <p className="text-sm text-neutral-400">
              Yes! You can upgrade or downgrade at any time. Changes take effect immediately.
            </p>
          </div>
          <div>
            <h3 className="font-semibold mb-2">What payment methods do you accept?</h3>
            <p className="text-sm text-neutral-400">
              We accept all major credit cards through Stripe. Enterprise plans can be invoiced.
            </p>
          </div>
          <div>
            <h3 className="font-semibold mb-2">Is there a free trial?</h3>
            <p className="text-sm text-neutral-400">
              The Free plan is available forever. Pro plans include a 14-day free trial.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

