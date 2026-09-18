"use client";

import { useAuth } from "@/lib/store";

export default function ProfilePage() {
  const { user, logout } = useAuth();
  const initial = (user?.full_name || user?.email || "?").charAt(0).toUpperCase();

  return (
    <div className="flex flex-col gap-5 lg:max-w-3xl">
      <h1 className="text-2xl font-bold tracking-tight">Profile</h1>

      <div className="flex items-center gap-4 rounded-2xl border border-hairline bg-white p-4">
        <span className="flex h-14 w-14 items-center justify-center rounded-full bg-ink text-lg font-semibold text-white">
          {initial}
        </span>
        <div className="min-w-0">
          <p className="truncate font-semibold">{user?.full_name || "—"}</p>
          <p className="truncate text-sm text-ink-muted">{user?.email}</p>
        </div>
      </div>

      <div className="divide-y divide-hairline overflow-hidden rounded-2xl border border-hairline bg-white">
        <Row label="Credits" value={String(user?.credits ?? 0)} />
        <Row label="Plan" value="Free" />
      </div>

      <button onClick={logout} className="btn-ghost text-danger">
        <span className="material-symbols-outlined text-[18px]">logout</span> Log out
      </button>
    </div>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between px-4 py-3 text-sm">
      <span className="text-ink-muted">{label}</span>
      <span className="font-medium">{value}</span>
    </div>
  );
}
