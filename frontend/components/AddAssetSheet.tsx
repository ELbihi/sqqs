"use client";

import { useRef, useState } from "react";

import Sheet from "@/components/Sheet";
import { api } from "@/lib/api";

type Kind = "person" | "clothes" | "scene";

const CONFIG: Record<Kind, { title: string; endpoint: string; fileField: string }> = {
  person: { title: "Add a person", endpoint: "/characters", fileField: "photo" },
  clothes: { title: "Add clothing", endpoint: "/clothes", fileField: "image" },
  scene: { title: "Add a scene", endpoint: "/backgrounds", fileField: "image" },
};

export default function AddAssetSheet({
  kind,
  open,
  onClose,
  onCreated,
}: {
  kind: Kind;
  open: boolean;
  onClose: () => void;
  onCreated: (created: { id: string }) => void;
}) {
  const cfg = CONFIG[kind];
  const [mode, setMode] = useState<"upload" | "generate">("upload");
  const [name, setName] = useState("");
  const [category, setCategory] = useState("");
  const [prompt, setPrompt] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileRef = useRef<HTMLInputElement>(null);

  const reset = () => {
    setName(""); setCategory(""); setPrompt(""); setFile(null); setPreview(null); setError(null);
    if (fileRef.current) fileRef.current.value = "";
  };

  const close = () => { reset(); setMode("upload"); onClose(); };

  const pick = (f: File | null) => {
    setFile(f);
    setPreview(f ? URL.createObjectURL(f) : null);
    if (f && !name) setName(f.name.replace(/\.[^.]+$/, ""));
  };

  const submitUpload = async () => {
    setError(null);
    if (!name.trim()) return setError("Give it a name.");
    if (!file) return setError("Add a photo.");
    setBusy(true);
    try {
      const form = new FormData();
      form.append("name", name.trim());
      if (kind === "person") form.append("source", "upload");
      if (kind === "clothes" && category) form.append("category", category);
      if (kind === "scene") {
        form.append("source", "upload");
        if (prompt) form.append("prompt", prompt);
      }
      form.append(cfg.fileField, file);
      const created = await api<{ id: string }>(cfg.endpoint, { method: "POST", form });
      onCreated(created);
      close();
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  };

  const submitGenerate = async () => {
    setError(null);
    if (!prompt.trim()) return setError("Describe the scene you want.");
    setBusy(true);
    try {
      const created = await api<{ id: string }>("/backgrounds/generate", {
        method: "POST",
        body: {
          name: name.trim() || prompt.trim().slice(0, 40),
          prompt: prompt.trim(),
          aspect_ratio: "4:3",
        },
      });
      onCreated(created);
      close();
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  };

  const isScene = kind === "scene";

  return (
    <Sheet open={open} onClose={close} title={cfg.title}>
      {isScene && (
        <div className="mb-4 flex rounded-full border border-hairline bg-canvas-subtle p-1">
          {([
            { k: "upload", label: "Upload", icon: "upload_file" },
            { k: "generate", label: "Generate", icon: "auto_awesome" },
          ] as const).map((m) => (
            <button
              key={m.k}
              onClick={() => { setMode(m.k); setError(null); }}
              className={`flex h-10 flex-1 items-center justify-center gap-2 rounded-full text-sm font-medium transition ${
                mode === m.k ? "bg-white shadow-hair text-ink" : "text-ink-muted"
              }`}
            >
              <span className="material-symbols-outlined text-[18px]">{m.icon}</span>
              {m.label}
            </button>
          ))}
        </div>
      )}

      <div className="flex flex-col gap-4">
        {(!isScene || mode === "upload") && (
          <>
            <button
              onClick={() => fileRef.current?.click()}
              className="flex aspect-[4/3] w-full items-center justify-center overflow-hidden rounded-xl border border-dashed border-hairline-strong bg-canvas-subtle"
            >
              {preview ? (
                // eslint-disable-next-line @next/next/no-img-element
                <img src={preview} alt="" className="h-full w-full object-cover" />
              ) : (
                <span className="flex flex-col items-center gap-1 text-ink-muted">
                  <span className="material-symbols-outlined text-[28px]">add_a_photo</span>
                  <span className="text-xs">Take photo or upload</span>
                </span>
              )}
            </button>
            <input
              ref={fileRef}
              type="file"
              accept="image/*"
              className="hidden"
              onChange={(e) => pick(e.target.files?.[0] ?? null)}
            />
          </>
        )}

        {isScene && mode === "generate" && (
          <div>
            <label className="label mb-1 block">Describe the scene</label>
            <textarea
              className="input h-24 resize-none py-2.5"
              placeholder="e.g. sunlit Moroccan riad courtyard, zellige tiles, dappled light"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
            />
            <p className="mt-2 text-xs text-ink-muted">
              The AI renders an empty environment — no people. Costs 2 credits.
            </p>
          </div>
        )}

        <div>
          <label className="label mb-1 block">
            Name {isScene && mode === "generate" && <span className="text-ink-muted">(optional)</span>}
          </label>
          <input
            className="input"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder={isScene ? "Travertine Loft" : "e.g. Elena"}
          />
        </div>

        {kind === "clothes" && (
          <div>
            <label className="label mb-1 block">Type (optional)</label>
            <input className="input" value={category} onChange={(e) => setCategory(e.target.value)} placeholder="jacket, shoes…" />
          </div>
        )}

        {isScene && mode === "upload" && (
          <div>
            <label className="label mb-1 block">Description (optional)</label>
            <input className="input" value={prompt} onChange={(e) => setPrompt(e.target.value)} placeholder="warm sunbeam & oak" />
          </div>
        )}

        {error && <p className="text-sm text-danger">{error}</p>}

        <button
          className="btn-primary"
          onClick={isScene && mode === "generate" ? submitGenerate : submitUpload}
          disabled={busy}
        >
          {busy
            ? isScene && mode === "generate"
              ? "Generating…"
              : "Adding…"
            : isScene && mode === "generate"
              ? "Generate scene · 2 credits"
              : "Add"}
        </button>
      </div>
    </Sheet>
  );
}
