(function () {
  // A hero é pinada (ScrollTrigger). Se a página recarrega rolada para baixo, o browser
  // restaura o scroll DEPOIS do load e bagunça o cálculo do pin/spacer — a hero (vídeo +
  // texto) some ao voltar ao topo. Desativar a restauração automática faz a página sempre
  // carregar no topo, com o pin calculado corretamente. Roda imediatamente (antes do load).
  if ('scrollRestoration' in history) history.scrollRestoration = 'manual';

  function setup() {
    var heroSection = document.querySelector('.heroContainer');
    var stepsWrap = document.getElementById('gsap-steps');
    if (!heroSection || !stepsWrap) return;
    var steps = Array.from(stepsWrap.children);
    if (steps.length < 3) return;

    // ScrollTrigger guarda a própria memória de posição e a restaura no reload, mesmo com
    // scrollRestoration='manual'. Limpar essa memória + forçar topo evita que a hero pinada
    // volte "presa" no estado final ao recarregar rolado para baixo.
    if (window.ScrollTrigger && ScrollTrigger.clearScrollMemory) ScrollTrigger.clearScrollMemory();
    window.scrollTo(0, 0);

    gsap.set(steps[0], { opacity: 1, y: 0 });
    gsap.set(steps[1], { opacity: 0, y: 30, position: 'absolute', top: '50%', left: '50%',
      xPercent: -50, yPercent: -50, width: '100%' });
    gsap.set(steps[2], { opacity: 0, y: 30, position: 'absolute', top: '50%', left: '50%',
      xPercent: -50, yPercent: -50, width: '100%' });

    // --- Native <video> scroll-scrub ---
    var video      = document.getElementById('hero-video');
    var videoBg    = heroSection.querySelector('.heroVideoBg');
    var duration   = 0;
    var targetTime = 0;
    var smoothTime = 0;

    if (video) {
      var revealed = false;
      function reveal() {
        if (revealed) return;
        revealed = true;
        if (videoBg) videoBg.style.opacity = '1';
      }

      // Grab a finite duration as soon as one is known. A non-faststart MP4 can report
      // NaN/Infinity until fully downloaded, which would freeze the scrub — guard for it.
      function updateDuration() {
        var d = video.duration;
        if (isFinite(d) && d > 0) duration = d;
      }
      video.addEventListener('loadedmetadata', updateDuration);
      video.addEventListener('durationchange', updateDuration);
      video.addEventListener('canplay', updateDuration);

      function onReady() {
        try { video.currentTime = 0; } catch (e) {}
        reveal();
      }
      // 'loadeddata' fires once the first frame is decoded and paintable.
      video.addEventListener('loadeddata', onReady);

      // The Django dev server doesn't support HTTP Range requests, so the browser marks the
      // video as NOT seekable (seekable.length === 0) — every `currentTime =` silently snaps
      // back to 0. Fix: fetch the whole file into a Blob and play it from an in-memory
      // object URL. With all bytes local, the video becomes fully seekable regardless of
      // what the server supports. Cheap for a small hero clip and ideal for scrubbing.
      var srcUrl = video.currentSrc || video.getAttribute('src');
      fetch(srcUrl)
        .then(function (r) { return r.blob(); })
        .then(function (blob) {
          video.src = URL.createObjectURL(blob);
          video.load();
        })
        .catch(function () {
          // Fallback: if the fetch fails, still try to use whatever already loaded.
          if (video.readyState >= 1) updateDuration();
          if (video.readyState >= 2) onReady();
        });

      // Safety net: never leave the hero permanently blank.
      setTimeout(reveal, 1500);

      // Tick on GSAP's own RAF. Native currentTime is synchronous and fast in BOTH
      // directions, so no seek queue/watchdog is needed — just lerp toward the target
      // for a smooth, eased scrub.
      gsap.ticker.add(function () {
        if (!duration) return;
        smoothTime += (targetTime - smoothTime) * 0.15;
        if (Math.abs(targetTime - smoothTime) > 0.01) {
          try { video.currentTime = Math.min(smoothTime, duration - 0.05); } catch (e) {}
        }
      });
    }

    var tl = gsap.timeline({
      scrollTrigger: {
        trigger: heroSection,
        start: 'top top',
        end: 'bottom+=200% bottom',
        scrub: 0.5,
        pin: true,
        anticipatePin: 1,
        invalidateOnRefresh: true,
        onUpdate: function (self) {
          if (duration > 0) targetTime = self.progress * duration;
        }
      }
    });

    tl.to(steps[0],   { opacity: 0, y: -30, ease: 'power1.out' }, 0.1);
    tl.fromTo(steps[1], { opacity: 0, y: 30 }, { opacity: 1, y: 0, ease: 'power1.inOut' }, 0.3);
    tl.to(steps[1],   { opacity: 0, y: -30, ease: 'power1.in' }, 0.6);
    tl.fromTo(steps[2], { opacity: 0, y: 30 }, { opacity: 1, y: 0, ease: 'power1.inOut' }, 0.75);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', setup);
  } else {
    setup();
  }

  // Após o load completo (fontes, vídeo, layout assentado), garante topo + recálculo do pin.
  // Sem isso, o pin pode ficar com medidas obsoletas quando a página recarrega rolada.
  window.addEventListener('load', function () {
    window.scrollTo(0, 0);
    if (window.ScrollTrigger) {
      if (ScrollTrigger.clearScrollMemory) ScrollTrigger.clearScrollMemory();
      ScrollTrigger.refresh();
    }
  });
})();
