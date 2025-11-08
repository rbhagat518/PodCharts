"use client";

import Link from "next/link";
import { useState } from "react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ComposedChart, Bar } from "recharts";

type HistoryPoint = {
  date: string;
  rank: number | null;
  delta_7d: number | null;
  delta_30d: number | null;
  momentum_score: number | null;
};

type PodcastData = {
  id: string;
  title: string;
  publisher: string | null;
  category: string | null;
  rss_url: string | null;
  country: string | null;
  created_at: string | null;
  history: HistoryPoint[];
};

type Props = {
  data: PodcastData;
};

function shareRankCard(data: PodcastData, currentRank: number | null) {
  const shareText = `${data.title} is ranked #${currentRank ?? "?"} on PodCharts! 🔥\n\nView full stats: ${window.location.href}`;
  
  if (navigator.share) {
    navigator.share({
      title: `${data.title} - PodCharts`,
      text: shareText,
      url: window.location.href,
    }).catch(() => {
      // Fallback to clipboard
      navigator.clipboard.writeText(shareText);
      alert("Rank card copied to clipboard!");
    });
  } else {
    navigator.clipboard.writeText(shareText);
    alert("Rank card copied to clipboard!");
  }
}

export default function PodcastClient({ data }: Props) {
  const [chartType, setChartType] = useState<"rank" | "momentum" | "combined">("rank");
  
  const history: HistoryPoint[] = data.history ?? [];
  const rankChartData = history
    .filter((h) => h.rank !== null)
    .map((h) => ({
      date: new Date(h.date).toLocaleDateString("en-US", { month: "short", day: "numeric" }),
      rank: h.rank,
      momentum: h.momentum_score,
      delta_7d: h.delta_7d,
      delta_30d: h.delta_30d,
      fullDate: h.date,
    }))
    .reverse();

  const currentRank = history[history.length - 1]?.rank ?? null;
  const delta7d = history[history.length - 1]?.delta_7d ?? null;
  const delta30d = history[history.length - 1]?.delta_30d ?? null;
  const momentum = history[history.length - 1]?.momentum_score ?? null;

  return (
    <div className="space-y-6">
      <div>
        <Link href="/leaderboard" className="text-sm text-neutral-400 hover:underline mb-4 inline-block">
          ← Back to Leaderboard
        </Link>
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-2xl font-semibold">{data.title}</h1>
            <div className="mt-2 space-y-1 text-sm text-neutral-400">
              <p>Publisher: {data.publisher ?? "—"}</p>
              <p>Category: {data.category ?? "—"}</p>
              {data.country && <p>Country: {data.country}</p>}
            </div>
          </div>
          <button
            onClick={() => shareRankCard(data, currentRank)}
            className="px-4 py-2 bg-neutral-800 border border-neutral-700 rounded hover:bg-neutral-700 transition text-sm"
          >
            📤 Share Rank
          </button>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="border border-neutral-800 rounded p-4">
          <div className="text-xs text-neutral-400 mb-1">Current Rank</div>
          <div className="text-2xl font-mono font-semibold">{currentRank ?? "—"}</div>
        </div>
        <div className="border border-neutral-800 rounded p-4">
          <div className="text-xs text-neutral-400 mb-1">7d Change</div>
          <div
            className={`text-2xl font-mono font-semibold ${
              delta7d !== null && delta7d > 0
                ? "text-green-400"
                : delta7d !== null && delta7d < 0
                ? "text-red-400"
                : "text-neutral-400"
            }`}
          >
            {delta7d !== null ? (delta7d > 0 ? `+${delta7d}` : String(delta7d)) : "—"}
          </div>
        </div>
        <div className="border border-neutral-800 rounded p-4">
          <div className="text-xs text-neutral-400 mb-1">30d Change</div>
          <div
            className={`text-2xl font-mono font-semibold ${
              delta30d !== null && delta30d > 0
                ? "text-green-400"
                : delta30d !== null && delta30d < 0
                ? "text-red-400"
                : "text-neutral-400"
            }`}
          >
            {delta30d !== null ? (delta30d > 0 ? `+${delta30d}` : String(delta30d)) : "—"}
          </div>
        </div>
        <div className="border border-neutral-800 rounded p-4">
          <div className="text-xs text-neutral-400 mb-1">Momentum</div>
          <div className="text-2xl font-mono font-semibold text-neutral-300">
            {momentum !== null ? momentum.toFixed(1) : "—"}
          </div>
        </div>
      </div>

      {rankChartData.length > 0 ? (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold">Analytics (Last 90 Days)</h2>
            <div className="flex gap-2">
              <button
                onClick={() => setChartType("rank")}
                className={`px-3 py-1 text-sm rounded ${
                  chartType === "rank" ? "bg-white text-black" : "bg-neutral-800 border border-neutral-700"
                }`}
              >
                Rank
              </button>
              <button
                onClick={() => setChartType("momentum")}
                className={`px-3 py-1 text-sm rounded ${
                  chartType === "momentum" ? "bg-white text-black" : "bg-neutral-800 border border-neutral-700"
                }`}
              >
                Momentum
              </button>
              <button
                onClick={() => setChartType("combined")}
                className={`px-3 py-1 text-sm rounded ${
                  chartType === "combined" ? "bg-white text-black" : "bg-neutral-800 border border-neutral-700"
                }`}
              >
                Combined
              </button>
            </div>
          </div>

          <div className="border border-neutral-800 rounded p-6">
            <div className="h-96">
              <ResponsiveContainer width="100%" height="100%">
                {chartType === "rank" ? (
                  <LineChart data={rankChartData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#404040" />
                    <XAxis
                      dataKey="date"
                      stroke="#a3a3a3"
                      style={{ fontSize: "12px" }}
                      angle={-45}
                      textAnchor="end"
                      height={60}
                    />
                    <YAxis
                      stroke="#a3a3a3"
                      style={{ fontSize: "12px" }}
                      reversed
                      domain={["auto", "auto"]}
                    />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: "#262626",
                        border: "1px solid #404040",
                        borderRadius: "4px",
                      }}
                      labelStyle={{ color: "#e5e5e5" }}
                    />
                    <Line
                      type="monotone"
                      dataKey="rank"
                      stroke="#3b82f6"
                      strokeWidth={2}
                      dot={{ fill: "#3b82f6", r: 3 }}
                      activeDot={{ r: 5 }}
                      name="Rank"
                    />
                  </LineChart>
                ) : chartType === "momentum" ? (
                  <LineChart data={rankChartData.filter((d) => d.momentum !== null)}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#404040" />
                    <XAxis
                      dataKey="date"
                      stroke="#a3a3a3"
                      style={{ fontSize: "12px" }}
                      angle={-45}
                      textAnchor="end"
                      height={60}
                    />
                    <YAxis
                      stroke="#a3a3a3"
                      style={{ fontSize: "12px" }}
                      domain={["auto", "auto"]}
                    />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: "#262626",
                        border: "1px solid #404040",
                        borderRadius: "4px",
                      }}
                      labelStyle={{ color: "#e5e5e5" }}
                    />
                    <Line
                      type="monotone"
                      dataKey="momentum"
                      stroke="#10b981"
                      strokeWidth={2}
                      dot={{ fill: "#10b981", r: 3 }}
                      activeDot={{ r: 5 }}
                      name="Momentum"
                    />
                  </LineChart>
                ) : (
                  <ComposedChart data={rankChartData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#404040" />
                    <XAxis
                      dataKey="date"
                      stroke="#a3a3a3"
                      style={{ fontSize: "12px" }}
                      angle={-45}
                      textAnchor="end"
                      height={60}
                    />
                    <YAxis
                      yAxisId="left"
                      stroke="#a3a3a3"
                      style={{ fontSize: "12px" }}
                      reversed
                      domain={["auto", "auto"]}
                    />
                    <YAxis
                      yAxisId="right"
                      orientation="right"
                      stroke="#a3a3a3"
                      style={{ fontSize: "12px" }}
                      domain={["auto", "auto"]}
                    />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: "#262626",
                        border: "1px solid #404040",
                        borderRadius: "4px",
                      }}
                      labelStyle={{ color: "#e5e5e5" }}
                    />
                    <Legend />
                    <Line
                      yAxisId="left"
                      type="monotone"
                      dataKey="rank"
                      stroke="#3b82f6"
                      strokeWidth={2}
                      dot={{ fill: "#3b82f6", r: 3 }}
                      activeDot={{ r: 5 }}
                      name="Rank"
                    />
                    <Line
                      yAxisId="right"
                      type="monotone"
                      dataKey="momentum"
                      stroke="#10b981"
                      strokeWidth={2}
                      dot={{ fill: "#10b981", r: 3 }}
                      activeDot={{ r: 5 }}
                      name="Momentum"
                    />
                    <Bar
                      yAxisId="right"
                      dataKey="delta_7d"
                      fill="#ef4444"
                      opacity={0.3}
                      name="7d Change"
                    />
                  </ComposedChart>
                )}
              </ResponsiveContainer>
            </div>
            <p className="text-xs text-neutral-500 mt-2">
              Lower rank numbers indicate higher position (rank 1 = #1 podcast)
            </p>
          </div>
        </div>
      ) : (
        <div className="border border-neutral-800 rounded p-6 text-center text-neutral-400">
          <p>No historical data available yet.</p>
        </div>
      )}
    </div>
  );
}
