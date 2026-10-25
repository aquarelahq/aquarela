import { useEffect, useMemo, useRef, useState } from "react";
import { Canvas } from "./canvas/Canvas";
import type { Box, LabelClass, Tool } from "./canvas/types";
import { sampleImages } from "./sample";

const CLASSES: LabelClass[] = [
  { id: "ripe", name: "Ripe", color: "#e86a92", key: "1" },
  { id: "unripe", name: "Unripe", color: "#f2b84b", key: "2" },
  { id: "disease", name: "Leaf disease", color: "#6cc4a1", key: "3" },
  { id: "plant", name: "Plant", color: "#9b8cff", key: "4" },
];

type Status = "todo" | "in_progress" | "in_review" | "done";
const STATUS: Record<Status, [string, string]> = {
  todo: ["To do", "#5a5a60"],
  in_progress: ["In progress", "#7aa7ff"],
  in_review: ["In review", "#f2b84b"],
  done: ["Done", "#6cc4a1"],
};

type Item = { name: string; src: string; boxes: Box[]; status: Status };

function useImage(src: string) {
  const [img, setImg] = useState<HTMLImageElement | null>(null);
  useEffect(() => {
    const i = new Image();
    i.onload = () => setImg(i);
    i.src = src;
  }, [src]);
  return img;
}

export function App() {
  const [items, setItems] = useState<Item[]>(() => sampleImages().map((s) => ({ ...s, boxes: [], status: "todo" })));
  const [index, setIndex] = useState(0);
  const [tool, setTool] = useState<Tool>("box");
  const [activeClass, setActiveClass] = useState("ripe");
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const fileRef = useRef<HTMLInputElement>(null);

  const item = items[index];
  const image = useImage(item.src);

  const setBoxes = (boxes: Box[]) =>
    setItems((all) => all.map((it, i) => (i === index ? { ...it, boxes, status: it.status === "todo" ? "in_progress" : it.status } : it)));
  const setStatus = (status: Status) => setItems((all) => all.map((it, i) => (i === index ? { ...it, status } : it)));
  const go = (d: number) => {
    setSelectedId(null);
    setIndex((i) => Math.min(items.length - 1, Math.max(0, i + d)));
  };

  const openFiles = (files: FileList | null) => {
    if (!files?.length) return;
    const added = [...files]
      .filter((f) => f.type.startsWith("image/"))
      .map((f) => ({ name: f.name, src: URL.createObjectURL(f), boxes: [], status: "todo" as Status }));
    if (!added.length) return;
    setItems(added);
    setIndex(0);
    setSelectedId(null);
  };

  // Keyboard shortcuts
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (document.activeElement instanceof HTMLInputElement) return;
      const k = e.key.toLowerCase();
      if (k === "v") setTool("select");
      if (k === "b") setTool("box");
      const cls = CLASSES.find((c) => c.key === e.key);
      if (cls) {
        setActiveClass(cls.id);
        if (selectedId) setBoxes(item.boxes.map((b) => (b.id === selectedId ? { ...b, cls: cls.id } : b)));
      }
      if ((e.key === "Delete" || e.key === "Backspace") && selectedId) {
        setBoxes(item.boxes.filter((b) => b.id !== selectedId));
        setSelectedId(null);
      }
      if (e.key === "Escape") setSelectedId(null);
      if (e.key === "ArrowLeft") go(-1);
      if (e.key === "ArrowRight") go(1);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  });

  const counts = useMemo(() => Object.fromEntries(CLASSES.map((c) => [c.id, item.boxes.filter((b) => b.cls === c.id).length])), [item]);
  const [statusLabel, statusColor] = STATUS[item.status];

  return (
    <div
      className="app"
      onDragOver={(e) => e.preventDefault()}
      onDrop={(e) => { e.preventDefault(); openFiles(e.dataTransfer.files); }}
    >
      <header>
        <div className="logo"><i />Aquarela</div>
        <div className="crumb">blueberry-field-2026</div>
        <div className="spacer" />
        <input ref={fileRef} type="file" accept="image/*" multiple hidden onChange={(e) => openFiles(e.target.files)} />
        <button className="btn" onClick={() => fileRef.current?.click()}>Open images</button>
        <button className="btn primary">Export</button>
      </header>

      <nav className="tools">
        <button className={`tool ${tool === "select" ? "on" : ""}`} onClick={() => setTool("select")} title="Select (V)">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M5 3l14 8-6 2-2 6z" /></svg>
          <kbd>V</kbd>
        </button>
        <button className={`tool ${tool === "box" ? "on" : ""}`} onClick={() => setTool("box")} title="Box (B)">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="4" y="5" width="16" height="14" rx="1" /></svg>
          <kbd>B</kbd>
        </button>
      </nav>

      <main>
        {image && (
          <Canvas
            image={image}
            boxes={item.boxes}
            classes={CLASSES}
            activeClass={activeClass}
            tool={tool}
            selectedId={selectedId}
            onSelect={setSelectedId}
            onChange={setBoxes}
            below={
              <div className="pager">
                <button onClick={() => go(-1)} disabled={index === 0}>‹</button>
                <span>{index + 1} / {items.length}</span>
                <button onClick={() => go(1)} disabled={index === items.length - 1}>›</button>
              </div>
            }
          />
        )}
      </main>

      <aside>
        <section>
          <h3>Image</h3>
          <div className="field"><span>Name</span><b>{item.name}</b></div>
          <div className="field">
            <span>Status</span>
            <span className="status"><i style={{ background: statusColor }} />{statusLabel}</span>
          </div>
        </section>
        <section>
          <h3>Classes</h3>
          {CLASSES.map((c) => (
            <div key={c.id} className={`row ${c.id === activeClass ? "on" : ""}`} onClick={() => setActiveClass(c.id)}>
              <span className="dot" style={{ background: c.color }} />
              {c.name}
              <span className="n">{counts[c.id]}</span>
              <kbd>{c.key}</kbd>
            </div>
          ))}
        </section>
        <section>
          <h3>Labels <span>{item.boxes.length}</span></h3>
          {item.boxes.length === 0 && <p className="empty">Press B and drag on the image to draw a box.</p>}
          {item.boxes.map((b) => (
            <div key={b.id} className={`row ${b.id === selectedId ? "on" : ""}`} onClick={() => { setTool("select"); setSelectedId(b.id); }}>
              <span className="dot" style={{ background: CLASSES.find((c) => c.id === b.cls)?.color }} />
              {CLASSES.find((c) => c.id === b.cls)?.name}
              <span className="n">{Math.round(b.w)}×{Math.round(b.h)}</span>
            </div>
          ))}
        </section>
        <section>
          <h3>Review</h3>
          <div className="review">
            <button className="btn" onClick={() => setStatus("in_progress")}>Request changes</button>
            <button className="btn primary" onClick={() => { setStatus("done"); go(1); }}>Accept</button>
          </div>
        </section>
      </aside>
    </div>
  );
}
