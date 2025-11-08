"use client";

import Link from "next/link";

export default function SignupPage() {
  return (
    <div className="max-w-md mx-auto space-y-6">
      <div className="space-y-2 text-center">
        <h1 className="text-3xl font-bold">Sign Up</h1>
        <p className="text-neutral-400">Create an account to get started with PodCharts</p>
      </div>

      <div className="border border-neutral-800 rounded-lg p-6 space-y-4">
        <div className="space-y-2">
          <label htmlFor="email" className="block text-sm font-medium">
            Email
          </label>
          <input
            type="email"
            id="email"
            name="email"
            className="w-full px-4 py-2 bg-neutral-900 border border-neutral-800 rounded text-white focus:outline-none focus:ring-2 focus:ring-white"
            placeholder="you@example.com"
          />
        </div>

        <div className="space-y-2">
          <label htmlFor="password" className="block text-sm font-medium">
            Password
          </label>
          <input
            type="password"
            id="password"
            name="password"
            className="w-full px-4 py-2 bg-neutral-900 border border-neutral-800 rounded text-white focus:outline-none focus:ring-2 focus:ring-white"
            placeholder="••••••••"
          />
        </div>

        <div className="space-y-2">
          <label htmlFor="confirmPassword" className="block text-sm font-medium">
            Confirm Password
          </label>
          <input
            type="password"
            id="confirmPassword"
            name="confirmPassword"
            className="w-full px-4 py-2 bg-neutral-900 border border-neutral-800 rounded text-white focus:outline-none focus:ring-2 focus:ring-white"
            placeholder="••••••••"
          />
        </div>

        <button
          type="button"
          className="w-full px-4 py-2 bg-white text-black rounded font-medium hover:bg-neutral-200 transition"
          onClick={() => {
            alert("Authentication integration coming soon! This will connect to Supabase Auth.");
          }}
        >
          Sign Up
        </button>

        <div className="text-center text-sm text-neutral-400">
          <p>
            Already have an account?{" "}
            <Link href="/login" className="text-white hover:underline">
              Sign in
            </Link>
          </p>
        </div>
      </div>

      <div className="text-center">
        <Link href="/" className="text-sm text-neutral-400 hover:text-neutral-300">
          ← Back to home
        </Link>
      </div>
    </div>
  );
}

