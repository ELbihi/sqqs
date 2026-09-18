"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

export const TABS = [
  { href: "/studio", label: "Studio", icon: "auto_fix_high" },
  { href: "/library", label: "Library", icon: "grid_view" },
  { href: "/generations", label: "History", icon: "history" },
  { href: "/settings", label: "Account", icon: "person" },
];

export default function BottomNav() {
  const pathname = usePathname();
  return (
    <nav className="fixed inset-x-0 bottom-0 z-50 border-t border-hairline bg-canvas-base/95 backdrop-blur-xl pb-[env(safe-area-inset-bottom)] lg:hidden">
      <div className="mx-auto flex h-16 max-w-md items-center justify-around px-2">
        {TABS.map((t) => {
          const active = pathname === t.href || pathname.startsWith(t.href + "/");
          return (
            <Link
              key={t.href}
              href={t.href}
              className="flex flex-1 flex-col items-center justify-center gap-1 py-1"
            >
              <span
                className="material-symbols-outlined text-[24px]"
                style={{ color: active ? "#121212" : "#A8A69E" }}
              >
                {t.icon}
              </span>
              <span
                className="text-[11px] font-medium"
                style={{ color: active ? "#121212" : "#A8A69E" }}
              >
                {t.label}
              </span>
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
