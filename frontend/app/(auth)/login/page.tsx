"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import AuthHero from "@/components/AuthHero";
import { getToken } from "@/lib/api";
import { useAuth } from "@/lib/store";

export default function LoginPage() {
  const router = useRouter();
  const login = useAuth((s) => s.login);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (getToken()) router.replace("/studio");
  }, [router]);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      await login(email, password);
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
        <input className="input" type="email" placeholder="Work or personal email" value={email} onChange={(e) => setEmail(e.target.value)} required />
        <input className="input" type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} required />
        {error && <p className="text-sm text-danger">{error}</p>}
        <button className="btn-primary" disabled={busy}>{busy ? "…" : "Log in"}</button>
      </form>
      <p className="text-center text-sm text-ink-muted">
        New here? <Link href="/register" className="font-medium text-accent">Create an account</Link>
      </p>
      <p className="text-center text-[11px] text-ink-muted">Google & Apple sign-in coming soon.</p>
    </main>
  );
}
