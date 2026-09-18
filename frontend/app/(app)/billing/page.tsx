"use client";

import { useEffect, useState } from "react";

import { api } from "@/lib/api";
import { useAuth } from "@/lib/store";

interface Plan { id: string; name: string; monthly_credits: number; price_eur: number }
interface LedgerRow { amount: number; reason: string }

export default function BillingPage() {
  const { user, refreshCredits } = useAuth();
  const [plans, setPlans] = useState<Plan[]>([]);
  const [ledger, setLedger] = useState<LedgerRow[]>([]);

  const loadLedger = () => api<LedgerRow[]>("/billing/ledger").then(setLedger).catch(() => {});
  useEffect(() => {
    api<{ plans: Plan[] }>("/billing/plans").then((d) => setPlans(d.plans)).catch(() => {});
    loadLedger();
  }, []);

  const topUp = async (amount: number) => {
    await api("/billing/credits/purchase", { method: "POST", body: { amount } });
    await refreshCredits();
    loadLedger();
  };

  return (
    <div className="flex flex-col gap-5 lg:max-w-3xl">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Credits</h1>
        <p className="mt-1 text-sm text-ink-secondary">
          Balance <span className="font-semibold text-ink">{user?.credits ?? 0}</span> credits.
        </p>
      </div>

      <div className="rounded-2xl border border-hairline bg-ink p-5 text-white">
        <p className="text-xs uppercase tracking-widest text-white/50">Available</p>
        <p className="mt-1 text-4xl font-bold">{user?.credits ?? 0}</p>
        <p className="mt-1 text-xs text-white/50">Each image costs 2 credits.</p>
      </div>

      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        {plans.map((p) => (
          <div key={p.id} className="flex flex-col rounded-2xl border border-hairline bg-white p-4">
            <p className="text-sm font-semibold">{p.name}</p>
            <p className="mt-1 text-2xl font-bold">
              {p.price_eur === 0 ? "Free" : `€${p.price_eur}`}
              {p.price_eur > 0 && <span className="text-xs font-normal text-ink-muted">/mo</span>}
            </p>
            <p className="mt-0.5 text-xs text-ink-muted">{p.monthly_credits} credits / mo</p>
            <button onClick={() => topUp(p.monthly_credits)} className="btn-ghost mt-3 text-xs">
              Add {p.monthly_credits} (dev)
            </button>
          </div>
        ))}
      </div>

      <div>
        <h2 className="mb-2 text-sm font-semibold">History</h2>
        <div className="divide-y divide-hairline overflow-hidden rounded-2xl border border-hairline bg-white">
          {ledger.length === 0 && <p className="p-4 text-sm text-ink-muted">No activity yet.</p>}
          {ledger.map((r, i) => (
            <div key={i} className="flex items-center justify-between px-4 py-2.5 text-sm">
              <span className="capitalize text-ink-secondary">{r.reason}</span>
              <span className={r.amount >= 0 ? "font-medium text-accent" : "text-danger"}>
                {r.amount >= 0 ? "+" : ""}{r.amount}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
