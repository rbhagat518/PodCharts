"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";

type HistoryPoint = {
  date: string;
  rank: number | null;
  delta_7d: number | null;
  delta_30d: number | null;
  momentum_score: number | null;
};

type CompareData = {
  id1: string;
  id2: string;
  podcast1: {
    id: string;
    title: string;
    publisher: string | null;
    category: string | null;
  };
  podcast2: {
    id: string;
    title: string;
    publisher: string | null;
    category: string | null;
  };
  series: Array<{
    podcast_id: string;
    data: HistoryPoint[];
  }>;
};

async function fetchCompare(id1: string, id2: string): Promise<CompareData | null> {
  try {
    const base = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";
    const params = new URLSearchParams({ id1, id2 });
    const res = await fetch(`${base}/compare?${params}`, { 
      cache: "no-store" // Client-side fetch, don't cache
    });
    if (!res.ok) return null;
    return res.json();
  } catch (error) {
    console.warn("Failed to fetch compare:", error);
    return null;
  }
}

type Props = {
  initialId1?: string;
  initialId2?: string;
};

export default function CompareClient({ initialId1, initialId2 }: Props) {
  const router = useRouter();
  const [id1, setId1] = useState(initialId1 || "");
  const [id2, setId2] = useState(initialId2 || "");
  const [data, setData] = useState<CompareData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch initial data if IDs are provided
  useEffect(() => {
    if (initialId1 && initialId2 && !data) {
      setLoading(true);
      fetchCompare(initialId1, initialId2)
        .then((result) => {
          if (result) {
            setData(result);
          } else {
            setError("Failed to fetch comparison data. Check that both podcast IDs are valid.");
          }
        })
        .catch(() => {
          setError("An error occurred while fetching data.");
        })
        .finally(() => {
          setLoading(false);
        });
    }
  }, [initialId1, initialId2, data]);

  const handleCompare = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!id1 || !id2) {
      setError("Please enter both podcast IDs");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const result = await fetchCompare(id1, id2);
      if (result) {
        setData(result);
        router.push(`/compare?id1=${id1}&id2=${id2}`);
      } else {
        setError("Failed to fetch comparison data. Check that both podcast IDs are valid.");
      }
    } catch (err) {
      setError("An error occurred while fetching data.");
    } finally {
      setLoading(false);
    }
  };

  const chartData =
    data?.series
      .flatMap((s) =>
        s.data
          .filter((d) => d.rank !== null)
          .map((d) => ({
            date: new Date(d.date).toLocaleDateString("en-US", { month: "short", day: "numeric" }),
            [data.podcast1.title]: s.podcast_id === data.id1 ? d.rank : null,
            [data.podcast2.title]: s.podcast_id === data.id2 ? d.rank : null,
            fullDate: d.date,
          }))
      )
      .reduce((acc, curr) => {
        const existing = acc.find((a) => a.date === curr.date);
        if (existing) {
          existing[data!.podcast1.title] = curr[data!.podcast1.title] ?? existing[data!.podcast1.title];
          existing[data!.podcast2.title] = curr[data!.podcast2.title] ?? existing[data!.podcast2.title];
        } else {
          acc.push(curr);
        }
        return acc;
      }, [] as any[])
      .sort((a, b) => new Date(a.fullDate).getTime() - new Date(b.fullDate).getTime()) ?? [];

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">Compare Podcasts</h1>

      <form onSubmit={handleCompare} className="flex gap-2">
        <input
          type="text"
          value={id1}
          onChange={(e) => setId1(e.target.value)}
          placeholder="Podcast ID 1"
          className="flex-1 px-3 py-2 bg-neutral-900 border border-neutral-800 rounded"
        />
        <input
          type="text"
          value={id2}
          onChange={(e) => setId2(e.target.value)}
          placeholder="Podcast ID 2"
          className="flex-1 px-3 py-2 bg-neutral-900 border border-neutral-800 rounded"
        />
        <button
          type="submit"
          disabled={loading}
          className="px-4 py-2 rounded bg-white text-black hover:bg-neutral-200 disabled:opacity-50"
        >
          {loading ? "Loading..." : "Compare"}
        </button>
      </form>

      {error && <div className="p-4 bg-red-900/20 border border-red-800 rounded text-red-400">{error}</div>}

      {data && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="border border-neutral-800 rounded p-4">
              <h3 className="font-semibold mb-2">{data.podcast1.title}</h3>
              <p className="text-sm text-neutral-400">Publisher: {data.podcast1.publisher ?? "—"}</p>
              <p className="text-sm text-neutral-400">Category: {data.podcast1.category ?? "—"}</p>
            </div>
            <div className="border border-neutral-800 rounded p-4">
              <h3 className="font-semibold mb-2">{data.podcast2.title}</h3>
              <p className="text-sm text-neutral-400">Publisher: {data.podcast2.publisher ?? "—"}</p>
              <p className="text-sm text-neutral-400">Category: {data.podcast2.category ?? "—"}</p>
            </div>
          </div>

          {chartData.length > 0 ? (
            <div className="border border-neutral-800 rounded p-6">
              <h2 className="text-lg font-semibold mb-4">Rank Comparison (Last 90 Days)</h2>
              <div className="h-96">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={chartData}>
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
                    <Legend />
                    <Line
                      type="monotone"
                      dataKey={data.podcast1.title}
                      stroke="#3b82f6"
                      strokeWidth={2}
                      dot={{ fill: "#3b82f6", r: 3 }}
                      activeDot={{ r: 5 }}
                    />
                    <Line
                      type="monotone"
                      dataKey={data.podcast2.title}
                      stroke="#ef4444"
                      strokeWidth={2}
                      dot={{ fill: "#ef4444", r: 3 }}
                      activeDot={{ r: 5 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
              <p className="text-xs text-neutral-500 mt-2">
                Lower rank numbers indicate higher position (rank 1 = #1 podcast)
              </p>
            </div>
          ) : (
            <div className="border border-neutral-800 rounded p-6 text-center text-neutral-400">
              <p>No historical data available for comparison.</p>
            </div>
          )}
        </div>
      )}

      {!data && !error && !loading && (
        <div className="border border-neutral-800 rounded p-6 text-center text-neutral-400">
          <p>Enter two podcast IDs above to compare their rankings.</p>
          <p className="text-sm mt-2">You can find podcast IDs on the leaderboard page.</p>
        </div>
      )}
    </div>
  );
}

