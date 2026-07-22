/* Utilitários + carrossel + menu mobile */
document.addEventListener("DOMContentLoaded", () => {
  const flashes = document.querySelectorAll(".flash");
  flashes.forEach((el) => {
    setTimeout(() => {
      el.style.transition = "opacity .4s";
      el.style.opacity = "0";
      setTimeout(() => el.remove(), 400);
    }, 4500);
  });

  document.querySelectorAll("[data-carousel]").forEach(initCarousel);

  const toggle = document.getElementById("nav-toggle");
  const nav = document.getElementById("site-nav");
  if (toggle && nav) {
    toggle.addEventListener("click", () => {
      const open = nav.classList.toggle("is-open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
      toggle.textContent = open ? "✕" : "☰";
    });
    nav.querySelectorAll("a").forEach((a) => {
      a.addEventListener("click", () => {
        nav.classList.remove("is-open");
        toggle.setAttribute("aria-expanded", "false");
        toggle.textContent = "☰";
      });
    });
  }

  document.querySelectorAll("form[data-confirm]").forEach((form) => {
    form.addEventListener("submit", (e) => {
      if (!confirm(form.dataset.confirm)) e.preventDefault();
    });
  });
});

function initCarousel(root) {
  const track = root.querySelector("[data-carousel-track]");
  if (!track) return;
  const slides = [...track.children];
  if (!slides.length) return;

  const section = root.closest(".preview-menu") || root.parentElement;
  const prevBtn = section.querySelector("[data-carousel-prev]");
  const nextBtn = section.querySelector("[data-carousel-next]");
  const dotsWrap = section.querySelector("[data-carousel-dots]");

  let index = 0;
  let timer = null;

  function perView() {
    const w = window.innerWidth;
    if (w >= 1100) return 3;
    if (w >= 720) return 2;
    return 1;
  }

  function maxIndex() {
    return Math.max(0, slides.length - perView());
  }

  function renderDots() {
    if (!dotsWrap) return;
    dotsWrap.innerHTML = "";
    const pages = maxIndex() + 1;
    for (let i = 0; i < pages; i++) {
      const b = document.createElement("button");
      b.type = "button";
      b.className = "carousel-dot" + (i === index ? " is-active" : "");
      b.setAttribute("aria-label", `Ir para slide ${i + 1}`);
      b.addEventListener("click", () => goTo(i));
      dotsWrap.appendChild(b);
    }
  }

  function goTo(i) {
    index = Math.max(0, Math.min(i, maxIndex()));
    const slideW = slides[0].getBoundingClientRect().width;
    const gap = parseFloat(getComputedStyle(track).gap) || 0;
    track.style.transform = `translateX(-${index * (slideW + gap)}px)`;
    renderDots();
  }

  function next() {
    goTo(index >= maxIndex() ? 0 : index + 1);
  }

  function prev() {
    goTo(index <= 0 ? maxIndex() : index - 1);
  }

  function startAuto() {
    stopAuto();
    timer = setInterval(next, 4500);
  }

  function stopAuto() {
    if (timer) clearInterval(timer);
    timer = null;
  }

  prevBtn && prevBtn.addEventListener("click", () => { prev(); startAuto(); });
  nextBtn && nextBtn.addEventListener("click", () => { next(); startAuto(); });

  let startX = 0;
  let deltaX = 0;
  let dragging = false;

  track.addEventListener("pointerdown", (e) => {
    dragging = true;
    startX = e.clientX;
    deltaX = 0;
    stopAuto();
    track.setPointerCapture(e.pointerId);
    track.style.transition = "none";
  });

  track.addEventListener("pointermove", (e) => {
    if (!dragging) return;
    deltaX = e.clientX - startX;
    const slideW = slides[0].getBoundingClientRect().width;
    const gap = parseFloat(getComputedStyle(track).gap) || 0;
    track.style.transform = `translateX(${-index * (slideW + gap) + deltaX}px)`;
  });

  function endDrag() {
    if (!dragging) return;
    dragging = false;
    track.style.transition = "";
    if (Math.abs(deltaX) > 50) {
      deltaX < 0 ? next() : prev();
    } else {
      goTo(index);
    }
    startAuto();
  }

  track.addEventListener("pointerup", endDrag);
  track.addEventListener("pointercancel", endDrag);

  window.addEventListener("resize", () => goTo(Math.min(index, maxIndex())));

  goTo(0);
  startAuto();
  root.addEventListener("mouseenter", stopAuto);
  root.addEventListener("mouseleave", startAuto);
}
