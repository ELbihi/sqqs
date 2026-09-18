"use client";

import { usePathname, useRouter } from "next/navigation";
import { useEffect } from "react";

import AppHeader from "@/components/AppHeader";
import BottomNav from "@/components/BottomNav";
import { useAuth } from "@/lib/store";

const TITLES: Record<string, string> = {
  "/studio": "Studio",
  "/library": "Library",
  "/generations": "History",
  "/settings": "Account",
  "/billing": "Credits",
};

export default function AppLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const { user, loading, loadMe } = useAuth();

  useEffect(() => {
    loadMe();
  }, [loadMe]);

  useEffect(() => {
    if (!loading && !user) router.replace("/login");
  }, [loading, user, router]);

  if (loading || !user) {
    return (
      <div className="flex min-h-screen items-center justify-center text-ink-muted">
        Loading…
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-canvas-base">
      <AppHeader title={TITLES[pathname] || "Studio"} />
      <main className="mx-auto w-full max-w-md px-5 pb-28 pt-4 sm:max-w-3xl sm:px-6 lg:max-w-6xl lg:px-8 lg:pb-16 lg:pt-8">
        {children}
      </main>
      <BottomNav />
    </div>
  );
}
