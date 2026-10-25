import { useEffect, useRef, useState, type ReactNode } from "react";
import type Konva from "konva";
import { Group, Image as KImage, Layer, Rect, Stage, Transformer } from "react-konva";
import { fit, zoomAt } from "./camera";
import type { Box, Camera, LabelClass, Tool } from "./types";

type Props = {
  image: HTMLImageElement;
  boxes: Box[];
  classes: LabelClass[];
  activeClass: string;
  tool: Tool;
  selectedId: string | null;
  onSelect: (id: string | null) => void;
  onChange: (boxes: Box[]) => void;
  /** Rendered centered at the bottom edge of the canvas, fixed on screen. */
  below?: ReactNode;
};

type Pan = { sx: number; sy: number; cam: Camera };
type Draft = { x0: number; y0: number; x1: number; y1: number };

const isTyping = () => document.activeElement instanceof HTMLInputElement;

/**
 * The labeling canvas. One camera (pan and zoom) moves a single group that
 * holds the image at (0, 0), so every box lives in image pixels.
 */
export function Canvas({ image, boxes, classes, activeClass, tool, selectedId, onSelect, onChange, below }: Props) {
  const wrapRef = useRef<HTMLDivElement>(null);
  const groupRef = useRef<Konva.Group>(null);
  const trRef = useRef<Konva.Transformer>(null);
  const [size, setSize] = useState({ w: 0, h: 0 });
  const [cam, setCam] = useState<Camera>({ x: 0, y: 0, z: 1 });
  const [pan, setPan] = useState<Pan | null>(null);
  const [draft, setDraft] = useState<Draft | null>(null);
  const [space, setSpace] = useState(false);

  const iw = image.naturalWidth;
  const ih = image.naturalHeight;
  const color = (cls: string) => classes.find((c) => c.id === cls)?.color ?? "#fff";

  // Track the viewport size
  useEffect(() => {
    const el = wrapRef.current!;
    const ro = new ResizeObserver(([e]) => setSize({ w: e.contentRect.width, h: e.contentRect.height }));
    ro.observe(el);
    return () => ro.disconnect();
  }, []);

  // Fit when the image changes or the viewport is first measured
  const fitted = useRef<HTMLImageElement | null>(null);
  useEffect(() => {
    if (!size.w || fitted.current === image) return;
    fitted.current = image;
    setCam(fit(size.w, size.h, iw, ih));
  }, [image, size, iw, ih]);

  // Keyboard: Space to pan, F to fit
  useEffect(() => {
    const down = (e: KeyboardEvent) => {
      if (isTyping()) return;
      if (e.code === "Space") { setSpace(true); e.preventDefault(); }
      if (e.key === "f") setCam(fit(size.w, size.h, iw, ih));
    };
    const up = (e: KeyboardEvent) => { if (e.code === "Space") setSpace(false); };
    window.addEventListener("keydown", down);
    window.addEventListener("keyup", up);
    return () => { window.removeEventListener("keydown", down); window.removeEventListener("keyup", up); };
  }, [size, iw, ih]);

  // Attach the resize handles to the selected box
  useEffect(() => {
    const tr = trRef.current;
    if (!tr) return;
    const node = selectedId ? groupRef.current?.findOne(`#${selectedId}`) : null;
    tr.nodes(node && tool === "select" ? [node] : []);
  }, [selectedId, boxes, tool]);

  /** Pointer position in image pixels. */
  const imagePoint = () => groupRef.current!.getRelativePointerPosition()!;
  const clampX = (v: number) => Math.min(iw, Math.max(0, v));
  const clampY = (v: number) => Math.min(ih, Math.max(0, v));

  const onWheel = (e: Konva.KonvaEventObject<WheelEvent>) => {
    e.evt.preventDefault();
    const p = e.target.getStage()!.getPointerPosition()!;
    if (e.evt.ctrlKey || e.evt.metaKey) setCam((c) => zoomAt(c, Math.exp(-e.evt.deltaY * 0.01), p.x, p.y));
    else setCam((c) => ({ ...c, x: c.x - e.evt.deltaX, y: c.y - e.evt.deltaY }));
  };

  const onMouseDown = (e: Konva.KonvaEventObject<MouseEvent>) => {
    const onBox = e.target.hasName("box") || e.target.getParent()?.className === "Transformer";
    const wantsPan = space || e.evt.button === 1 || (tool === "select" && !onBox);
    if (wantsPan) {
      if (tool === "select" && !onBox) onSelect(null);
      setPan({ sx: e.evt.clientX, sy: e.evt.clientY, cam });
      return;
    }
    if (tool === "box" && e.evt.button === 0) {
      const p = imagePoint();
      setDraft({ x0: clampX(p.x), y0: clampY(p.y), x1: clampX(p.x), y1: clampY(p.y) });
    }
  };

  const onMouseMove = (e: Konva.KonvaEventObject<MouseEvent>) => {
    if (pan) {
      // Pan moves exactly as far as the mouse
      setCam({ ...pan.cam, x: pan.cam.x + e.evt.clientX - pan.sx, y: pan.cam.y + e.evt.clientY - pan.sy });
    } else if (draft) {
      const p = imagePoint();
      setDraft({ ...draft, x1: clampX(p.x), y1: clampY(p.y) });
    }
  };

  const onMouseUp = () => {
    if (draft) {
      const x = Math.min(draft.x0, draft.x1), y = Math.min(draft.y0, draft.y1);
      const w = Math.abs(draft.x1 - draft.x0), h = Math.abs(draft.y1 - draft.y0);
      // Ignore accidental clicks: at least 4 screen pixels each way
      if (w * cam.z > 4 && h * cam.z > 4) {
        const id = "b" + Math.random().toString(36).slice(2, 9);
        onChange([...boxes, { id, cls: activeClass, x, y, w, h }]);
        onSelect(id);
      }
    }
    setDraft(null);
    setPan(null);
  };

  const update = (id: string, patch: Partial<Box>) => onChange(boxes.map((b) => (b.id === id ? { ...b, ...patch } : b)));

  // Strokes keep the same size on screen at any zoom
  const px = 1 / cam.z;
  const cursor = pan ? "grabbing" : space ? "grab" : tool === "box" ? "crosshair" : "default";
  const grid = 22 * cam.z;

  return (
    <div
      ref={wrapRef}
      className="canvas"
      style={{ cursor, backgroundSize: `${grid}px ${grid}px`, backgroundPosition: `${cam.x}px ${cam.y}px` }}
    >
      {size.w > 0 && (
        <Stage
          width={size.w}
          height={size.h}
          onWheel={onWheel}
          onMouseDown={onMouseDown}
          onMouseMove={onMouseMove}
          onMouseUp={onMouseUp}
          onMouseLeave={onMouseUp}
        >
          <Layer>
            <Group ref={groupRef} x={cam.x} y={cam.y} scaleX={cam.z} scaleY={cam.z}>
              <Rect width={iw} height={ih} shadowColor="black" shadowBlur={60 * px} shadowOpacity={0.5} fill="#000" />
              <KImage image={image} width={iw} height={ih} />

              {boxes.map((b) => (
                <Rect
                  key={b.id}
                  id={b.id}
                  name="box"
                  x={b.x}
                  y={b.y}
                  width={b.w}
                  height={b.h}
                  stroke={color(b.cls)}
                  strokeWidth={(b.id === selectedId ? 3 : 2) * px}
                  fill={color(b.cls) + "38"}
                  opacity={selectedId && selectedId !== b.id ? 0.45 : 1}
                  draggable={tool === "select" && !space}
                  onMouseDown={() => tool === "select" && onSelect(b.id)}
                  onDragEnd={(e) => update(b.id, { x: e.target.x(), y: e.target.y() })}
                  onTransformEnd={(e) => {
                    const n = e.target;
                    const patch = { x: n.x(), y: n.y(), w: n.width() * n.scaleX(), h: n.height() * n.scaleY() };
                    n.scaleX(1);
                    n.scaleY(1);
                    update(b.id, patch);
                  }}
                />
              ))}

              {draft && (
                <Rect
                  x={Math.min(draft.x0, draft.x1)}
                  y={Math.min(draft.y0, draft.y1)}
                  width={Math.abs(draft.x1 - draft.x0)}
                  height={Math.abs(draft.y1 - draft.y0)}
                  stroke={color(activeClass)}
                  strokeWidth={2 * px}
                  dash={[6 * px, 4 * px]}
                  listening={false}
                />
              )}

              <Transformer ref={trRef} rotateEnabled={false} ignoreStroke anchorSize={8} borderStroke="#ffffff" anchorStroke="#ffffff" anchorFill="#111" anchorCornerRadius={2} />
            </Group>
          </Layer>
        </Stage>
      )}

      {below && <div className="below">{below}</div>}
    </div>
  );
}
