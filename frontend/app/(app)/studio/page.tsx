"use client";

import { useEffect, useRef, useState } from "react";

import AddAssetSheet from "@/components/AddAssetSheet";
import Sheet from "@/components/Sheet";
import { api, mediaUrl } from "@/lib/api";
import {
  FASHION_POSES,
  FORMATS,
  FRAMING_ANGLES,
  POSES,
  SCENE_PRESETS,
  WARDROBE_SLOTS,
} from "@/lib/constants";
import { useAuth } from "@/lib/store";
import type { Background, Character, Garment, Generation } from "@/types";

const COST = { image: 2, video: 15 };

export default function StudioPage() {
  const refreshCredits = useAuth((s) => s.refreshCredits);

  const [characters, setCharacters] = useState<Character[]>([]);
  const [garments, setGarments] = useState<Garment[]>([]);
  const [scenes, setScenes] = useState<Background[]>([]);

  const [characterId, setCharacterId] = useState("");
  const [slots, setSlots] = useState<Record<string, string>>({});
  const [backgroundId, setBackgroundId] = useState("");
  const [outputType, setOutputType] = useState<"image" | "video">("image");
  const [framing, setFraming] = useState("full_body");
  const [format, setFormat] = useState("4:5");
  const [pose, setPose] = useState(POSES[0]);
  const [tuneOpen, setTuneOpen] = useState(false);
  const [formatOpen, setFormatOpen] = useState(false);
  const [sceneSheet, setSceneSheet] = useState(false);

  const [museOpen, setMuseOpen] = useState(false);
  const [slotOpen, setSlotOpen] = useState<string | null>(null);
  const [current, setCurrent] = useState<Generation | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const photoRef = useRef<HTMLInputElement>(null);
  const uploadRef = useRef<HTMLInputElement>(null);
  const multiRef = useRef<HTMLInputElement>(null);
  const slotFileRef = useRef<HTMLInputElement>(null);

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

  useEffect(() => {
    if (!current || current.status === "COMPLETED" || current.status === "FAILED") return;
    const id = setInterval(async () => {
      try {
        const g = await api<Generation>(`/generations/${current.id}`);
        setCurrent(g);
        if (g.status === "COMPLETED" || g.status === "FAILED") {
          clearInterval(id);
          refreshCredits();
        }
      } catch {
        clearInterval(id);
      }
    }, 1300);
    return () => clearInterval(id);
  }, [current, refreshCredits]);

  // ---------- creators -------------------------------------------------
  const createCharacter = async (file: File) => {
    const form = new FormData();
    form.append("name", file.name.replace(/\.[^.]+$/, "") || "Model");
    form.append("source", "upload");
    form.append("photo", file);
    const c = await api<Character>("/characters", { method: "POST", form });
    await load();
    setCharacterId(c.id);
    setMuseOpen(false);
  };

  const createGarment = async (file: File, slotKey: string) => {
    const slot = WARDROBE_SLOTS.find((s) => s.key === slotKey);
    const form = new FormData();
    form.append("name", file.name.replace(/\.[^.]+$/, "") || slot?.title || "Item");
    if (slot) form.append("category", slot.title);
    form.append("image", file);
    const g = await api<Garment>("/clothes", { method: "POST", form });
    await load();
    setSlots((s) => ({ ...s, [slotKey]: g.id }));
    setSlotOpen(null);
  };

  const createManyGarments = async (files: FileList) => {
    const free = WARDROBE_SLOTS.filter((s) => !slots[s.key]).map((s) => s.key);
    const next: Record<string, string> = {};
    for (let i = 0; i < Math.min(files.length, free.length); i++) {
      const file = files[i];
      const slot = WARDROBE_SLOTS.find((s) => s.key === free[i]);
      const form = new FormData();
      form.append("name", file.name.replace(/\.[^.]+$/, "") || "Item");
      if (slot) form.append("category", slot.title);
      form.append("image", file);
      const g = await api<Garment>("/clothes", { method: "POST", form });
      next[free[i]] = g.id;
    }
    await load();
    setSlots((s) => ({ ...s, ...next }));
  };

  const createScene = async (name: string, prompt: string, file?: File) => {
    const form = new FormData();
    form.append("name", name);
    form.append("source", file ? "upload" : "ai");
    if (prompt) form.append("prompt", prompt);
    if (file) form.append("image", file);
    const b = await api<Background>("/backgrounds", { method: "POST", form });
    await load();
    setBackgroundId(b.id);
  };

  // ---------- generate --------------------------------------------------
  const garmentIds = WARDROBE_SLOTS.map((s) => slots[s.key]).filter(Boolean);
  const ready = !!characterId && garmentIds.length > 0;
  const cost = COST[outputType];

  const generate = async () => {
    setBusy(true);
    setError(null);
    try {
      const gen = await api<Generation>("/generations", {
        method: "POST",
        body: {
          output_type: outputType,
          character_id: characterId || null,
          garment_ids: garmentIds,
          background_id: backgroundId || null,
          pose,
          framing,
          instruction: null,
          params: { aspect_ratio: format },
        },
      });
      setCurrent(gen);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  };

  const generating = !!current && current.status !== "COMPLETED" && current.status !== "FAILED";
  const asset = current?.assets.find((a) => a.kind === current?.output_type) || current?.assets[0];
  const activeChar = characters.find((c) => c.id === characterId);
  const hasResult = !!current;

  // ---------- shared blocks (rendered mobile inline / desktop sidebar) ---
  const resultBlock = hasResult ? (
    <div className="overflow-hidden rounded-2xl border border-hairline bg-canvas-subtle">
      {current?.status === "COMPLETED" && asset ? (
        asset.kind === "video" ? (
          <video src={mediaUrl(asset.storage_key)} controls className="w-full" />
        ) : (
          // eslint-disable-next-line @next/next/no-img-element
          <img src={mediaUrl(asset.storage_key)} alt="result" className="w-full" />
        )
      ) : current?.status === "FAILED" ? (
        <p className="p-6 text-center text-sm text-danger">{current.error || "Generation failed"}</p>
      ) : (
        <div className="flex flex-col items-center gap-3 p-10">
          <span className="material-symbols-outlined animate-pulse text-[32px] text-accent">
            auto_fix_high
          </span>
          <p className="text-sm font-medium">{current!.status.replace(/_/g, " ")}</p>
        </div>
      )}
    </div>
  ) : null;

  const generateBlock = (
    <div>
      <div className="mb-3 flex items-center justify-between text-xs">
        <span className="flex items-center gap-2 text-ink-muted">
          <span className={`h-2 w-2 rounded-full ${ready ? "bg-green-600" : "bg-accent"}`} />
          {ready ? "Ready to render" : "Awaiting model & wardrobe items"}
        </span>
        <span className="text-ink-muted">Cost: {cost} Credits</span>
      </div>
      {error && <p className="mb-3 text-sm text-danger">{error}</p>}
      <button className="btn-primary" onClick={generate} disabled={!ready || busy || generating}>
        <span className="material-symbols-outlined text-[18px]">auto_fix_high</span>
        {busy || generating ? "Rendering…" : `Generate Editorial ${outputType === "image" ? "Photo" : "Video"}`}
      </button>
    </div>
  );

  return (
    <div className="lg:grid lg:grid-cols-[minmax(0,1fr)_380px] lg:items-start lg:gap-10">
      {/* ---------------- left column ---------------- */}
      <div className="flex flex-col gap-7">
        {/* Format (top-left) + output toggle */}
        <div className="flex items-center gap-2">
          <div className="relative shrink-0">
            <button
              onClick={() => setFormatOpen((v) => !v)}
              title="Output format"
              className="flex h-12 items-center gap-1.5 rounded-full border border-hairline bg-canvas-subtle px-3 text-ink"
            >
              <span className="material-symbols-outlined text-[20px]">aspect_ratio</span>
              <span className="text-xs font-semibold">{format}</span>
              <span className={`material-symbols-outlined text-[16px] text-ink-muted transition ${formatOpen ? "rotate-180" : ""}`}>
                expand_more
              </span>
            </button>
            {formatOpen && (
              <>
                <div className="fixed inset-0 z-10" onClick={() => setFormatOpen(false)} />
                <div className="absolute left-0 top-14 z-20 w-56 overflow-hidden rounded-xl border border-hairline bg-white shadow-float">
                  {FORMATS.map((f) => (
                    <button
                      key={f.value}
                      onClick={() => { setFormat(f.value); setFormatOpen(false); }}
                      className={`flex w-full items-center justify-between px-4 py-3 text-left text-sm transition ${
                        format === f.value ? "bg-canvas-subtle font-medium" : "hover:bg-canvas-subtle"
                      }`}
                    >
                      <span>
                        {f.label}
                        <span className="block text-[11px] text-ink-muted">{f.hint}</span>
                      </span>
                      {format === f.value && (
                        <span className="material-symbols-outlined text-[18px]">check</span>
                      )}
                    </button>
                  ))}
                </div>
              </>
            )}
          </div>

          <div className="flex flex-1 rounded-full border border-hairline bg-canvas-subtle p-1 sm:max-w-sm">
          {(["image", "video"] as const).map((t) => (
            <button
              key={t}
              onClick={() => setOutputType(t)}
              className={`flex h-10 flex-1 items-center justify-center gap-2 rounded-full text-sm font-medium transition ${
                outputType === t ? "bg-white shadow-hair text-ink" : "text-ink-muted"
              }`}
            >
              {t === "image" ? "Image" : "Video"}
              {t === "video" && (
                <span className="rounded-full bg-canvas-subtle px-1.5 py-0.5 text-[10px] text-ink-muted">
                  Beta
                </span>
              )}
            </button>
            ))}
          </div>
        </div>

        {resultBlock && <div className="lg:hidden">{resultBlock}</div>}

        {/* 01 Model or Muse */}
        <Section num="01" title="Model or Muse" meta="Required">
          {activeChar ? (
            <div className="panel flex items-center gap-4">
              <span className="h-16 w-16 shrink-0 overflow-hidden rounded-xl bg-white">
                {activeChar.original_photo_key ? (
                  // eslint-disable-next-line @next/next/no-img-element
                  <img src={mediaUrl(activeChar.original_photo_key)} alt="" className="h-full w-full object-cover" />
                ) : (
                  <span className="flex h-full items-center justify-center text-ink-muted">
                    <span className="material-symbols-outlined">person</span>
                  </span>
                )}
              </span>
              <div className="min-w-0 flex-1">
                <p className="truncate font-medium">{activeChar.name}</p>
                <p className="text-xs text-ink-muted">Casting selected</p>
              </div>
              <button onClick={() => setMuseOpen(true)} className="chip">Change</button>
            </div>
          ) : (
            <div className="panel flex flex-col items-center py-8 text-center sm:py-10">
              <span className="mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-white shadow-hair">
                <span className="material-symbols-outlined text-[28px] text-ink">add_a_photo</span>
              </span>
              <p className="text-lg font-medium">Add model or person</p>
              <p className="mt-1 max-w-[320px] text-sm text-ink-muted">
                Take a photo, upload casting shots, or choose from saved agency talent.
              </p>
              <div className="mt-5 flex flex-wrap justify-center gap-2.5">
                <button className="btn-ghost" onClick={() => photoRef.current?.click()}>
                  <span className="material-symbols-outlined text-[18px]">photo_camera</span> Take Photo
                </button>
                <button className="btn-ghost" onClick={() => uploadRef.current?.click()}>
                  <span className="material-symbols-outlined text-[18px]">upload_file</span> Upload File
                </button>
                <button className="btn-ghost" onClick={() => setMuseOpen(true)}>
                  <span className="material-symbols-outlined text-[18px]">group</span> Cast Muse
                </button>
              </div>
              <p className="mt-5 flex items-center gap-2 text-xs text-ink-muted">
                <span className="material-symbols-outlined text-[16px] text-accent">auto_awesome</span>
                Pro Tip: Multi-angle views preserve couture draping
              </p>
            </div>
          )}
          <input ref={photoRef} type="file" accept="image/*" capture="user" className="hidden"
            onChange={(e) => e.target.files?.[0] && createCharacter(e.target.files[0])} />
          <input ref={uploadRef} type="file" accept="image/*" className="hidden"
            onChange={(e) => e.target.files?.[0] && createCharacter(e.target.files[0])} />
        </Section>

        {/* 02 Wardrobe & Pieces — images only, no names */}
        <Section num="02" title="Wardrobe & Pieces" meta={`${garmentIds.length}/6 items`}>
          <div className="panel">
            <p className="mb-3 text-xs text-ink-muted">
              Direct apparel flat-lays or curated archive:{" "}
              <a href="/library" className="font-medium text-accent">Lookbook ›</a>
            </p>
            <div className="grid grid-cols-3 gap-2.5 sm:grid-cols-6 lg:grid-cols-3">
              {WARDROBE_SLOTS.map((s) => {
                const g = garments.find((x) => x.id === slots[s.key]);
                return (
                  <button
                    key={s.key}
                    onClick={() => setSlotOpen(s.key)}
                    className={`group relative aspect-square overflow-hidden rounded-xl border bg-white transition ${
                      g ? "border-ink" : "border-hairline"
                    }`}
                  >
                    {g?.original_image_key ? (
                      <>
                        {/* eslint-disable-next-line @next/next/no-img-element */}
                        <img src={mediaUrl(g.original_image_key)} alt="" className="h-full w-full object-cover" />
                        <span className="absolute right-1.5 top-1.5 flex h-5 w-5 items-center justify-center rounded-full bg-ink text-canvas-base">
                          <span className="material-symbols-outlined text-[13px]">check</span>
                        </span>
                      </>
                    ) : (
                      <span className="flex h-full flex-col items-center justify-center gap-1.5 px-1 text-center">
                        <span className="flex h-9 w-9 items-center justify-center rounded-full bg-canvas-subtle">
                          <span className="material-symbols-outlined text-[18px] text-ink-secondary">{s.icon}</span>
                        </span>
                        <span className="text-[10px] font-medium leading-tight text-ink-secondary">{s.title}</span>
                        <span className="text-[9px] text-ink-muted">{s.sub}</span>
                      </span>
                    )}
                  </button>
                );
              })}
            </div>
            <div className="mt-4 flex justify-end">
              <button
                onClick={() => multiRef.current?.click()}
                className="flex h-11 items-center gap-2 rounded-full bg-ink px-5 text-sm font-semibold text-canvas-base active:scale-[0.98]"
              >
                <span className="material-symbols-outlined text-[18px]">cloud_upload</span> + Upload Item(s)
              </button>
            </div>
            <input ref={multiRef} type="file" accept="image/*" multiple className="hidden"
              onChange={(e) => e.target.files?.length && createManyGarments(e.target.files)} />
          </div>
        </Section>

        {/* 03 Atmosphere & Scene */}
        <Section num="03" title="Atmosphere & Scene" meta="Editorial presets">
          <div className="no-scrollbar -mx-5 flex gap-3 overflow-x-auto px-5 pb-1 sm:mx-0 sm:grid sm:grid-cols-3 sm:overflow-visible sm:px-0 lg:grid-cols-2">
            {scenes.map((s) => (
              <button
                key={s.id}
                onClick={() => setBackgroundId(backgroundId === s.id ? "" : s.id)}
                className={`w-40 shrink-0 overflow-hidden rounded-xl border bg-white text-left sm:w-auto ${
                  backgroundId === s.id ? "border-ink" : "border-hairline"
                }`}
              >
                <span className="relative block aspect-[4/3] bg-canvas-subtle">
                  {s.image_key ? (
                    // eslint-disable-next-line @next/next/no-img-element
                    <img src={mediaUrl(s.image_key)} alt="" className="h-full w-full object-cover" />
                  ) : (
                    <span className="flex h-full items-center justify-center text-ink-muted">
                      <span className="material-symbols-outlined">image</span>
                    </span>
                  )}
                  {backgroundId === s.id && (
                    <span className="absolute left-2 top-2 rounded-full bg-ink px-2 py-0.5 text-[10px] font-semibold text-canvas-base">
                      Active
                    </span>
                  )}
                </span>
                <span className="block p-2.5">
                  <span className="block truncate text-sm font-medium">{s.name}</span>
                  <span className="block truncate text-xs text-ink-muted">{s.prompt || s.source}</span>
                </span>
              </button>
            ))}

            <button
              onClick={() => setSceneSheet(true)}
              className="flex w-40 shrink-0 flex-col items-center justify-center gap-1.5 rounded-xl border border-dashed border-hairline-strong bg-canvas-subtle p-4 text-center sm:w-auto sm:aspect-[4/3]"
            >
              <span className="material-symbols-outlined text-[22px] text-ink-secondary">add_photo_alternate</span>
              <span className="text-sm font-medium">+ Custom Scene</span>
              <span className="text-[11px] text-ink-muted">Upload image or moodboard</span>
            </button>
          </div>

          {scenes.length === 0 && (
            <div className="mt-3 flex flex-wrap gap-2">
              {SCENE_PRESETS.map((p) => (
                <button key={p.name} className="chip" onClick={() => createScene(p.name, p.prompt)}>
                  + {p.name}
                </button>
              ))}
            </div>
          )}
        </Section>

        {/* 04 Look & Framing */}
        <Section num="04" title="Look & Framing">
          <div className="panel">
            <button onClick={() => setTuneOpen((v) => !v)} className="flex w-full items-start justify-between gap-3 text-left">
              <span className="min-w-0">
                <span className="flex flex-wrap items-center gap-2">
                  <span className="text-sm font-medium">Composition Parameters</span>
                  <span className="chip chip-active h-7">
                    {FRAMING_ANGLES.find((f) => f.value === framing)?.label}
                  </span>
                </span>
                <span className="mt-2 block">
                  <span className="chip h-7">{pose}</span>
                </span>
                <span className="mt-2 block text-xs text-ink-muted">
                  Camera height: Eye level • Aspect ratio: {format}
                </span>
              </span>
              <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-white">
                <span className={`material-symbols-outlined text-[20px] transition ${tuneOpen ? "rotate-180" : ""}`}>
                  expand_more
                </span>
              </span>
            </button>

            {tuneOpen && (
              <div className="mt-4 flex flex-col gap-5 border-t border-hairline pt-4">
                <div>
                  <p className="label mb-2">Framing Angle</p>
                  <div className="flex flex-wrap gap-2">
                    {FRAMING_ANGLES.map((f) => (
                      <button
                        key={f.value}
                        onClick={() => setFraming(f.value)}
                        className={`chip ${framing === f.value ? "chip-active" : ""}`}
                      >
                        {f.label}
                      </button>
                    ))}
                  </div>
                </div>

                <div>
                  <p className="label mb-2">Poses &amp; Motion</p>
                  <div className="flex flex-wrap gap-2">
                    {POSES.map((p) => (
                      <button
                        key={p}
                        onClick={() => setPose(p)}
                        className={`chip ${pose === p ? "chip-active" : ""}`}
                      >
                        {p}
                      </button>
                    ))}
                  </div>
                </div>

                <div>
                  <p className="label mb-2">Fashion Poses</p>
                  <div className="flex flex-wrap gap-2">
                    {FASHION_POSES.map((p) => (
                      <button
                        key={p}
                        onClick={() => setPose(p)}
                        className={`chip ${pose === p ? "chip-active" : ""}`}
                      >
                        {p}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        </Section>

        <div className="lg:hidden">{generateBlock}</div>
      </div>

      {/* ---------------- right column (desktop) ---------------- */}
      <aside className="hidden lg:sticky lg:top-28 lg:flex lg:flex-col lg:gap-5">
        {resultBlock || (
          <div className="flex aspect-[4/5] flex-col items-center justify-center rounded-2xl border border-dashed border-hairline-strong bg-canvas-subtle text-center">
            <span className="material-symbols-outlined text-[34px] text-ink-muted">image</span>
            <p className="mt-2 text-sm font-medium">Your look appears here</p>
            <p className="mt-1 max-w-[220px] text-xs text-ink-muted">
              Pick a model, wardrobe pieces and a scene, then render.
            </p>
          </div>
        )}
        {generateBlock}
      </aside>

      {sceneSheet && (
        <AddAssetSheet
          kind="scene"
          open
          onClose={() => setSceneSheet(false)}
          onCreated={async (created) => {
            await load();
            setBackgroundId(created.id);
            refreshCredits();
          }}
        />
      )}

      {/* Cast Muse sheet */}
      <Sheet open={museOpen} onClose={() => setMuseOpen(false)} title="Cast a muse">
        {characters.length === 0 ? (
          <p className="pb-4 text-sm text-ink-muted">No saved talent yet — take or upload a photo.</p>
        ) : (
          <div className="grid max-h-[50vh] grid-cols-3 gap-3 overflow-y-auto pb-2 sm:grid-cols-5">
            {characters.map((c) => (
              <button
                key={c.id}
                onClick={() => { setCharacterId(c.id); setMuseOpen(false); }}
                className={`overflow-hidden rounded-xl border ${characterId === c.id ? "border-ink" : "border-hairline"}`}
              >
                <span className="block aspect-[3/4] bg-canvas-subtle">
                  {c.original_photo_key ? (
                    // eslint-disable-next-line @next/next/no-img-element
                    <img src={mediaUrl(c.original_photo_key)} alt="" className="h-full w-full object-cover" />
                  ) : (
                    <span className="flex h-full items-center justify-center text-ink-muted">
                      <span className="material-symbols-outlined">person</span>
                    </span>
                  )}
                </span>
              </button>
            ))}
          </div>
        )}
        <button className="btn-ghost mt-3 w-full" onClick={() => uploadRef.current?.click()}>
          <span className="material-symbols-outlined text-[18px]">upload_file</span> Upload new
        </button>
      </Sheet>

      {/* Wardrobe slot sheet — images only */}
      <Sheet
        open={!!slotOpen}
        onClose={() => setSlotOpen(null)}
        title={WARDROBE_SLOTS.find((s) => s.key === slotOpen)?.title || "Item"}
      >
        <div className="grid max-h-[46vh] grid-cols-3 gap-3 overflow-y-auto pb-2 sm:grid-cols-5">
          {garments.map((g) => (
            <button
              key={g.id}
              onClick={() => {
                setSlots((s) => ({ ...s, [slotOpen!]: g.id }));
                setSlotOpen(null);
              }}
              className="aspect-square overflow-hidden rounded-xl border border-hairline bg-canvas-subtle"
            >
              {g.original_image_key ? (
                // eslint-disable-next-line @next/next/no-img-element
                <img src={mediaUrl(g.original_image_key)} alt="" className="h-full w-full object-cover" />
              ) : (
                <span className="flex h-full items-center justify-center text-ink-muted">
                  <span className="material-symbols-outlined">checkroom</span>
                </span>
              )}
            </button>
          ))}
        </div>
        <div className="mt-3 flex gap-2">
          <button className="btn-ghost flex-1" onClick={() => slotFileRef.current?.click()}>
            <span className="material-symbols-outlined text-[18px]">upload_file</span> Upload
          </button>
          {slotOpen && slots[slotOpen] && (
            <button
              className="btn-ghost flex-1 text-danger"
              onClick={() => {
                setSlots((s) => {
                  const n = { ...s };
                  delete n[slotOpen!];
                  return n;
                });
                setSlotOpen(null);
              }}
            >
              Clear slot
            </button>
          )}
        </div>
        <input ref={slotFileRef} type="file" accept="image/*" className="hidden"
          onChange={(e) => {
            const f = e.target.files?.[0];
            if (f && slotOpen) createGarment(f, slotOpen);
          }} />
      </Sheet>
    </div>
  );
}

function Section({
  num, title, meta, children,
}: { num: string; title: string; meta?: string; children: React.ReactNode }) {
  return (
    <section>
      <div className="mb-3 flex items-baseline justify-between">
        <div className="flex items-baseline gap-2">
          <span className="step-num">{num}</span>
          <h2 className="text-[17px] font-medium tracking-tight">{title}</h2>
        </div>
        {meta && <span className="text-xs text-ink-muted">{meta}</span>}
      </div>
      {children}
    </section>
  );
}
