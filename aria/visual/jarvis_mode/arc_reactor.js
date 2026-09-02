/**
 * Jarvis Mode — Arc-Reactor HUD & Multi-layer Ring Visual Presence
 * Specs: Electric cyan (#00E5FF), deep blue (#0051FF), rotating rings, HUD framing.
 */

export class ArcReactorRenderer {
  constructor(canvas) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    this.ringAngle1 = 0;
    this.ringAngle2 = 0;
    this.ringAngle3 = 0;
    this.particles = [];
    this.initParticles(80);
  }

  initParticles(count) {
    this.particles = [];
    for (let i = 0; i < count; i++) {
      this.particles.push({
        angle: Math.random() * Math.PI * 2,
        radius: 30 + Math.random() * 80,
        speed: (Math.random() - 0.5) * 0.04,
        size: 1 + Math.random() * 2,
        life: Math.random(),
      });
    }
  }

  render(snapshot) {
    const { width, height } = this.canvas;
    const ctx = this.ctx;
    const cx = width / 2;
    const cy = height / 2;

    const amplitude = snapshot.audio_amplitude || 0;
    const scale = snapshot.scale || 1.0;
    const cyan = snapshot.primary_color || '#00E5FF';
    const deepBlue = snapshot.secondary_color || '#0051FF';

    this.ringAngle1 += 0.015 * (1 + amplitude * 2);
    this.ringAngle2 -= 0.025 * (1 + amplitude * 2);
    this.ringAngle3 += 0.008;

    // 1. Arc-Reactor Core Flare
    const coreRadius = 40 * scale * (1 + amplitude * 0.3);
    const coreGrad = ctx.createRadialGradient(
      cx, cy, 5,
      cx, cy, coreRadius * 2.5
    );
    coreGrad.addColorStop(0, '#FFFFFF');
    coreGrad.addColorStop(0.25, cyan);
    coreGrad.addColorStop(0.7, deepBlue);
    coreGrad.addColorStop(1, 'rgba(0,0,0,0)');

    ctx.save();
    ctx.fillStyle = coreGrad;
    ctx.globalAlpha = Math.min(1.0, snapshot.glow_intensity * 1.3);
    ctx.beginPath();
    ctx.arc(cx, cy, coreRadius * 2.5, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();

    // 2. Rotating Segmented Ring 1 (Inner)
    ctx.save();
    ctx.translate(cx, cy);
    ctx.rotate(this.ringAngle1);
    ctx.strokeStyle = cyan;
    ctx.lineWidth = 2.5;
    ctx.shadowBlur = 12;
    ctx.shadowColor = cyan;

    const innerRadius = 52 * scale;
    const segments = 8;
    for (let i = 0; i < segments; i++) {
      const startAngle = (i * (Math.PI * 2 / segments)) + 0.1;
      const endAngle = startAngle + (Math.PI * 2 / segments) - 0.25;
      ctx.beginPath();
      ctx.arc(0, 0, innerRadius, startAngle, endAngle);
      ctx.stroke();
    }
    ctx.restore();

    // 3. Counter-Rotating Outer Ring with Chevron Marks
    ctx.save();
    ctx.translate(cx, cy);
    ctx.rotate(this.ringAngle2);
    ctx.strokeStyle = cyan;
    ctx.lineWidth = 1.5;
    ctx.shadowBlur = 10;
    ctx.shadowColor = cyan;

    const outerRadius = 75 * scale;
    const outerSegments = 12;
    for (let i = 0; i < outerSegments; i++) {
      const angle = i * (Math.PI * 2 / outerSegments);
      ctx.beginPath();
      ctx.arc(0, 0, outerRadius, angle, angle + 0.2);
      ctx.stroke();
    }
    ctx.restore();

    // 4. Particle Vortex Fields
    ctx.save();
    this.particles.forEach((p) => {
      p.angle += p.speed * (1 + amplitude * 3);
      const px = cx + Math.cos(p.angle) * (p.radius * scale);
      const py = cy + Math.sin(p.angle) * (p.radius * scale);

      ctx.fillStyle = cyan;
      ctx.globalAlpha = 0.4 + (amplitude * 0.6);
      ctx.beginPath();
      ctx.arc(px, py, p.size, 0, Math.PI * 2);
      ctx.fill();
    });
    ctx.restore();
  }
}
