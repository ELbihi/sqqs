"use client";

import { useEffect } from "react";

export default function Sheet({
  open,
  onClose,
  title,
  children,
}: {
  open: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
}) {
  useEffect(() => {
    if (open) document.body.style.overflow = "hidden";
    return () => {
      document.body.style.overflow = "";
    };
  }, [open]);

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-[60] flex items-end justify-center">
      <div className="absolute inset-0 bg-black/30 backdrop-blur-sm" onClick={onClose} />
      <div className="relative w-full max-w-[440px] rounded-t-2xl border-t border-hairline bg-white p-5 pb-[max(env(safe-area-inset-bottom),20px)] shadow-float">
        <div className="mx-auto mb-4 h-1 w-10 rounded-full bg-neutral-200" />
        <div className="mb-4 flex items-center justify-between">
          <h3 className="text-base font-semibold">{title}</h3>
          <button onClick={onClose} className="text-ink-muted">
            <span className="material-symbols-outlined">close</span>
          </button>
        </div>
        {children}
      </div>
    </div>
  );
}
