"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { TABS } from "@/components/BottomNav";
import { useAuth } from "@/lib/store";

export default function AppHeader({ title = "Studio" }: { title?: string }) {
  const user = useAuth((s) => s.user);
  const pathname = usePathname();
  const initial = (user?.full_name || user?.email || "?").charAt(0).toUpperCase();

  return (
    <header className="sticky top-0 z-40 border-b border-hairline bg-canvas-base/90 backdrop-blur-xl pt-[env(safe-area-inset-top)]">
      <div className="mx-auto flex h-16 w-full max-w-md items-center justify-between gap-6 px-5 sm:max-w-3xl lg:h-20 lg:max-w-6xl lg:px-8">
        {/* Brand */}
        <Link href="/studio" className="flex shrink-0 items-center gap-2.5">
          <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-ink text-canvas-base">
            <span className="material-symbols-outlined text-[18px]">apparel</span>
          </span>
          <span className="leading-tight">
            <span className="block text-[10px] font-semibold uppercase tracking-[0.12em] text-ink-muted">
              AI Virtual Studio
            </span>
            <span className="block text-lg font-semibold tracking-tight lg:hidden">{title}</span>
            <span className="hidden text-lg font-semibold tracking-tight lg:block">Studio</span>
          </span>
        </Link>

        {/* Desktop nav */}
        <nav className="hidden flex-1 items-center justify-center gap-1 lg:flex">
          {TABS.map((t) => {
            const active = pathname === t.href || pathname.startsWith(t.href + "/");
            return (
              <Link
                key={t.href}
                href={t.href}
                className={`flex h-10 items-center gap-2 rounded-full px-4 text-sm font-medium transition ${
                  active ? "bg-canvas-subtle text-ink" : "text-ink-muted hover:text-ink"
                }`}
              >
                <span className="material-symbols-outlined text-[19px]">{t.icon}</span>
                {t.label}
              </Link>
            );
          })}
        </nav>

        <div className="flex shrink-0 items-center gap-2">
          <Link
            href="/billing"
            className="flex h-9 items-center gap-1.5 rounded-full bg-canvas-subtle px-3 text-ink"
          >
            <span className="material-symbols-outlined text-[16px] text-accent">bolt</span>
            <span className="text-sm font-semibold">{user?.credits ?? "—"}</span>
            <span className="text-ink-muted">+</span>
          </Link>
          <Link
            href="/settings"
            className="flex h-9 w-9 items-center justify-center rounded-full bg-ink text-xs font-semibold text-canvas-base"
          >
            {initial}
          </Link>
        </div>
      </div>
    </header>
  );
}
