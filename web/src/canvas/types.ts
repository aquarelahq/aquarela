// Everything is stored in image pixels. The screen never leaks into the data.

export type Box = {
  id: string;
  cls: string;
  x: number;
  y: number;
  w: number;
  h: number;
};

export type LabelClass = {
  id: string;
  name: string;
  color: string;
  key: string;
};

export type Tool = "select" | "box";

/** Pan (x, y) in screen pixels and zoom (z) as a scale factor. */
export type Camera = { x: number; y: number; z: number };
