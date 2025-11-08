"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";

type TrendingItem = {
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
  items: TrendingItem[];
  initialCategory?: string;
};

function formatDelta(delta: number | null): string {
  if (delta === null) return "—";
  if (delta > 0) return `+${delta}`;
  return String(delta);
}

export default function TrendingClient({ items, initialCategory }: Props) {
  const router = useRouter();
  const [category, setCategory] = useState(initialCategory || "");

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

  const handleCategoryChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newCategory = e.target.value;
    setCategory(newCategory);
    const params = new URLSearchParams();
    if (newCategory) params.set("category", newCategory);
    router.push(`/trending${params.toString() ? `?${params}` : ""}`);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold flex items-center gap-2">
            🔥 Trending Podcasts
          </h1>
          <p className="text-sm text-neutral-400 mt-1">
            Shows with the highest momentum and fastest growth
          </p>
        </div>
        <select
          value={category}
          onChange={handleCategoryChange}
          className="px-3 py-1.5 bg-neutral-900 border border-neutral-800 rounded text-sm"
        >
          {categories.map((cat) => (
            <option key={cat.value} value={cat.value}>
              {cat.label}
            </option>
          ))}
        </select>
      </div>

      {items.length === 0 ? (
        <div className="py-12 text-center text-neutral-400">
          <p>No trending data available yet.</p>
          <p className="text-sm mt-2">Run the ingestion script to populate data.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {items.map((item, index) => (
            <Link
              key={item.id}
              href={`/podcast/${item.id}`}
              className="border border-neutral-800 rounded-lg p-4 hover:bg-neutral-900/50 transition space-y-3"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-xs font-mono text-neutral-500">#{index + 1}</span>
                    <span className="px-2 py-0.5 bg-green-900/30 text-green-400 rounded text-xs font-medium">
                      🔥 Trending
                    </span>
                  </div>
                  <h3 className="font-semibold line-clamp-2">{item.title}</h3>
                </div>
              </div>
              <p className="text-sm text-neutral-400">{item.publisher ?? "—"}</p>
              <div className="flex items-center gap-4 text-sm pt-2 border-t border-neutral-800">
                <div>
                  <span className="text-neutral-500">Rank:</span>{" "}
                  <span className="font-mono text-neutral-300">#{item.rank ?? "—"}</span>
                </div>
                <div>
                  <span className="text-neutral-500">Momentum:</span>{" "}
                  <span className="font-mono text-green-400">
                    {item.momentum_score !== null ? `+${item.momentum_score.toFixed(1)}` : "—"}
                  </span>
                </div>
              </div>
              <div className="flex items-center gap-4 text-xs text-neutral-500">
                {item.delta_7d !== null && (
                  <span>
                    7d:{" "}
                    <span
                      className={
                        item.delta_7d > 0 ? "text-green-400" : item.delta_7d < 0 ? "text-red-400" : "text-neutral-400"
                      }
                    >
                      {formatDelta(item.delta_7d)}
                    </span>
                  </span>
                )}
                {item.category && (
                  <span className="px-2 py-0.5 bg-neutral-800 rounded text-xs">{item.category}</span>
                )}
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}

