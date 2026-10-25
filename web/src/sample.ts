// A painted field scene so the app has something to label before you open your own images.

function paint(seed: number): string {
  const W = 2000, H = 1250;
  const c = document.createElement("canvas");
  c.width = W;
  c.height = H;
  const g = c.getContext("2d")!;
  let s = seed;
  const rnd = () => ((s = (s * 9301 + 49297) % 233280) / 233280);

  const sky = g.createLinearGradient(0, 0, 0, H * 0.75);
  sky.addColorStop(0, "#cfe3e8");
  sky.addColorStop(1, "#e8efe4");
  g.fillStyle = sky;
  g.fillRect(0, 0, W, H);

  const soil = g.createLinearGradient(0, H * 0.75, 0, H);
  soil.addColorStop(0, "#8a7356");
  soil.addColorStop(1, "#5e4c38");
  g.fillStyle = soil;
  g.fillRect(0, H * 0.75, W, H * 0.25);

  // Bushes made of soft overlapping blobs
  for (const cx of [560, 1460]) {
    for (let i = 0; i < 26; i++) {
      g.fillStyle = `hsla(${118 + rnd() * 20}, ${28 + rnd() * 12}%, ${28 + rnd() * 12}%, 0.55)`;
      g.beginPath();
      g.ellipse(cx + (rnd() - 0.5) * 700, 600 + (rnd() - 0.5) * 420, 120 + rnd() * 160, 90 + rnd() * 120, 0, 0, Math.PI * 2);
      g.fill();
    }
    // Berries
    for (let i = 0; i < 14; i++) {
      const x = cx + (rnd() - 0.5) * 520, y = 520 + rnd() * 320, ripe = rnd() > 0.35;
      g.fillStyle = ripe ? "#3a3f8f" : "#9cb06a";
      g.beginPath();
      g.arc(x, y, 26, 0, Math.PI * 2);
      g.fill();
      g.fillStyle = "rgba(255,255,255,.35)";
      g.beginPath();
      g.arc(x - 8, y - 8, 7, 0, Math.PI * 2);
      g.fill();
    }
  }
  return c.toDataURL("image/jpeg", 0.9);
}

export function sampleImages(): { name: string; src: string }[] {
  return [3, 17, 42].map((seed, i) => ({ name: `row-14_${String(231 + i).padStart(4, "0")}.jpg`, src: paint(seed) }));
}
