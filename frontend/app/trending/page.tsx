import Link from "next/link";
import TrendingClient from "./trending-client";

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

async function fetchTrending(category?: string) {
  const base = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";
  const params = new URLSearchParams();
  if (category) params.set("category", category);
  const url = `${base}/trending${params.toString() ? `?${params}` : ""}`;
  const res = await fetch(url, { next: { revalidate: 60 } });
  if (!res.ok) return { items: [] };
  return res.json();
}

export default async function TrendingPage({
  searchParams,
}: {
  searchParams?: { category?: string };
}) {
  const category = searchParams?.category;
  const data = await fetchTrending(category);
  const items: TrendingItem[] = data.items ?? [];

  return <TrendingClient items={items} initialCategory={category} />;
}

