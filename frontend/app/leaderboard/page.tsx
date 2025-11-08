import Link from "next/link";
import LeaderboardClient from "./leaderboard-client";

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

// Force dynamic rendering to avoid build-time fetch
export const dynamic = 'force-dynamic';

async function fetchLeaderboard(
  category?: string,
  country?: string,
  sortBy?: string,
  search?: string,
  interval?: string
) {
  try {
    const base = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";
    const params = new URLSearchParams();
    if (category) params.set("category", category);
    if (country) params.set("country", country);
    if (sortBy) params.set("sort_by", sortBy);
    if (search) params.set("search", search);
    if (interval) params.set("interval", interval);
    const url = `${base}/leaderboard${params.toString() ? `?${params}` : ""}`;
    const res = await fetch(url, { 
      cache: "no-store" // Dynamic page, don't cache
    });
    if (!res.ok) return { items: [] };
    return res.json();
  } catch (error) {
    console.warn("Failed to fetch leaderboard:", error);
    return { items: [] };
  }
}

export default async function LeaderboardPage({
  searchParams,
}: {
  searchParams?: {
    category?: string;
    country?: string;
    sort_by?: string;
    search?: string;
    interval?: string;
  };
}) {
  const category = searchParams?.category;
  const country = searchParams?.country;
  const sortBy = searchParams?.sort_by;
  const search = searchParams?.search;
  const interval = searchParams?.interval || "daily";
  const data = await fetchLeaderboard(category, country, sortBy, search, interval);
  const items: LeaderboardItem[] = data.items ?? [];

  return (
    <LeaderboardClient
      items={items}
      initialCategory={category}
      initialCountry={country}
      initialSort={sortBy}
      initialSearch={search}
      initialInterval={interval}
    />
  );
}
