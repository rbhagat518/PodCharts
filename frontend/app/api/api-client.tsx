"use client";

import { useState } from "react";
import Link from "next/link";

export default function ApiClient() {
  const [selectedEndpoint, setSelectedEndpoint] = useState<string | null>(null);

  const endpoints = [
    {
      method: "GET",
      path: "/leaderboard",
      description: "Get leaderboard of podcasts",
      params: ["category", "country", "interval", "sort_by", "search", "limit"],
      example: "/leaderboard?category=technology&sort_by=momentum&limit=50",
    },
    {
      method: "GET",
      path: "/trending",
      description: "Get trending podcasts",
      params: ["category", "limit"],
      example: "/trending?category=technology&limit=20",
    },
    {
      method: "GET",
      path: "/podcast/{id}",
      description: "Get podcast details and history",
      params: [],
      example: "/podcast/4d3fe717742d4963a85562e9f7d74f8e",
    },
    {
      method: "GET",
      path: "/compare",
      description: "Compare two podcasts",
      params: ["id1", "id2"],
      example: "/compare?id1=abc123&id2=def456",
    },
  ];

  const baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

  return (
    <div className="space-y-8">
      <div className="space-y-4">
        <h1 className="text-3xl font-bold">API Documentation</h1>
        <p className="text-neutral-400 max-w-2xl">
          Access PodCharts data programmatically with our REST API. All endpoints return JSON and
          support CORS.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-4">
          <div className="border border-neutral-800 rounded p-4">
            <h2 className="font-semibold mb-2">Base URL</h2>
            <code className="text-sm text-neutral-400">{baseUrl}</code>
          </div>

          <div className="space-y-4">
            <h2 className="text-xl font-semibold">Endpoints</h2>
            {endpoints.map((endpoint) => (
              <div
                key={endpoint.path}
                className="border border-neutral-800 rounded p-4 space-y-3"
              >
                <div className="flex items-center gap-3">
                  <span className="px-2 py-1 bg-green-900/30 text-green-400 rounded text-xs font-mono">
                    {endpoint.method}
                  </span>
                  <code className="text-sm font-mono">{endpoint.path}</code>
                </div>
                <p className="text-sm text-neutral-400">{endpoint.description}</p>
                {endpoint.params.length > 0 && (
                  <div>
                    <div className="text-xs text-neutral-500 mb-1">Query Parameters:</div>
                    <div className="flex flex-wrap gap-2">
                      {endpoint.params.map((param) => (
                        <code key={param} className="text-xs bg-neutral-900 px-2 py-1 rounded">
                          {param}
                        </code>
                      ))}
                    </div>
                  </div>
                )}
                <div>
                  <div className="text-xs text-neutral-500 mb-1">Example:</div>
                  <code className="text-xs bg-neutral-900 px-2 py-1 rounded block break-all">
                    {baseUrl}{endpoint.example}
                  </code>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="space-y-4">
          <div className="border border-neutral-800 rounded p-4">
            <h3 className="font-semibold mb-2">Authentication</h3>
            <p className="text-sm text-neutral-400 mb-3">
              Public endpoints don't require authentication. For API access, use your API key:
            </p>
            <code className="text-xs bg-neutral-900 px-2 py-1 rounded block">
              X-API-Key: pk_your_api_key_here
            </code>
            <Link
              href="/dashboard"
              className="text-sm text-blue-400 hover:underline mt-2 inline-block"
            >
              Get your API key →
            </Link>
          </div>

          <div className="border border-neutral-800 rounded p-4">
            <h3 className="font-semibold mb-2">Rate Limits</h3>
            <ul className="text-sm text-neutral-400 space-y-1">
              <li>Free: 1,000/month</li>
              <li>Pro: 10,000/month</li>
              <li>Enterprise: 100,000+/month</li>
            </ul>
          </div>

          <div className="border border-neutral-800 rounded p-4">
            <h3 className="font-semibold mb-2">Response Format</h3>
            <p className="text-sm text-neutral-400 mb-2">All responses are JSON:</p>
            <pre className="text-xs bg-neutral-900 p-2 rounded overflow-x-auto">
              {`{
  "items": [...],
  "category": "technology",
  "captured_on": "2025-11-07"
}`}
            </pre>
          </div>
        </div>
      </div>
    </div>
  );
}

