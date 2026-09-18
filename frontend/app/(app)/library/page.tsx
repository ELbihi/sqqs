"use client";

import { useEffect, useState } from "react";

import AddAssetSheet from "@/components/AddAssetSheet";
import { api, mediaUrl } from "@/lib/api";
import type { Background, Character, Garment } from "@/types";

type Tab = "models" | "clothes" | "scenes";

export default function LibraryPage() {
  const [tab, setTab] = useState<Tab>("models");
  const [characters, setCharacters] = useState<Character[]>([]);
  const [garments, setGarments] = useState<Garment[]>([]);
  const [scenes, setScenes] = useState<Background[]>([]);
  const [sheet, setSheet] = useState<null | "person" | "clothes" | "scene">(null);

  const load = () =>
    Promise.all([
      api<Character[]>("/characters"),
      api<Garment[]>("/clothes"),
      api<Background[]>("/backgrounds"),
    ]).then(([c, g, b]) => {
      setCharacters(c);
      setGarments(g);
      setScenes(b);
    });

  useEffect(() => {
    load().catch(() => {});
  }, []);

  const del = async (endpoint: string, id: string) => {
    await api(`${endpoint}/${id}`, { method: "DELETE" });
    load();
  };

  const tabs: { key: Tab; label: string; count: number }[] = [
    { key: "models", label: "Models", count: characters.length },
    { key: "clothes", label: "Clothes", count: garments.length },
    { key: "scenes", label: "Scenes", count: scenes.length },
  ];

  const addKind = tab === "models" ? "person" : tab === "clothes" ? "clothes" : "scene";

  return (
    <div className="flex flex-col gap-5">
      <h1 className="text-2xl font-bold tracking-tight">Library</h1>

      <div className="flex rounded-full bg-canvas-subtle p-1 sm:max-w-md">
        {tabs.map((t) => (
          <button
            key={t.key}
            onClick={() => setTab(t.key)}
            className={`flex-1 rounded-full py-2 text-sm font-medium ${tab === t.key ? "bg-white shadow-hair" : "text-ink-muted"}`}
          >
            {t.label} <span className="text-ink-muted">{t.count}</span>
          </button>
        ))}
      </div>

      <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-5">
        <button
          onClick={() => setSheet(addKind)}
          className="flex aspect-[3/4] flex-col items-center justify-center gap-1.5 rounded-2xl border border-dashed border-hairline bg-white text-ink-secondary"
        >
          <span className="material-symbols-outlined text-[26px]">add</span>
          <span className="text-sm font-medium">Add {tab === "models" ? "model" : tab === "clothes" ? "clothing" : "scene"}</span>
        </button>

        {tab === "models" &&
          characters.map((c) => (
            <AssetCard key={c.id} title={c.name} sub={c.source} img={c.original_photo_key ? mediaUrl(c.original_photo_key) : null} onDelete={() => del("/characters", c.id)} />
          ))}
        {tab === "clothes" &&
          garments.map((g) => (
            <AssetCard key={g.id} title={g.name} sub={[g.brand, g.category].filter(Boolean).join(" · ") || "Clothing"} img={g.original_image_key ? mediaUrl(g.original_image_key) : null} onDelete={() => del("/clothes", g.id)} />
          ))}
        {tab === "scenes" &&
          scenes.map((s) => (
            <AssetCard key={s.id} title={s.name} sub={s.prompt || s.source} img={s.image_key ? mediaUrl(s.image_key) : null} onDelete={() => del("/backgrounds", s.id)} />
          ))}
      </div>

      {sheet && (
        <AddAssetSheet
          kind={sheet}
          open
          onClose={() => setSheet(null)}
          onCreated={() => load()}
        />
      )}
    </div>
  );
}

function AssetCard({ title, sub, img, onDelete }: { title: string; sub: string; img: string | null; onDelete: () => void }) {
  return (
    <div className="overflow-hidden rounded-2xl border border-hairline bg-white">
      <div className="relative aspect-[3/4] bg-neutral-100">
        {img ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img src={img} alt={title} className="h-full w-full object-cover" />
        ) : (
          <span className="flex h-full items-center justify-center text-ink-muted">
            <span className="material-symbols-outlined">image</span>
          </span>
        )}
        <button
          onClick={onDelete}
          className="absolute right-2 top-2 flex h-7 w-7 items-center justify-center rounded-full bg-white/90 text-ink-muted shadow-hair"
        >
          <span className="material-symbols-outlined text-[16px]">delete</span>
        </button>
      </div>
      <div className="p-2.5">
        <p className="truncate text-sm font-medium">{title}</p>
        <p className="truncate text-[11px] text-ink-muted">{sub}</p>
      </div>
    </div>
  );
}
