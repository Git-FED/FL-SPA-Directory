(function () {
  'use strict';

  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function setupMobileNav() {
    var toggle = document.getElementById('menuToggle');
    var nav = document.getElementById('primaryNav');
    if (!toggle || !nav) return;
    toggle.addEventListener('click', function () {
      var open = toggle.getAttribute('aria-expanded') === 'true';
      toggle.setAttribute('aria-expanded', String(!open));
      nav.classList.toggle('is-open', !open);
    });
    nav.querySelectorAll('a').forEach(function (link) {
      link.addEventListener('click', function () {
        toggle.setAttribute('aria-expanded', 'false');
        nav.classList.remove('is-open');
      });
    });
  }

  function setupReveals() {
    var nodes = document.querySelectorAll('.trust-strip, .directory-section, .premium-section, .subscriber, .method-section, .site-footer, .archive-console, .signal-gallery, .feature-grid > div');
    nodes.forEach(function (node) { node.setAttribute('data-reveal', ''); });
    if (reduceMotion || !('IntersectionObserver' in window)) {
      nodes.forEach(function (node) { node.classList.add('is-visible'); });
      return;
    }
    var observer = new IntersectionObserver(function (entries, obs) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          obs.unobserve(entry.target);
        }
      });
    }, { threshold: .12, rootMargin: '0px 0px -35px' });
    nodes.forEach(function (node) { observer.observe(node); });
  }

  function setupMagneticButtons() {
    if (reduceMotion || !window.matchMedia('(pointer: fine)').matches) return;
    document.querySelectorAll('.button, button, .text-link').forEach(function (el) {
      el.addEventListener('pointermove', function (event) {
        var rect = el.getBoundingClientRect();
        var x = (event.clientX - rect.left - rect.width / 2) * .12;
        var y = (event.clientY - rect.top - rect.height / 2) * .12;
        el.style.transform = 'translate(' + x + 'px,' + y + 'px)';
      });
      el.addEventListener('pointerleave', function () { el.style.transform = ''; });
    });
  }

  function setupTilt() {
    if (reduceMotion || !window.matchMedia('(pointer: fine)').matches) return;
    function bind(card) {
      if (card.dataset.tiltBound) return;
      card.dataset.tiltBound = 'true';
      card.addEventListener('pointermove', function (event) {
        var rect = card.getBoundingClientRect();
        var rotateY = ((event.clientX - rect.left) / rect.width - .5) * 5;
        var rotateX = ((event.clientY - rect.top) / rect.height - .5) * -5;
        card.style.transform = 'perspective(700px) rotateX(' + rotateX + 'deg) rotateY(' + rotateY + 'deg) translateY(-2px)';
      });
      card.addEventListener('pointerleave', function () { card.style.transform = ''; });
    }
    document.querySelectorAll('.feature-grid > div, .trust-strip > div').forEach(bind);
    new MutationObserver(function (mutations) {
      mutations.forEach(function (mutation) {
        mutation.addedNodes.forEach(function (node) {
          if (node.nodeType !== 1) return;
          if (node.matches && node.matches('.parlor-card')) bind(node);
          if (node.querySelectorAll) node.querySelectorAll('.parlor-card').forEach(bind);
        });
      });
    }).observe(document.getElementById('parlorList') || document.body, { childList: true });
  }

  function setupParticles() {
    var canvas = document.getElementById('particleCanvas');
    if (!canvas || reduceMotion) return;
    var ctx = canvas.getContext('2d');
    var points = [];
    var pointer = { x: -9999, y: -9999 };
    var dpr = Math.min(window.devicePixelRatio || 1, 2);
    function resize() {
      var rect = canvas.getBoundingClientRect();
      canvas.width = rect.width * dpr;
      canvas.height = rect.height * dpr;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      var count = Math.min(44, Math.max(22, Math.floor(rect.width / 28)));
      points = Array.from({ length: count }, function () {
        return { x: Math.random() * rect.width, y: Math.random() * rect.height, vx: (Math.random() - .5) * .22, vy: (Math.random() - .5) * .22, r: Math.random() * 1.5 + .4 };
      });
    }
    function tick() {
      var rect = canvas.getBoundingClientRect();
      ctx.clearRect(0, 0, rect.width, rect.height);
      points.forEach(function (p, i) {
        p.x += p.vx; p.y += p.vy;
        if (p.x < 0 || p.x > rect.width) p.vx *= -1;
        if (p.y < 0 || p.y > rect.height) p.vy *= -1;
        var dx = pointer.x - p.x, dy = pointer.y - p.y;
        var distance = Math.sqrt(dx * dx + dy * dy);
        if (distance < 150) { p.x -= dx * .0008; p.y -= dy * .0008; }
        ctx.beginPath(); ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2); ctx.fillStyle = i % 3 === 0 ? 'rgba(0,240,255,.7)' : 'rgba(112,0,255,.6)'; ctx.fill();
        for (var j = i + 1; j < points.length; j++) {
          var q = points[j], qx = p.x - q.x, qy = p.y - q.y, dist = Math.sqrt(qx * qx + qy * qy);
          if (dist < 120) { ctx.beginPath(); ctx.moveTo(p.x, p.y); ctx.lineTo(q.x, q.y); ctx.strokeStyle = 'rgba(0,240,255,' + ((1 - dist / 120) * .13) + ')'; ctx.stroke(); }
        }
      });
      window.setTimeout(function () { requestAnimationFrame(tick); }, 33);
    }
    canvas.addEventListener('pointermove', function (event) { var rect = canvas.getBoundingClientRect(); pointer.x = event.clientX - rect.left; pointer.y = event.clientY - rect.top; });
    canvas.addEventListener('pointerleave', function () { pointer.x = -9999; pointer.y = -9999; });
    window.addEventListener('resize', resize);
    resize(); tick();
  }

  document.addEventListener('DOMContentLoaded', function () {
    setupMobileNav(); setupReveals();
  });
}());
