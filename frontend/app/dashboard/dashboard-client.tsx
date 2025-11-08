"use client";

import { useState, useEffect } from "react";
import Link from "next/link";

type UserProfile = {
  id: string;
  email: string;
  subscription_tier: string;
  subscription_status: string;
  subscription_expires_at: string | null;
  api_quota: {
    monthly: number;
    used: number;
    remaining: number;
  };
};

type WatchlistItem = {
  id: string;
  title: string;
  publisher: string | null;
  category: string | null;
  rank: number | null;
  delta_7d: number | null;
  delta_30d: number | null;
  momentum_score: number | null;
};

export default function DashboardClient() {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [watchlist, setWatchlist] = useState<WatchlistItem[]>([]);
  const [apiKey, setApiKey] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // TODO: Implement Supabase Auth
    // For now, this is a placeholder
    setLoading(false);
  }, []);

  const handleGetApiKey = async () => {
    // TODO: Implement API key generation
    alert("API key generation requires authentication. Coming soon!");
  };

  if (loading) {
    return <div className="py-12 text-center text-neutral-400">Loading...</div>;
  }

  if (!user) {
    return (
      <div className="space-y-6">
        <h1 className="text-2xl font-semibold">Dashboard</h1>
        <div className="border border-neutral-800 rounded p-6 text-center">
          <p className="text-neutral-400 mb-4">Sign in to access your dashboard</p>
          <Link
            href="/login"
            className="px-4 py-2 bg-white text-black rounded hover:bg-neutral-200 transition"
          >
            Sign In
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Dashboard</h1>
        <Link
          href="/pricing"
          className="px-4 py-2 bg-white text-black rounded hover:bg-neutral-200 transition text-sm"
        >
          {user.subscription_tier === "free" ? "Upgrade to Pro" : "Manage Subscription"}
        </Link>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="border border-neutral-800 rounded p-4">
          <div className="text-xs text-neutral-400 mb-1">Subscription</div>
          <div className="text-lg font-semibold capitalize">{user.subscription_tier}</div>
          <div className="text-sm text-neutral-400 mt-1">
            {user.subscription_status === "active" ? "Active" : "Inactive"}
          </div>
        </div>
        <div className="border border-neutral-800 rounded p-4">
          <div className="text-xs text-neutral-400 mb-1">API Quota</div>
          <div className="text-lg font-semibold">
            {user.api_quota.used} / {user.api_quota.monthly}
          </div>
          <div className="text-sm text-neutral-400 mt-1">
            {user.api_quota.remaining} remaining
          </div>
        </div>
        <div className="border border-neutral-800 rounded p-4">
          <div className="text-xs text-neutral-400 mb-1">Watchlist</div>
          <div className="text-lg font-semibold">{watchlist.length} podcasts</div>
          <div className="text-sm text-neutral-400 mt-1">Following</div>
        </div>
      </div>

      <div className="border border-neutral-800 rounded p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold">API Key</h2>
          <button
            onClick={handleGetApiKey}
            className="px-3 py-1.5 bg-neutral-800 border border-neutral-700 rounded text-sm hover:bg-neutral-700"
          >
            {apiKey ? "Regenerate" : "Generate API Key"}
          </button>
        </div>
        {apiKey ? (
          <div className="space-y-2">
            <code className="block p-3 bg-neutral-900 rounded text-sm font-mono break-all">
              {apiKey}
            </code>
            <p className="text-xs text-neutral-400">
              Use this API key in the X-API-Key header for authenticated requests
            </p>
          </div>
        ) : (
          <p className="text-neutral-400 text-sm">Generate an API key to access the PodCharts API</p>
        )}
      </div>

      {watchlist.length > 0 && (
        <div className="border border-neutral-800 rounded p-6">
          <h2 className="text-lg font-semibold mb-4">My Watchlist</h2>
          <div className="space-y-2">
            {watchlist.map((item) => (
              <Link
                key={item.id}
                href={`/podcast/${item.id}`}
                className="block p-3 border border-neutral-800 rounded hover:bg-neutral-900/50 transition"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-medium">{item.title}</div>
                    <div className="text-sm text-neutral-400">{item.publisher}</div>
                  </div>
                  <div className="text-right">
                    <div className="font-mono text-sm">Rank #{item.rank ?? "—"}</div>
                    {item.momentum_score !== null && item.momentum_score > 0 && (
                      <span className="text-xs text-green-400">🔥 Trending</span>
                    )}
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

