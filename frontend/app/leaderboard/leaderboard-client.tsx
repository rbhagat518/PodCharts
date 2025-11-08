"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState, useMemo } from "react";

type LeaderboardItem = {
  id: string;
  title: string;
  publisher: string | null;
  category: string | null;
  country: string | null;
  rank: number | null;
  delta_7d: number | null;
  delta_30d: number | null;
  momentum_score: number | null;
};

type Props = {
  items: LeaderboardItem[];
  initialCategory?: string;
  initialCountry?: string;
  initialSort?: string;
  initialSearch?: string;
  initialInterval?: string;
};

function formatDelta(delta: number | null): string {
  if (delta === null) return "—";
  if (delta > 0) return `+${delta}`;
  return String(delta);
}

function formatMomentum(score: number | null): string {
  if (score === null) return "—";
  return score.toFixed(1);
}

function exportToCSV(items: LeaderboardItem[]) {
  const headers = ["Rank", "Title", "Publisher", "Category", "Country", "7d Δ", "30d Δ", "Momentum", "ID"];
  const rows = items.map((item) => [
    item.rank ?? "",
    item.title,
    item.publisher ?? "",
    item.category ?? "",
    item.country ?? "",
    item.delta_7d ?? "",
    item.delta_30d ?? "",
    item.momentum_score ?? "",
    item.id,
  ]);

  const csv = [
    headers.join(","),
    ...rows.map((row) => row.map((cell) => `"${String(cell).replace(/"/g, '""')}"`).join(",")),
  ].join("\n");

  const blob = new Blob([csv], { type: "text/csv" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `podcharts-leaderboard-${new Date().toISOString().split("T")[0]}.csv`;
  a.click();
  URL.revokeObjectURL(url);
}

export default function LeaderboardClient({
  items,
  initialCategory,
  initialCountry,
  initialSort,
  initialSearch,
  initialInterval,
}: Props) {
  const router = useRouter();
  const [category, setCategory] = useState(initialCategory || "");
  const [sortBy, setSortBy] = useState(initialSort || "rank");
  const [search, setSearch] = useState(initialSearch || "");
  const [interval, setInterval] = useState(initialInterval || "daily");

  const categories = [
    { value: "", label: "All Categories" },
    { value: "top", label: "Top" },
    { value: "technology", label: "Technology" },
    { value: "news", label: "News" },
    { value: "comedy", label: "Comedy" },
    { value: "business", label: "Business" },
    { value: "health", label: "Health" },
    { value: "education", label: "Education" },
  ];

  const sortOptions = [
    { value: "rank", label: "Rank" },
    { value: "momentum", label: "Momentum" },
    { value: "delta_7d", label: "7d Change" },
    { value: "delta_30d", label: "30d Change" },
  ];

  const handleFilterChange = () => {
    const params = new URLSearchParams();
    if (category) params.set("category", category);
    if (initialCountry) params.set("country", initialCountry);
    if (sortBy !== "rank") params.set("sort_by", sortBy);
    if (search) params.set("search", search);
    if (interval !== "daily") params.set("interval", interval);
    router.push(`/leaderboard${params.toString() ? `?${params}` : ""}`);
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    handleFilterChange();
  };

  const filteredItems = useMemo(() => {
    let filtered = [...items];

    if (search) {
      const searchLower = search.toLowerCase();
      filtered = filtered.filter(
        (item) =>
          item.title.toLowerCase().includes(searchLower) ||
          (item.publisher && item.publisher.toLowerCase().includes(searchLower))
      );
    }

    return filtered;
  }, [items, search]);

  const isTrending = (item: LeaderboardItem) => {
    return item.momentum_score !== null && item.momentum_score > 0;
  };

  const isRising = (item: LeaderboardItem) => {
    return item.delta_7d !== null && item.delta_7d > 0;
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between flex-wrap gap-4">
        <h1 className="text-2xl font-semibold">Leaderboard</h1>
        <div className="flex gap-2 flex-wrap">
          <form onSubmit={handleSearch} className="flex gap-2">
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search podcasts..."
              className="px-3 py-1.5 bg-neutral-900 border border-neutral-800 rounded text-sm w-48"
            />
            <button
              type="submit"
              className="px-3 py-1.5 bg-neutral-800 border border-neutral-700 rounded text-sm hover:bg-neutral-700"
            >
              Search
            </button>
          </form>
          <select
            value={category}
            onChange={(e) => {
              setCategory(e.target.value);
              setTimeout(handleFilterChange, 0);
            }}
            className="px-3 py-1.5 bg-neutral-900 border border-neutral-800 rounded text-sm"
          >
            {categories.map((cat) => (
              <option key={cat.value} value={cat.value}>
                {cat.label}
              </option>
            ))}
          </select>
          <select
            value={interval}
            onChange={(e) => {
              setInterval(e.target.value);
              setTimeout(handleFilterChange, 0);
            }}
            className="px-3 py-1.5 bg-neutral-900 border border-neutral-800 rounded text-sm"
          >
            <option value="daily">Daily</option>
            <option value="weekly">Weekly</option>
            <option value="monthly">Monthly</option>
          </select>
          <select
            value={sortBy}
            onChange={(e) => {
              setSortBy(e.target.value);
              setTimeout(handleFilterChange, 0);
            }}
            className="px-3 py-1.5 bg-neutral-900 border border-neutral-800 rounded text-sm"
          >
            {sortOptions.map((opt) => (
              <option key={opt.value} value={opt.value}>
                Sort: {opt.label}
              </option>
            ))}
          </select>
          <button
            onClick={() => exportToCSV(filteredItems)}
            className="px-3 py-1.5 bg-neutral-800 border border-neutral-700 rounded text-sm hover:bg-neutral-700"
          >
            Export CSV
          </button>
        </div>
      </div>

      {filteredItems.length === 0 ? (
        <div className="py-12 text-center text-neutral-400">
          <p>No data available yet.</p>
          <p className="text-sm mt-2">Run the ingestion script to populate data.</p>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left border-b border-neutral-800">
                <th className="py-3 pr-4 font-medium">Rank</th>
                <th className="py-3 pr-4 font-medium">Show</th>
                <th className="py-3 pr-4 font-medium">ID</th>
                <th className="py-3 pr-4 font-medium">Publisher</th>
                <th className="py-3 pr-4 font-medium">Category</th>
                <th className="py-3 pr-4 font-medium text-right">7d Δ</th>
                <th className="py-3 pr-4 font-medium text-right">30d Δ</th>
                <th className="py-3 pr-4 font-medium text-right">Momentum</th>
                <th className="py-3 pr-4 font-medium text-center">Trend</th>
              </tr>
            </thead>
            <tbody>
              {filteredItems.map((item) => (
                <tr key={item.id} className="border-b border-neutral-900 hover:bg-neutral-900/50">
                  <td className="py-3 pr-4 font-mono text-neutral-400">{item.rank ?? "—"}</td>
                  <td className="py-3 pr-4">
                    <Link href={`/podcast/${item.id}`} className="hover:underline font-medium">
                      {item.title}
                    </Link>
                  </td>
                  <td className="py-3 pr-4">
                    <code className="text-xs font-mono text-neutral-500 bg-neutral-900 px-2 py-1 rounded">
                      {item.id}
                    </code>
                  </td>
                  <td className="py-3 pr-4 text-neutral-400">{item.publisher ?? "—"}</td>
                  <td className="py-3 pr-4">
                    <span className="px-2 py-0.5 bg-neutral-800 rounded text-xs text-neutral-300">
                      {item.category ?? "—"}
                    </span>
                  </td>
                  <td className="py-3 pr-4 text-right font-mono text-sm">
                    <span
                      className={
                        item.delta_7d !== null && item.delta_7d > 0
                          ? "text-green-400"
                          : item.delta_7d !== null && item.delta_7d < 0
                          ? "text-red-400"
                          : "text-neutral-400"
                      }
                    >
                      {formatDelta(item.delta_7d)}
                    </span>
                  </td>
                  <td className="py-3 pr-4 text-right font-mono text-sm">
                    <span
                      className={
                        item.delta_30d !== null && item.delta_30d > 0
                          ? "text-green-400"
                          : item.delta_30d !== null && item.delta_30d < 0
                          ? "text-red-400"
                          : "text-neutral-400"
                      }
                    >
                      {formatDelta(item.delta_30d)}
                    </span>
                  </td>
                  <td className="py-3 pr-4 text-right font-mono text-sm text-neutral-400">
                    {formatMomentum(item.momentum_score)}
                  </td>
                  <td className="py-3 pr-4 text-center">
                    {isTrending(item) && (
                      <span className="px-2 py-0.5 bg-green-900/30 text-green-400 rounded text-xs font-medium">
                        🔥 Trending
                      </span>
                    )}
                    {isRising(item) && !isTrending(item) && (
                      <span className="px-2 py-0.5 bg-blue-900/30 text-blue-400 rounded text-xs font-medium">
                        ↑ Rising
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
