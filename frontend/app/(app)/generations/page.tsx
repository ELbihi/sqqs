"use client";

import { useEffect, useState } from "react";

import { api, mediaUrl } from "@/lib/api";
import type { Generation } from "@/types";

export default function GalleryPage() {
  const [items, setItems] = useState<Generation[]>([]);
  const [filter, setFilter] = useState<"all" | "image" | "video">("all");

  useEffect(() => {
    const load = () => api<Generation[]>("/generations").then(setItems).catch(() => {});
    load();
    const id = setInterval(load, 3500);
    return () => clearInterval(id);
  }, []);

  const shown = items.filter((g) => filter === "all" || g.output_type === filter);

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-baseline justify-between">
        <h1 className="text-2xl font-bold tracking-tight">Gallery</h1>
        <span className="text-xs text-ink-muted">{items.length} creations</span>
      </div>

      <div className="flex gap-2">
        {(["all", "image", "video"] as const).map((f) => (
          <button key={f} onClick={() => setFilter(f)} className={`chip ${filter === f ? "chip-active" : ""}`}>
            {f === "all" ? "All" : f === "image" ? "Photos" : "Videos"}
          </button>
        ))}
      </div>

      {shown.length === 0 ? (
        <p className="mt-8 text-center text-sm text-ink-muted">Nothing yet — create your first look.</p>
      ) : (
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-5">
          {shown.map((g) => {
            const a = g.assets[0];
            const done = g.status === "COMPLETED";
            return (
              <div key={g.id} className="overflow-hidden rounded-2xl border border-hairline bg-white">
                <div className="relative aspect-[3/4] bg-neutral-100">
                  {done && a ? (
                    a.kind === "video" ? (
                      <video src={mediaUrl(a.storage_key)} muted className="h-full w-full object-cover" />
                    ) : (
                      // eslint-disable-next-line @next/next/no-img-element
                      <img src={mediaUrl(a.storage_key)} alt="" className="h-full w-full object-cover" />
                    )
                  ) : (
                    <span className="flex h-full items-center justify-center text-center text-[11px] text-ink-muted">
                      {g.status === "FAILED" ? "Failed" : g.status.replace(/_/g, " ")}
                    </span>
                  )}
                  <span className="absolute left-2 top-2 chip bg-white/90 uppercase">{g.output_type}</span>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
