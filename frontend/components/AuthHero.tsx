export default function AuthHero() {
  return (
    <div className="w-full">
      <div className="mb-4 flex items-center gap-2">
        <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-ink text-white">
          <span className="material-symbols-outlined text-[18px]">apparel</span>
        </span>
        <span className="text-base font-semibold tracking-tight">Virtual Studio</span>
      </div>

      {/* Before / after hero */}
      <div className="relative aspect-[4/3] w-full overflow-hidden rounded-2xl border border-hairline">
        <div className="absolute inset-0 grid grid-cols-2">
          <div className="flex items-end justify-center bg-neutral-200 pb-3">
            <span className="chip bg-white/90">Phone flatlay</span>
          </div>
          <div className="flex items-end justify-center bg-gradient-to-br from-neutral-300 to-neutral-400 pb-3">
            <span className="chip bg-white/90">Studio render</span>
          </div>
        </div>
        <div className="absolute inset-y-0 left-1/2 w-0.5 -translate-x-1/2 bg-white/80" />
        <div className="absolute left-1/2 top-1/2 flex h-9 w-9 -translate-x-1/2 -translate-y-1/2 items-center justify-center rounded-full bg-ink text-white shadow-float">
          <span className="material-symbols-outlined text-[18px]">drag_indicator</span>
        </div>
      </div>

      <h1 className="mt-6 text-3xl font-bold leading-tight tracking-tight">
        Professional fashion photos in seconds.
      </h1>
      <p className="mt-2 text-sm text-ink-secondary">
        Upload clothes, pick a model, set a scene. No photographer or studio needed.
      </p>
      <div className="mt-3 flex flex-wrap gap-2">
        <span className="chip"><span className="material-symbols-outlined text-[14px]">bolt</span> ~30s</span>
        <span className="chip"><span className="material-symbols-outlined text-[14px]">checkroom</span> Any garment</span>
        <span className="chip"><span className="material-symbols-outlined text-[14px]">auto_awesome</span> Photorealistic</span>
      </div>
    </div>
  );
}
