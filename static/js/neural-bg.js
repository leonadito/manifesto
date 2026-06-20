(function () {
  // Factory: cria uma rede neural de partículas. Sem opts -> canvas fixo global (atrás de
  // todo o conteúdo). Com { canvas } -> usa um canvas existente dimensionado ao seu container
  // (usado na hero, por cima do vídeo). Os dois modos compartilham a mesma lógica de desenho.
  function createNeuralBg(opts) {
    opts = opts || {};
    var canvas = opts.canvas || null;
    var fixed = !canvas; // sem canvas dado => instância global fixa

    if (!canvas) {
      canvas = document.createElement('canvas');
      canvas.style.cssText = 'position:fixed;top:0;left:0;z-index:0;pointer-events:none;background:transparent;';
      document.body.appendChild(canvas);
    }

    var ctx = canvas.getContext('2d');
    var mouse = { x: -1000, y: -1000, active: false };
    var scrollY = 0;
    var particles = [];

    var PARTICLE_COUNT = opts.count != null ? opts.count : 60;
    var CONNECTION_DIST = opts.connectionDist != null ? opts.connectionDist : 120;
    var MOUSE_DIST = opts.mouseDist != null ? opts.mouseDist : 180;
    var HEADER_H = opts.headerH != null ? opts.headerH : 90;
    var parallax = opts.parallax !== false; // global usa parallax de scroll; hero não

    function dims() {
      if (fixed) return { w: window.innerWidth, h: window.innerHeight };
      var p = canvas.parentElement;
      return { w: p.clientWidth, h: p.clientHeight };
    }

    function resize() {
      var d = dims();
      canvas.width = d.w; canvas.height = d.h;
      canvas.style.width = d.w + 'px'; canvas.style.height = d.h + 'px';
      init();
    }

    function init() {
      particles = [];
      for (var i = 0; i < PARTICLE_COUNT; i++) {
        var x = Math.random() * canvas.width;
        var y = HEADER_H + 10 + Math.random() * (canvas.height - HEADER_H - 20);
        particles.push({ x: x, y: y, vx: (Math.random() - 0.5) * 0.4, vy: (Math.random() - 0.5) * 0.4,
          radius: Math.random() * 2 + 1, baseY: y, hue: Math.random() });
      }
    }

    function lerp(a, b, t) { return Math.round(a + (b - a) * t); }

    function animate() {
      var w = canvas.width, h = canvas.height;
      ctx.clearRect(0, 0, w, h);
      ctx.save();
      ctx.beginPath(); ctx.rect(0, HEADER_H, w, h - HEADER_H); ctx.clip();

      for (var i = 0; i < particles.length; i++) {
        var p = particles[i];
        p.baseY += p.vy; p.x += p.vx;
        if (p.x < -10) p.x = w + 10;
        if (p.x > w + 10) p.x = -10;
        if (p.baseY < HEADER_H + 10) p.baseY = h - 10;
        if (p.baseY > h + 10) p.baseY = HEADER_H + 10;
        var maxShift = h * 0.15;
        var shift = parallax ? Math.max(-maxShift, Math.min(maxShift, scrollY * 0.06)) : 0;
        p.y = Math.max(HEADER_H + 2, p.baseY - shift);
        if (p.x < 0 || p.x > w) continue;
        var fade = Math.min(1, (p.y - HEADER_H) / 40);
        var r = lerp(33, 240, p.hue), g = lerp(49, 45, p.hue), b = lerp(122, 98, p.hue);
        ctx.beginPath(); ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(' + r + ',' + g + ',' + b + ',' + (0.55 * fade) + ')';
        ctx.fill();
      }

      for (var i = 0; i < particles.length; i++) {
        var p1 = particles[i];
        if (p1.y < HEADER_H || p1.x < 0 || p1.x > w) continue;
        if (mouse.active && mouse.y > HEADER_H) {
          var dx = p1.x - mouse.x, dy = p1.y - mouse.y;
          var d = Math.sqrt(dx * dx + dy * dy);
          if (d < MOUSE_DIST) {
            ctx.beginPath(); ctx.moveTo(p1.x, p1.y); ctx.lineTo(mouse.x, mouse.y);
            ctx.strokeStyle = 'rgba(240,45,98,' + ((1 - d / MOUSE_DIST) * 0.22) + ')';
            ctx.lineWidth = 1; ctx.stroke();
          }
        }
        for (var j = i + 1; j < particles.length; j++) {
          var p2 = particles[j];
          if (p2.y < HEADER_H || p2.x < 0 || p2.x > w) continue;
          var dx = p1.x - p2.x, dy = p1.y - p2.y;
          var d = Math.sqrt(dx * dx + dy * dy);
          if (d < CONNECTION_DIST) {
            var avg = (p1.hue + p2.hue) / 2;
            var r = lerp(33, 240, avg), g = lerp(49, 45, avg), b = lerp(122, 98, avg);
            ctx.beginPath(); ctx.moveTo(p1.x, p1.y); ctx.lineTo(p2.x, p2.y);
            ctx.strokeStyle = 'rgba(' + r + ',' + g + ',' + b + ',' + ((1 - d / CONNECTION_DIST) * 0.18) + ')';
            ctx.lineWidth = 0.8; ctx.stroke();
          }
        }
      }
      ctx.restore();
      requestAnimationFrame(animate);
    }

    // Resize: global observa o documento; instância scoped observa o próprio container.
    new ResizeObserver(resize).observe(fixed ? document.documentElement : canvas.parentElement);

    // Mouse em coordenadas locais do canvas (para a instância fixa o offset é 0,0).
    window.addEventListener('mousemove', function (e) {
      var ox = 0, oy = 0;
      if (!fixed) { var r = canvas.getBoundingClientRect(); ox = r.left; oy = r.top; }
      mouse.x = e.clientX - ox; mouse.y = e.clientY - oy; mouse.active = true;
    });
    document.addEventListener('mouseleave', function () { mouse.x = -1000; mouse.y = -1000; mouse.active = false; });
    if (parallax) {
      window.addEventListener('scroll', function () { scrollY = window.scrollY; }, { passive: true });
    }

    resize();
    animate();
  }

  // Instância global (comportamento original, atrás de todo o conteúdo).
  createNeuralBg();

  // Instância da hero (por cima do vídeo): sem parallax, sem recorte de header.
  var heroCanvas = document.querySelector('.heroParticles');
  if (heroCanvas) {
    createNeuralBg({ canvas: heroCanvas, parallax: false, headerH: 0 });
  }
})();
