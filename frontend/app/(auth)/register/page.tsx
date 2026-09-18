"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";

import AuthHero from "@/components/AuthHero";
import { useAuth } from "@/lib/store";

export default function RegisterPage() {
  const router = useRouter();
  const register = useAuth((s) => s.register);
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      await register(email, password, fullName || undefined);
      router.push("/studio");
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <main className="mx-auto flex min-h-screen max-w-[440px] flex-col justify-center gap-6 px-5 py-10">
      <AuthHero />
      <form onSubmit={submit} className="flex flex-col gap-3">
        <input className="input" placeholder="Full name" value={fullName} onChange={(e) => setFullName(e.target.value)} />
        <input className="input" type="email" placeholder="Work or personal email" value={email} onChange={(e) => setEmail(e.target.value)} required />
        <input className="input" type="password" placeholder="Password (min 6)" value={password} onChange={(e) => setPassword(e.target.value)} required minLength={6} />
        {error && <p className="text-sm text-danger">{error}</p>}
        <button className="btn-primary" disabled={busy}>{busy ? "…" : "Create account"}</button>
        <p className="text-center text-[11px] text-ink-muted">10 free studio credits on signup · No credit card required</p>
      </form>
      <p className="text-center text-sm text-ink-muted">
        Already have an account? <Link href="/login" className="font-medium text-accent">Log in</Link>
      </p>
    </main>
  );
}
