/* 한국증시 레시피 — theme + scroll-spy. Framework-free. */
(function () {
  'use strict';

  /* ---- theme ---- */
  var root = document.documentElement;
  var KEY = 'krsr-theme';
  function applyTheme(t) { root.setAttribute('data-theme', t); }
  var saved = null;
  try { saved = localStorage.getItem(KEY); } catch (e) {}
  if (saved === 'light' || saved === 'dark') {
    applyTheme(saved);
  } else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
    applyTheme('dark');
  } else {
    applyTheme('light');
  }
  document.addEventListener('click', function (e) {
    var btn = e.target.closest && e.target.closest('[data-theme-toggle]');
    if (!btn) return;
    var next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    applyTheme(next);
    try { localStorage.setItem(KEY, next); } catch (err) {}
  });

  /* ---- 모바일 햄버거 메뉴 토글 ---- */
  document.addEventListener('click', function (e) {
    var nav = document.querySelector('.site-header .nav');
    if (!nav) return;
    var toggle = e.target.closest && e.target.closest('[data-nav-toggle]');
    if (toggle) {
      var open = nav.classList.toggle('is-open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
      return;
    }
    // 메뉴 밖 클릭 시 닫기
    if (nav.classList.contains('is-open') && !e.target.closest('.nav')) {
      nav.classList.remove('is-open');
    }
  });

  /* ---- scroll-spy for article section nav ---- */
  // 헤딩 id 가 한글이면 Hugo 가 href 를 %xx 로 URL 인코딩하지만 element id 는 원문이라
  // 그대로 비교하면 안 맞는다 → href 를 디코드해서 id 와 맞춘다(ASCII 는 그대로).
  function targetId(a) {
    var raw = a.getAttribute('href').slice(1);
    try { return decodeURIComponent(raw); } catch (e) { return raw; }
  }
  function initSpy() {
    var nav = document.querySelector('[data-secnav]');
    if (!nav) return;
    var links = Array.prototype.slice.call(nav.querySelectorAll('a[href^="#"]'));
    if (!links.length) return;
    var sections = links.map(function (a) {
      return document.getElementById(targetId(a));
    }).filter(Boolean);
    var progressBar = document.querySelector('[data-progress]');

    function setActive(id) {
      links.forEach(function (a) {
        a.classList.toggle('is-active', targetId(a) === id);
      });
      // 모바일 칩바: 활성 뱃지를 가운데로 부드럽게 자동 스크롤(항상 보이게)
      var list = nav.querySelector('.secnav__list');
      var active = nav.querySelector('a.is-active');
      if (active && list && list.scrollWidth > list.clientWidth + 4) {
        var lr = active.getBoundingClientRect(), cr = list.getBoundingClientRect();
        var target = list.scrollLeft + (lr.left - cr.left) - (cr.width - lr.width) / 2;
        list.scrollTo({ left: Math.max(0, target), behavior: 'smooth' });
      }
    }

    var io = new IntersectionObserver(function (entries) {
      // choose the topmost section currently intersecting
      var visible = entries.filter(function (en) { return en.isIntersecting; });
      if (visible.length) {
        visible.sort(function (a, b) { return a.boundingClientRect.top - b.boundingClientRect.top; });
        setActive(visible[0].target.id);
      }
    }, { rootMargin: '-25% 0px -65% 0px', threshold: 0 });

    sections.forEach(function (s) { io.observe(s); });

    // smooth-scroll + progress
    links.forEach(function (a) {
      a.addEventListener('click', function (ev) {
        var el = document.getElementById(targetId(a));
        if (!el) return;
        ev.preventDefault();
        var y = el.getBoundingClientRect().top + window.pageYOffset - 80;
        window.scrollTo({ top: y, behavior: 'smooth' });
        history.replaceState(null, '', a.getAttribute('href'));
      });
    });

    function onScroll() {
      if (!progressBar) return;
      var doc = document.documentElement;
      var h = doc.scrollHeight - doc.clientHeight;
      var p = h > 0 ? Math.min(1, Math.max(0, doc.scrollTop / h)) : 0;
      progressBar.style.width = (p * 100).toFixed(1) + '%';
    }
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initSpy);
  } else {
    initSpy();
  }
})();
