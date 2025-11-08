import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "PodCharts",
  description: "The public scoreboard for podcasts"
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-neutral-950 text-neutral-100">
        <header className="border-b border-neutral-800">
          <div className="mx-auto max-w-6xl px-4 py-4 flex items-center justify-between">
            <a href="/" className="font-semibold text-lg">PodCharts</a>
            <nav className="text-sm space-x-6">
              <a href="/leaderboard" className="hover:text-neutral-300 transition">Leaderboard</a>
            <a href="/trending" className="hover:text-neutral-300 transition">🔥 Trending</a>
            <a href="/insights" className="hover:text-neutral-300 transition">📊 Insights</a>
            <a href="/most-watched" className="hover:text-neutral-300 transition">👀 Most Watched</a>
            <a href="/compare" className="hover:text-neutral-300 transition">Compare</a>
              <a href="/pricing" className="hover:text-neutral-300 transition">Pricing</a>
              <a href="/dashboard" className="hover:text-neutral-300 transition">Dashboard</a>
            </nav>
          </div>
        </header>
        <main className="mx-auto max-w-6xl px-4 py-8">{children}</main>
      </body>
    </html>
  );
}


