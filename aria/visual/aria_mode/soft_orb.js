/**
 * Aria Mode — Soft Luminous Orb Visual Presence
 * Specs: Cool blues (#8FA8FF), soft violets (#D4BFFF), gentle bloom, orbital particles.
 */

export class SoftOrbRenderer {
  constructor(canvas) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    this.particles = [];
    this.initParticles(45);
    this.rotation = 0;
  }

  initParticles(count) {
    this.particles = [];
    for (let i = 0; i < count; i++) {
      this.particles.push({
        angle: Math.random() * Math.PI * 2,
        distance: 40 + Math.random() * 50,
        speed: 0.005 + Math.random() * 0.015,
        radius: 1.0 + Math.random() * 2.0,
        alpha: 0.2 + Math.random() * 0.6
      });
    }
  }

  render(snapshot) {
    const { width, height } = this.canvas;
    const ctx = this.ctx;
    const cx = width / 2;
    const cy = height / 2;

    const baseRadius = 55 * snapshot.scale;
    const amplitude = snapshot.audio_amplitude || 0;
    const reactiveRadius = baseRadius + (amplitude * 25);

    // 1. Outer Bloom
    const gradient = ctx.createRadialGradient(
      cx, cy, baseRadius * 0.2,
      cx, cy, reactiveRadius * 2.2
    );
    gradient.addColorStop(0, snapshot.primary_color || '#8FA8FF');
    gradient.addColorStop(0.4, snapshot.secondary_color || '#D4BFFF');
    gradient.addColorStop(1, 'rgba(0, 0, 0, 0)');

    ctx.save();
    ctx.globalAlpha = Math.min(1.0, snapshot.glow_intensity);
    ctx.fillStyle = gradient;
    ctx.beginPath();
    ctx.arc(cx, cy, reactiveRadius * 2.2, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();

    // 2. Core Soft Sphere
    const coreGrad = ctx.createRadialGradient(
      cx - (reactiveRadius * 0.3), cy - (reactiveRadius * 0.3), reactiveRadius * 0.1,
      cx, cy, reactiveRadius
    );
    coreGrad.addColorStop(0, '#FFFFFF');
    coreGrad.addColorStop(0.3, snapshot.primary_color || '#8FA8FF');
    coreGrad.addColorStop(1, snapshot.secondary_color || '#D4BFFF');

    ctx.save();
    ctx.fillStyle = coreGrad;
    ctx.beginPath();
    ctx.arc(cx, cy, reactiveRadius, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();

    // 3. Orbital Particles
    ctx.save();
    this.particles.forEach((p) => {
      p.angle += p.speed * (1 + amplitude * 2);
      const px = cx + Math.cos(p.angle) * (p.distance * snapshot.scale);
      const py = cy + Math.sin(p.angle) * (p.distance * snapshot.scale);

      ctx.fillStyle = snapshot.secondary_color || '#D4BFFF';
      ctx.globalAlpha = p.alpha;
      ctx.beginPath();
      ctx.arc(px, py, p.radius, 0, Math.PI * 2);
      ctx.fill();
    });
    ctx.restore();
  }
}
