import type { Camera } from "./types";

export const MIN_ZOOM = 0.1;
export const MAX_ZOOM = 8;

const clamp = (v: number, lo: number, hi: number) => Math.min(hi, Math.max(lo, v));

/** Zoom by a factor while keeping the point under (sx, sy) fixed on screen. */
export function zoomAt(cam: Camera, factor: number, sx: number, sy: number): Camera {
  const z = clamp(cam.z * factor, MIN_ZOOM, MAX_ZOOM);
  const k = z / cam.z;
  return { x: sx - (sx - cam.x) * k, y: sy - (sy - cam.y) * k, z };
}

/** Center the image in the viewport, leaving room for the pager under it. */
export function fit(viewW: number, viewH: number, imgW: number, imgH: number): Camera {
  const pad = 48;
  const pager = 48;
  const z = clamp(Math.min((viewW - pad * 2) / imgW, (viewH - pad * 2 - pager) / imgH), MIN_ZOOM, MAX_ZOOM);
  return { x: (viewW - imgW * z) / 2, y: (viewH - pager - imgH * z) / 2, z };
}
