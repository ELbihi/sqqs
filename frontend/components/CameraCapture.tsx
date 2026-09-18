"use client";
import { useEffect, useRef, useState } from "react";

export default function CameraCapture({ onCapture, disabled = false }: { onCapture: (file: File) => void; disabled?: boolean }) {
  const [open, setOpen] = useState(false);
  const [facing, setFacing] = useState<"user" | "environment">("environment");
  const [error, setError] = useState("");
  const [ready, setReady] = useState(false);
  const video = useRef<HTMLVideoElement>(null);
  useEffect(() => {
    if (!open) return;
    let cancelled = false; let stream: MediaStream | undefined;
    setReady(false); setError("");
    if (!navigator.mediaDevices?.getUserMedia) { setError("Camera access requires HTTPS or localhost. You can still upload a photo."); return; }
    navigator.mediaDevices.getUserMedia({ video: { facingMode: { ideal: facing } }, audio: false }).then(s => {
      if (cancelled) { s.getTracks().forEach(t => t.stop()); return; }
      stream = s; if (video.current) video.current.srcObject = s;
    }).catch(() => { if (!cancelled) setError("Could not open the camera. Allow camera access in your browser, or upload a photo."); });
    return () => { cancelled = true; stream?.getTracks().forEach(t => t.stop()); };
  }, [open, facing]);
  const capture = () => {
    const v = video.current; if (!v?.videoWidth) return;
    const canvas = document.createElement("canvas"); canvas.width = v.videoWidth; canvas.height = v.videoHeight;
    canvas.getContext("2d")?.drawImage(v, 0, 0);
    canvas.toBlob(blob => { if (blob) { onCapture(new File([blob], `camera-${Date.now()}.jpg`, { type: "image/jpeg" })); setOpen(false); } }, "image/jpeg", 0.95);
  };
  return <div className="mt-2">
    <button type="button" className="btn-ghost text-sm" disabled={disabled} onClick={() => setOpen(true)}>Take a photo</button>
    {open && <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 p-4" role="dialog" aria-modal="true" aria-label="Take a photo">
      <div className="card w-full max-w-lg space-y-3">
        <video ref={video} autoPlay playsInline muted onLoadedData={() => setReady(true)} className="max-h-[65vh] w-full rounded" />
        {error && <p role="alert" className="text-sm text-red-400">{error}</p>}
        <div className="flex flex-wrap gap-2">
          <button type="button" className="btn-primary" disabled={!ready || !!error} onClick={capture}>Capture photo</button>
          <button type="button" className="btn-ghost" onClick={() => setFacing(f => f === "user" ? "environment" : "user")}>Switch camera</button>
          <button type="button" className="btn-ghost" onClick={() => setOpen(false)}>Cancel</button>
        </div>
      </div>
    </div>}
  </div>;
}
