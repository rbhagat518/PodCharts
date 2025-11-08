import Link from "next/link";
import PodcastClient from "./podcast-client";

type Props = { params: { id: string } };

async function fetchPodcast(id: string) {
  const base = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";
  const res = await fetch(`${base}/podcast/${id}`, { next: { revalidate: 60 } });
  if (!res.ok) {
    if (res.status === 404) return null;
    return null;
  }
  return res.json();
}

export default async function PodcastPage({ params }: Props) {
  const data = await fetchPodcast(params.id);

  if (!data) {
    return (
      <div className="space-y-4">
        <h1 className="text-xl font-semibold">Podcast Not Found</h1>
        <p className="text-neutral-400">The podcast you're looking for doesn't exist.</p>
        <Link href="/leaderboard" className="text-blue-400 hover:underline">
          ← Back to Leaderboard
        </Link>
      </div>
    );
  }

  return <PodcastClient data={data} />;
}
