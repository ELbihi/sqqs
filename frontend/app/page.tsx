"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";

import { getToken } from "@/lib/api";

export default function Root() {
  const router = useRouter();
  useEffect(() => {
    router.replace(getToken() ? "/studio" : "/login");
  }, [router]);
  return <div className="flex min-h-screen items-center justify-center text-ink-muted">Loading…</div>;
}
