import Link from "next/link";

async function fetchTrending() {
  const base = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";
  const res = await fetch(`${base}/trending?limit=10`, { next: { revalidate: 60 } });
  if (!res.ok) return { items: [] };
  return res.json();
}

export default async function HomePage() {
  const trending = await fetchTrending();
  const trendingItems = trending.items ?? [];

  return (
    <div className="space-y-8">
      <div className="space-y-4">
        <h1 className="text-4xl font-bold">See who's rising in podcasting</h1>
        <p className="text-neutral-300 max-w-2xl text-lg">
          PodCharts is the public scoreboard for podcasts. Explore daily rankings, growth, and momentum across
          categories.
        </p>
        <div className="flex gap-3 flex-wrap">
          <Link
            href="/leaderboard"
            className="px-6 py-3 rounded bg-white text-black font-medium hover:bg-neutral-200 transition"
          >
            View Leaderboard
          </Link>
          <Link
            href="/trending"
            className="px-6 py-3 rounded border border-neutral-700 font-medium hover:bg-neutral-900 transition"
          >
            🔥 Trending
          </Link>
          <Link
            href="/api"
            className="px-6 py-3 rounded border border-neutral-700 font-medium hover:bg-neutral-900 transition"
          >
            API Docs
          </Link>
        </div>
      </div>

      {trendingItems.length > 0 && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-semibold">🔥 Trending Now</h2>
            <Link href="/leaderboard?sort_by=momentum" className="text-sm text-neutral-400 hover:text-neutral-300">
              View All →
            </Link>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {trendingItems.slice(0, 6).map((item: any) => (
              <Link
                key={item.id}
                href={`/podcast/${item.id}`}
                className="border border-neutral-800 rounded-lg p-4 hover:bg-neutral-900/50 transition space-y-2"
              >
                <div className="flex items-start justify-between">
                  <h3 className="font-semibold line-clamp-2 flex-1">{item.title}</h3>
                  <span className="px-2 py-0.5 bg-green-900/30 text-green-400 rounded text-xs font-medium ml-2">
                    🔥
                  </span>
                </div>
                <p className="text-sm text-neutral-400">{item.publisher ?? "—"}</p>
                <div className="flex items-center gap-4 text-sm">
                  <span className="text-neutral-500">Rank #{item.rank ?? "—"}</span>
                  {item.momentum_score !== null && (
                    <span className="text-green-400 font-mono">+{item.momentum_score.toFixed(1)} momentum</span>
                  )}
                </div>
              </Link>
            ))}
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-8 border-t border-neutral-800">
        <div className="space-y-2">
          <h3 className="font-semibold">Real-time Rankings</h3>
          <p className="text-sm text-neutral-400">
            Daily updated leaderboards showing the top podcasts across all categories.
          </p>
        </div>
        <div className="space-y-2">
          <h3 className="font-semibold">Growth Metrics</h3>
          <p className="text-sm text-neutral-400">
            Track momentum, 7-day and 30-day changes to see which shows are rising.
          </p>
        </div>
        <div className="space-y-2">
          <h3 className="font-semibold">Compare & Analyze</h3>
          <p className="text-sm text-neutral-400">
            Side-by-side comparisons and detailed analytics for any podcast.
          </p>
        </div>
      </div>
    </div>
  );
}
