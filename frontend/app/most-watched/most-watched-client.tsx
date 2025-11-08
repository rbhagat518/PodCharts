"use client";

import { useState, useEffect } from "react";
import Link from "next/link";

type MostWatchedItem = {
  id: string;
  title: string;
  publisher: string | null;
  category: string | null;
  country: string | null;
  total_listen_time_seconds: number;
  total_listen_time_hours: number;
  total_unique_listeners: number;
  avg_completion_rate: number | null;
  total_new_episodes: number;
  total_active_episodes: number;
  avg_engagement_score: number | null;
  days_tracked: number;
};

type MostWatchedData = {
  start_date: string;
  end_date: string;
  sort_by: string;
  category: string | null;
  country: string | null;
  items: MostWatchedItem[];
};

export default function MostWatchedClient() {
  const [data, setData] = useState<MostWatchedData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Default to first week of November 2024
  const today = new Date();
  const currentYear = today.getFullYear();
  const currentMonth = today.getMonth() + 1;
  
  const [startDate, setStartDate] = useState(
    currentMonth === 11 ? `${currentYear}-11-01` : `${currentYear - 1}-11-01`
  );
  const [endDate, setEndDate] = useState(
    currentMonth === 11 ? `${currentYear}-11-07` : `${currentYear - 1}-11-07`
  );
  const [sortBy, setSortBy] = useState("engagement_score");
  const [category, setCategory] = useState<string>("");
  const [country, setCountry] = useState<string>("");

  const fetchMostWatched = async () => {
    setLoading(true);
    setError(null);
    try {
      const base = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";
      const params = new URLSearchParams({
        start_date: startDate,
        end_date: endDate,
        sort_by: sortBy,
        limit: "50",
      });
      
      if (category) params.append("category", category);
      if (country) params.append("country", country);
      
      const url = `${base}/most-watched?${params.toString()}`;
      
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 10000);
      
      const res = await fetch(url, { signal: controller.signal });
      clearTimeout(timeoutId);
      
      if (!res.ok) {
        const errorData = await res.json().catch(() => ({ detail: res.statusText }));
        throw new Error(errorData.detail || `Failed to fetch most watched: ${res.statusText}`);
      }
      
      const result = await res.json();
      setData(result);
    } catch (err) {
      if (err instanceof Error) {
        if (err.name === "AbortError") {
          setError("Request timed out. Please check your database connection.");
        } else {
          setError(err.message);
        }
      } else {
        setError("Failed to load most watched podcasts");
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMostWatched();
  }, []);

  const formatHours = (hours: number) => {
    if (hours < 1) return `${(hours * 60).toFixed(0)} min`;
    if (hours < 24) return `${hours.toFixed(1)} hrs`;
    return `${(hours / 24).toFixed(1)} days`;
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Most Watched Podcasts</h1>
          <p className="text-neutral-400 mt-2">
            Track podcast engagement based on episode activity and listen time metrics
          </p>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-neutral-900 rounded-lg p-4 space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">Start Date</label>
            <input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              className="w-full px-3 py-2 bg-neutral-800 border border-neutral-700 rounded text-sm"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">End Date</label>
            <input
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              className="w-full px-3 py-2 bg-neutral-800 border border-neutral-700 rounded text-sm"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Sort By</label>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="w-full px-3 py-2 bg-neutral-800 border border-neutral-700 rounded text-sm"
            >
              <option value="engagement_score">Engagement Score</option>
              <option value="listen_time">Listen Time</option>
              <option value="listeners">Listeners</option>
              <option value="new_episodes">New Episodes</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Category</label>
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="w-full px-3 py-2 bg-neutral-800 border border-neutral-700 rounded text-sm"
            >
              <option value="">All Categories</option>
              <option value="technology">Technology</option>
              <option value="news">News</option>
              <option value="comedy">Comedy</option>
              <option value="business">Business</option>
              <option value="health">Health</option>
              <option value="education">Education</option>
            </select>
          </div>
        </div>
        <button
          onClick={fetchMostWatched}
          disabled={loading}
          className="px-4 py-2 bg-white text-black font-medium rounded hover:bg-neutral-200 transition disabled:opacity-50"
        >
          {loading ? "Loading..." : "Apply Filters"}
        </button>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-900/20 border border-red-700 rounded p-4 text-red-300">
          {error}
        </div>
      )}

      {/* Results */}
      {data && (
        <div className="space-y-4">
          <div className="text-sm text-neutral-400">
            Showing {data.items.length} podcasts from {data.start_date} to {data.end_date}
            {data.category && ` in ${data.category}`}
            {data.country && ` from ${data.country}`}
          </div>

          {data.items.length === 0 ? (
            <div className="text-center py-12 text-neutral-400">
              No data available for this time period. Try running the episode ingestion script.
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full border-collapse">
                <thead>
                  <tr className="border-b border-neutral-800">
                    <th className="text-left py-3 pr-4 text-sm font-medium text-neutral-400">Rank</th>
                    <th className="text-left py-3 pr-4 text-sm font-medium text-neutral-400">Podcast</th>
                    <th className="text-left py-3 pr-4 text-sm font-medium text-neutral-400">Publisher</th>
                    <th className="text-right py-3 pr-4 text-sm font-medium text-neutral-400">Engagement</th>
                    <th className="text-right py-3 pr-4 text-sm font-medium text-neutral-400">Listen Time</th>
                    <th className="text-right py-3 pr-4 text-sm font-medium text-neutral-400">Listeners</th>
                    <th className="text-right py-3 pr-4 text-sm font-medium text-neutral-400">New Episodes</th>
                    <th className="text-right py-3 pr-4 text-sm font-medium text-neutral-400">Active Episodes</th>
                  </tr>
                </thead>
                <tbody>
                  {data.items.map((item, idx) => (
                    <tr
                      key={item.id}
                      className="border-b border-neutral-900 hover:bg-neutral-900/50"
                    >
                      <td className="py-3 pr-4 font-mono text-neutral-400">{idx + 1}</td>
                      <td className="py-3 pr-4">
                        <Link
                          href={`/podcast/${item.id}`}
                          className="hover:underline font-medium"
                        >
                          {item.title}
                        </Link>
                        {item.category && (
                          <span className="ml-2 px-2 py-0.5 bg-neutral-800 rounded text-xs text-neutral-300">
                            {item.category}
                          </span>
                        )}
                      </td>
                      <td className="py-3 pr-4 text-neutral-400">{item.publisher || "—"}</td>
                      <td className="py-3 pr-4 text-right font-mono text-sm">
                        {item.avg_engagement_score !== null
                          ? item.avg_engagement_score.toFixed(2)
                          : "—"}
                      </td>
                      <td className="py-3 pr-4 text-right font-mono text-sm">
                        {item.total_listen_time_hours > 0
                          ? formatHours(item.total_listen_time_hours)
                          : "—"}
                      </td>
                      <td className="py-3 pr-4 text-right font-mono text-sm">
                        {item.total_unique_listeners > 0
                          ? item.total_unique_listeners.toLocaleString()
                          : "—"}
                      </td>
                      <td className="py-3 pr-4 text-right font-mono text-sm">
                        {item.total_new_episodes}
                      </td>
                      <td className="py-3 pr-4 text-right font-mono text-sm">
                        {item.total_active_episodes}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

