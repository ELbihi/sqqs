"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { useAuth } from "@/lib/store";

const NAV = [
  { href: "/studio", label: "AI Studio", icon: "✦" },
  { href: "/dashboard", label: "Dashboard", icon: "▦" },
  { href: "/characters", label: "Characters", icon: "☺" },
  { href: "/wardrobe", label: "Wardrobe", icon: "☂" },
  { href: "/backgrounds", label: "Scenes", icon: "◱" },
  { href: "/generations", label: "Generations", icon: "✧" },
  { href: "/billing", label: "Credits & Billing", icon: "◈" },
  { href: "/settings", label: "Settings", icon: "⚙" },
];

export default function Sidebar() {
  const pathname = usePathname();
  const { user, logout } = useAuth();

  return (
    <aside className="flex w-60 shrink-0 flex-col border-r border-studio-border bg-studio-panel/60 p-4">
      <Link href="/studio" className="mb-6 px-2 text-lg font-bold">
        AI Virtual Studio
      </Link>
      <nav className="flex flex-1 flex-col gap-1">
        {NAV.map((item) => {
          const active = pathname === item.href || pathname.startsWith(item.href + "/");
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition ${
                active
                  ? "bg-studio-accent/20 text-white"
                  : "text-white/60 hover:bg-white/5 hover:text-white"
              }`}
            >
              <span className="w-4 text-center opacity-80">{item.icon}</span>
              {item.label}
            </Link>
          );
        })}
      </nav>
      <div className="mt-4 rounded-lg border border-studio-border p-3 text-sm">
        <div className="flex items-center justify-between">
          <span className="text-white/50">Credits</span>
          <span className="font-semibold text-studio-accent2">{user?.credits ?? "—"}</span>
        </div>
        <div className="mt-2 truncate text-xs text-white/40">{user?.email}</div>
        <button onClick={logout} className="mt-2 text-xs text-white/40 hover:text-white">
          Log out
        </button>
      </div>
    </aside>
  );
}
