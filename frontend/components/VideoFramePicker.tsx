"use client";
import { useEffect, useRef, useState } from "react";
export default function VideoFramePicker({ onSelect, disabled = false }: { onSelect: (file: File) => void; disabled?: boolean }) {
  const [file, setFile] = useState<File | null>(null);
  const [url, setUrl] = useState(""); const [ready, setReady] = useState(false); const [error, setError] = useState("");
  const video = useRef<HTMLVideoElement>(null); const input = useRef<HTMLInputElement>(null);
  useEffect(() => { setReady(false); setError(""); if (!file) { setUrl(""); return; } const u = URL.createObjectURL(file); setUrl(u); return () => URL.revokeObjectURL(u); }, [file]);
  const select = () => {
    const v = video.current; if (!v?.videoWidth) return; v.pause();
    const c = document.createElement("canvas"); c.width = v.videoWidth; c.height = v.videoHeight;
    c.getContext("2d")?.drawImage(v, 0, 0);
    c.toBlob(blob => { if (blob) { onSelect(new File([blob], "background-video-frame.jpg", { type: "image/jpeg" })); setFile(null); if (input.current) input.current.value = ""; } else setError("Could not capture this frame."); }, "image/jpeg", 0.95);
  };
  return <div className="mt-4 space-y-2">
    <label className="label">Or choose a frame from a video
      <input ref={input} type="file" className="input mt-2" accept="video/*" disabled={disabled} onChange={e => setFile(e.target.files?.[0] || null)} />
    </label>
    <p className="text-xs text-white/50">Play or scrub to a frame, pause, then use it as your background. Only the still frame is uploaded; video motion and audio are not used.</p>
    {url && <><video ref={video} src={url} controls playsInline preload="auto" onLoadedData={() => setReady(true)} onSeeking={() => setReady(false)} onSeeked={() => setReady(true)} onError={() => { setReady(false); setError("This browser cannot play this video. Try an MP4 file."); }} className="max-h-64 w-full rounded" />
      <button type="button" disabled={disabled || !ready} className="btn-ghost" onClick={select}>Use this frame</button>
      <button type="button" className="btn-ghost" onClick={() => { setFile(null); if (input.current) input.current.value = ""; }}>Cancel video</button></>}
    {error && <p role="alert" className="text-sm text-red-400">{error}</p>}
  </div>;
}
