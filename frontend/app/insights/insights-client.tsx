"use client";

import { useState, useEffect } from "react";
import Link from "next/link";

type Insight = {
  id: string;
  title: string;
  publisher: string | null;
  category: string | null;
  country: string | null;
  avg_rank: number;
  best_rank: number;
  worst_rank: number;
  avg_delta_7d: number | null;
  avg_delta_30d: number | null;
  avg_momentum: number | null;
  peak_momentum: number | null;
  days_tracked: number;
};

type BiggestGainer = {
  id: string;
  title: string;
  publisher: string | null;
  max_delta_30d?: number | null;
  max_delta_7d?: number | null;
};

type MonthlyInsightsData = {
  year: number;
  month: number;
  month_name: string;
  start_date: string;
  end_date: string;
  top_podcasts: Insight[];
  biggest_gainers: BiggestGainer[];
};

type WeeklyInsightsData = {
  year: number;
  week: number;
  start_date: string;
  end_date: string;
  top_podcasts: Insight[];
  biggest_gainers: BiggestGainer[];
};

type InsightsData = MonthlyInsightsData | WeeklyInsightsData;

export default function InsightsClient() {
  const [viewType, setViewType] = useState<"monthly" | "weekly">("monthly");
  const [year, setYear] = useState(new Date().getFullYear());
  const [month, setMonth] = useState(new Date().getMonth() + 1);
  const [week, setWeek] = useState(getWeekNumber(new Date()));
  const [data, setData] = useState<InsightsData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  function getWeekNumber(date: Date): number {
    const d = new Date(Date.UTC(date.getFullYear(), date.getMonth(), date.getDate()));
    const dayNum = d.getUTCDay() || 7;
    d.setUTCDate(d.getUTCDate() + 4 - dayNum);
    const yearStart = new Date(Date.UTC(d.getUTCFullYear(), 0, 1));
    return Math.ceil(((d.getTime() - yearStart.getTime()) / 86400000 + 1) / 7);
  }

  const fetchInsights = async () => {
    setLoading(true);
    setError(null);
    try {
      const base = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";
      const url =
        viewType === "monthly"
          ? `${base}/insights/monthly?year=${year}&month=${month}&limit=50`
          : `${base}/insights/weekly?year=${year}&week=${week}&limit=50`;
      
      // Add timeout to prevent hanging
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout
      
      const res = await fetch(url, { signal: controller.signal });
      clearTimeout(timeoutId);
      
      if (!res.ok) {
        const errorData = await res.json().catch(() => ({ detail: res.statusText }));
        throw new Error(errorData.detail || `Failed to fetch insights: ${res.statusText}`);
      }
      const insights = await res.json();
      setData(insights);
    } catch (err) {
      if (err instanceof Error) {
        if (err.name === "AbortError") {
          setError("Request timed out. Please check your database connection.");
        } else {
          setError(err.message);
        }
      } else {
        setError("Failed to load insights");
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInsights();
  }, [year, month, week, viewType]);

  const months = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
  ];

  const currentYear = new Date().getFullYear();
  const years = Array.from({ length: 3 }, (_, i) => currentYear - i);
  const weeks = Array.from({ length: 53 }, (_, i) => i + 1);

  const isMonthly = (data: InsightsData): data is MonthlyInsightsData => {
    return "month" in data;
  };

  return (
    <div className="space-y-8">
      <div className="space-y-4">
        <h1 className="text-4xl font-bold">Insights</h1>
        <p className="text-neutral-300 max-w-2xl text-lg">
          Discover the top podcasts and biggest gainers for any month or week. See who dominated the
          charts and who had the biggest momentum.
        </p>

        <div className="flex gap-2 border-b border-neutral-800">
          <button
            onClick={() => setViewType("monthly")}
            className={`px-4 py-2 font-medium transition ${
              viewType === "monthly"
                ? "border-b-2 border-white text-white"
                : "text-neutral-400 hover:text-neutral-300"
            }`}
          >
            Monthly
          </button>
          <button
            onClick={() => setViewType("weekly")}
            className={`px-4 py-2 font-medium transition ${
              viewType === "weekly"
                ? "border-b-2 border-white text-white"
                : "text-neutral-400 hover:text-neutral-300"
            }`}
          >
            Weekly
          </button>
        </div>

        <div className="flex gap-4 items-center flex-wrap">
          <div className="flex gap-2 items-center">
            <label htmlFor="year" className="text-sm font-medium">
              Year:
            </label>
            <select
              id="year"
              value={year}
              onChange={(e) => setYear(Number(e.target.value))}
              className="px-3 py-2 bg-neutral-900 border border-neutral-800 rounded text-white focus:outline-none focus:ring-2 focus:ring-white"
            >
              {years.map((y) => (
                <option key={y} value={y}>
                  {y}
                </option>
              ))}
            </select>
          </div>

          {viewType === "monthly" ? (
            <div className="flex gap-2 items-center">
              <label htmlFor="month" className="text-sm font-medium">
                Month:
              </label>
              <select
                id="month"
                value={month}
                onChange={(e) => setMonth(Number(e.target.value))}
                className="px-3 py-2 bg-neutral-900 border border-neutral-800 rounded text-white focus:outline-none focus:ring-2 focus:ring-white"
              >
                {months.map((m, i) => (
                  <option key={i + 1} value={i + 1}>
                    {m}
                  </option>
                ))}
              </select>
            </div>
          ) : (
            <div className="flex gap-2 items-center">
              <label htmlFor="week" className="text-sm font-medium">
                Week:
              </label>
              <select
                id="week"
                value={week}
                onChange={(e) => setWeek(Number(e.target.value))}
                className="px-3 py-2 bg-neutral-900 border border-neutral-800 rounded text-white focus:outline-none focus:ring-2 focus:ring-white"
              >
                {weeks.map((w) => (
                  <option key={w} value={w}>
                    Week {w}
                  </option>
                ))}
              </select>
            </div>
          )}

          <button
            onClick={fetchInsights}
            disabled={loading}
            className="px-4 py-2 bg-white text-black rounded font-medium hover:bg-neutral-200 transition disabled:opacity-50"
          >
            {loading ? "Loading..." : "Refresh"}
          </button>
        </div>
      </div>

      {error && (
        <div className="border border-red-800 bg-red-900/20 rounded p-4 text-red-400">
          {error}
        </div>
      )}

      {loading && !data && (
        <div className="py-12 text-center text-neutral-400">Loading insights...</div>
      )}

      {data && (
        <div className="space-y-8">
          <div className="border border-neutral-800 rounded-lg p-6 bg-neutral-900/50">
            <h2 className="text-2xl font-semibold mb-2">
              {isMonthly(data)
                ? `Top Podcasts in ${data.month_name} ${data.year}`
                : `Top Podcasts in Week ${data.week}, ${data.year}`}
            </h2>
            <p className="text-sm text-neutral-400 mb-4">
              Ranked by average rank during the {viewType === "monthly" ? "month" : "week"} (
              {data.start_date} to {data.end_date})
            </p>

            {data.top_podcasts.length === 0 ? (
              <p className="text-neutral-400 py-8 text-center">
                No data available for this {viewType === "monthly" ? "month" : "week"}. Make sure
                you have ingested data for this period.
              </p>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-neutral-800">
                      <th className="text-left py-3 px-4 font-medium">Rank</th>
                      <th className="text-left py-3 px-4 font-medium">Title</th>
                      <th className="text-left py-3 px-4 font-medium">Publisher</th>
                      <th className="text-left py-3 px-4 font-medium">Category</th>
                      <th className="text-right py-3 px-4 font-medium">Avg Rank</th>
                      <th className="text-right py-3 px-4 font-medium">Best</th>
                      <th className="text-right py-3 px-4 font-medium">Worst</th>
                      <th className="text-right py-3 px-4 font-medium">Avg Momentum</th>
                      <th className="text-right py-3 px-4 font-medium">Days</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.top_podcasts.map((podcast, idx) => (
                      <tr
                        key={podcast.id}
                        className="border-b border-neutral-800 hover:bg-neutral-900/50 transition"
                      >
                        <td className="py-3 px-4 font-medium">#{idx + 1}</td>
                        <td className="py-3 px-4">
                          <Link
                            href={`/podcast/${podcast.id}`}
                            className="text-white hover:underline font-medium"
                          >
                            {podcast.title}
                          </Link>
                        </td>
                        <td className="py-3 px-4 text-neutral-400">{podcast.publisher ?? "—"}</td>
                        <td className="py-3 px-4 text-neutral-400">{podcast.category ?? "—"}</td>
                        <td className="py-3 px-4 text-right font-mono">{podcast.avg_rank}</td>
                        <td className="py-3 px-4 text-right font-mono text-green-400">
                          {podcast.best_rank}
                        </td>
                        <td className="py-3 px-4 text-right font-mono text-red-400">
                          {podcast.worst_rank}
                        </td>
                        <td className="py-3 px-4 text-right font-mono">
                          {podcast.avg_momentum !== null
                            ? podcast.avg_momentum.toFixed(1)
                            : "—"}
                        </td>
                        <td className="py-3 px-4 text-right text-neutral-400">
                          {podcast.days_tracked}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          {data.biggest_gainers.length > 0 && (
            <div className="border border-neutral-800 rounded-lg p-6 bg-neutral-900/50">
              <h2 className="text-2xl font-semibold mb-4">Biggest Gainers</h2>
              <p className="text-sm text-neutral-400 mb-4">
                Podcasts with the largest {viewType === "monthly" ? "30-day" : "7-day"} rank
                improvements
              </p>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {data.biggest_gainers.map((gainer) => (
                  <Link
                    key={gainer.id}
                    href={`/podcast/${gainer.id}`}
                    className="border border-neutral-800 rounded-lg p-4 hover:bg-neutral-900/50 transition"
                  >
                    <h3 className="font-semibold mb-1 line-clamp-2">{gainer.title}</h3>
                    <p className="text-sm text-neutral-400 mb-2">{gainer.publisher ?? "—"}</p>
                    {viewType === "monthly" ? (
                      gainer.max_delta_30d !== null && (
                        <p className="text-green-400 font-mono text-sm">
                          +{gainer.max_delta_30d} rank improvement
                        </p>
                      )
                    ) : (
                      gainer.max_delta_7d !== null && (
                        <p className="text-green-400 font-mono text-sm">
                          +{gainer.max_delta_7d} rank improvement
                        </p>
                      )
                    )}
                  </Link>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

