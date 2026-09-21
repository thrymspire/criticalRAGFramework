/**
 * Phase 4 — Polish & Integration: The Circle UI (circle.js)
 * Implements calibrated token logprob physics, dynamic entropy ring, and ReAct agent telemetry.
 */

class EntropyCircleVisualizer {
  constructor(canvasId) {
    this.canvas = document.getElementById(canvasId);
    if (!this.canvas) return;
    this.ctx = this.canvas.getContext('2d');

    // Current animated state
    this.currentEntropy = 0.0;
    this.targetEntropy = 0.0;
    this.currentToken = "";
    this.currentProb = 0.0;
    this.targetProb = 0.0;

    // Spoke targets and currents
    this.spokes = [];
    this.targetSpokes = [];

    // Orbital particles
    this.particles = [];
    this.baseRadius = 50;
    this.maxRadius = 140;
    this.rotationOffset = 0;
    this.pulsePhase = 0;

    this.initParticles();
    this.resize();
    window.addEventListener('resize', () => this.resize());
    this.animate();
  }

  initParticles() {
    this.particles = [];
    for (let i = 0; i < 16; i++) {
      this.particles.push({
        angle: Math.random() * 2 * Math.PI,
        speed: 0.008 + Math.random() * 0.012,
        radiusOffset: (Math.random() - 0.5) * 8
      });
    }
  }

  resize() {
    const parent = this.canvas.parentElement;
    const rect = parent ? parent.getBoundingClientRect() : { width: 440, height: 440 };
    const size = Math.max(340, Math.min(rect.width || 440, 480));
    const dpr = window.devicePixelRatio || 1;

    this.canvas.width = size * dpr;
    this.canvas.height = size * dpr;
    this.canvas.style.width = `${size}px`;
    this.canvas.style.height = `${size}px`;
    this.ctx.scale(dpr, dpr);

    this.width = size;
    this.height = size;
    this.cx = size / 2;
    this.cy = size / 2;
    this.baseRadius = size * 0.16;
    this.maxRadius = size * 0.42;
  }

  update(data) {
    if (!data) return;
    this.targetEntropy = Math.max(0, Number(data.entropy) || 0);
    this.currentToken = data.chosen_token || "";
    this.targetProb = Math.max(0, Math.min(1.0, Number(data.prob) || 0));

    const topList = data.top || [];
    const n = Math.max(1, topList.length);

    this.targetSpokes = topList.map((item, idx) => {
      const angle = (idx * (2 * Math.PI / n)) - (Math.PI / 2);
      const isChosen = item.token === this.currentToken;
      return {
        token: item.token,
        prob: item.prob,
        angle: angle,
        isChosen: isChosen
      };
    });

    if (this.spokes.length !== this.targetSpokes.length) {
      this.spokes = this.targetSpokes.map(s => ({ ...s, currentLen: 0 }));
    }
  }

  lerp(a, b, t) {
    return a + (b - a) * t;
  }

  getEntropyColor(entropy) {
    // Status colors:
    // Low entropy (< 0.6) = Tight bioluminescent cyan (#5ffbf1)
    // Moderate entropy (0.6 - 1.4) = Balanced purple (#c084fc)
    // High entropy (> 1.4) = Wide warning coral (#ff6b81)
    if (entropy < 0.6) {
      return { stroke: '#5ffbf1', glow: 'rgba(95, 251, 241, 0.65)', label: 'GROUNDED CERTAINTY', tier: 'low' };
    } else if (entropy < 1.4) {
      return { stroke: '#c084fc', glow: 'rgba(192, 132, 252, 0.55)', label: 'BALANCED SYNTHESIS', tier: 'mid' };
    } else {
      return { stroke: '#ff6b81', glow: 'rgba(255, 107, 129, 0.7)', label: 'EPISTEMIC GAP RISK', tier: 'high' };
    }
  }

  animate() {
    this.pulsePhase += 0.04;
    this.rotationOffset += 0.0018;

    // Smooth physics lerping
    this.currentEntropy = this.lerp(this.currentEntropy, this.targetEntropy, 0.14);
    this.currentProb = this.lerp(this.currentProb, this.targetProb, 0.16);

    // Update Spokes
    for (let i = 0; i < this.spokes.length; i++) {
      if (this.targetSpokes[i]) {
        const targetLen = this.baseRadius + (this.targetSpokes[i].prob * (this.maxRadius - this.baseRadius));
        this.spokes[i].currentLen = this.lerp(this.spokes[i].currentLen || 0, targetLen, 0.16);
        this.spokes[i].token = this.targetSpokes[i].token;
        this.spokes[i].prob = this.targetSpokes[i].prob;
        this.spokes[i].isChosen = this.targetSpokes[i].isChosen;
        this.spokes[i].angle = this.targetSpokes[i].angle;
      }
    }

    this.draw();
    requestAnimationFrame(() => this.animate());
  }

  draw() {
    const ctx = this.ctx;
    ctx.clearRect(0, 0, this.width, this.height);

    const config = this.getEntropyColor(this.currentEntropy);

    // 1. Ambient Background Guides
    ctx.save();
    ctx.beginPath();
    ctx.arc(this.cx, this.cy, this.maxRadius, 0, 2 * Math.PI);
    ctx.strokeStyle = 'rgba(157, 92, 255, 0.18)';
    ctx.lineWidth = 1;
    ctx.setLineDash([3, 6]);
    ctx.stroke();

    ctx.beginPath();
    ctx.arc(this.cx, this.cy, this.baseRadius, 0, 2 * Math.PI);
    ctx.strokeStyle = 'rgba(157, 92, 255, 0.3)';
    ctx.stroke();
    ctx.restore();

    // 2. Dynamic Entropy Ring
    const entropyExpansion = Math.min(this.maxRadius - this.baseRadius - 10, this.currentEntropy * 28);
    const ringRadius = this.baseRadius + entropyExpansion + Math.sin(this.pulsePhase) * 2;
    const ringThickness = Math.max(2.5, 2.5 + this.currentEntropy * 2.2);

    ctx.save();
    ctx.beginPath();
    ctx.arc(this.cx, this.cy, ringRadius, 0, 2 * Math.PI);
    ctx.strokeStyle = config.stroke;
    ctx.lineWidth = ringThickness;
    ctx.shadowColor = config.stroke;
    ctx.shadowBlur = 14 + this.currentEntropy * 8;
    ctx.stroke();

    // Orbiting Particles on the Entropy Ring
    this.particles.forEach((p) => {
      p.angle += p.speed;
      const px = this.cx + Math.cos(p.angle) * (ringRadius + p.radiusOffset);
      const py = this.cy + Math.sin(p.angle) * (ringRadius + p.radiusOffset);

      ctx.beginPath();
      ctx.arc(px, py, 2.2, 0, 2 * Math.PI);
      ctx.fillStyle = config.stroke;
      ctx.shadowColor = config.stroke;
      ctx.shadowBlur = 8;
      ctx.fill();
    });
    ctx.restore();

    // 3. Radial Probability Spokes
    this.spokes.forEach((spoke) => {
      const angle = spoke.angle + this.rotationOffset;
      const len = spoke.currentLen || this.baseRadius;
      const x1 = this.cx + Math.cos(angle) * (this.baseRadius * 0.9);
      const y1 = this.cy + Math.sin(angle) * (this.baseRadius * 0.9);
      const x2 = this.cx + Math.cos(angle) * len;
      const y2 = this.cy + Math.sin(angle) * len;

      ctx.save();
      ctx.beginPath();
      ctx.moveTo(x1, y1);
      ctx.lineTo(x2, y2);

      if (spoke.isChosen) {
        ctx.strokeStyle = '#5ffbf1';
        ctx.lineWidth = 4.0;
        ctx.shadowColor = '#5ffbf1';
        ctx.shadowBlur = 16;
      } else {
        ctx.strokeStyle = 'rgba(192, 132, 252, 0.55)';
        ctx.lineWidth = 1.8;
        ctx.shadowColor = '#9d5cff';
        ctx.shadowBlur = 6;
      }
      ctx.stroke();

      // Node Marker at Spoke Tip
      ctx.beginPath();
      ctx.arc(x2, y2, spoke.isChosen ? 5.5 : 3.5, 0, 2 * Math.PI);
      ctx.fillStyle = spoke.isChosen ? '#5ffbf1' : '#c084fc';
      ctx.fill();
      ctx.restore();

      // Label at Spoke Tip
      const labelX = this.cx + Math.cos(angle) * (len + 18);
      const labelY = this.cy + Math.sin(angle) * (len + 18);
      ctx.save();
      ctx.font = spoke.isChosen ? 'bold 11px "JetBrains Mono", monospace' : '9px "JetBrains Mono", monospace';
      ctx.fillStyle = spoke.isChosen ? '#5ffbf1' : '#d8c6ff';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      const pctStr = `${Math.round(spoke.prob * 100)}%`;
      const tokClean = JSON.stringify(spoke.token || "");
      ctx.fillText(`${tokClean} ${pctStr}`, labelX, labelY);
      ctx.restore();
    });

    // 4. Central Generation Hub
    ctx.save();
    ctx.beginPath();
    ctx.arc(this.cx, this.cy, this.baseRadius * 0.85, 0, 2 * Math.PI);
    const grad = ctx.createRadialGradient(this.cx, this.cy, 5, this.cx, this.cy, this.baseRadius * 0.85);
    grad.addColorStop(0, 'rgba(34, 16, 60, 0.95)');
    grad.addColorStop(1, 'rgba(10, 5, 18, 0.98)');
    ctx.fillStyle = grad;
    ctx.strokeStyle = config.stroke;
    ctx.lineWidth = 2.5;
    ctx.shadowColor = config.stroke;
    ctx.shadowBlur = 16;
    ctx.fill();
    ctx.stroke();
    ctx.restore();

    // Central Token & Metric Readout
    ctx.save();
    ctx.font = 'bold 13px "Space Grotesk", sans-serif';
    ctx.fillStyle = '#ede6ff';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    const displayTok = this.currentToken ? JSON.stringify(this.currentToken) : "ARMED";
    ctx.fillText(displayTok, this.cx, this.cy - 7);

    ctx.font = '9px "JetBrains Mono", monospace';
    ctx.fillStyle = config.stroke;
    ctx.fillText(`H: ${this.currentEntropy.toFixed(2)}b`, this.cx, this.cy + 11);
    ctx.restore();
  }
}

window.EntropyCircleVisualizer = EntropyCircleVisualizer;
