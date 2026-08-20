const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

function setupReveals() {
  const elements = [...document.querySelectorAll(".reveal")];
  if (reduceMotion || !("IntersectionObserver" in window)) {
    elements.forEach((element) => element.classList.add("is-visible"));
    return;
  }

  const observer = new IntersectionObserver(
    (entries) => {
      for (const entry of entries) {
        if (!entry.isIntersecting) continue;
        entry.target.classList.add("is-visible");
        observer.unobserve(entry.target);
      }
    },
    { rootMargin: "0px 0px -9% 0px", threshold: 0.12 },
  );

  elements.forEach((element) => observer.observe(element));
}

function setupMagneticButtons() {
  if (reduceMotion || !window.matchMedia("(pointer: fine)").matches) return;

  for (const button of document.querySelectorAll("[data-magnetic]")) {
    button.addEventListener("pointermove", (event) => {
      const rect = button.getBoundingClientRect();
      const x = ((event.clientX - rect.left) / rect.width - 0.5) * 8;
      const y = ((event.clientY - rect.top) / rect.height - 0.5) * 8;
      button.style.transform = `translate3d(${x}px, ${y}px, 0)`;
    });
    button.addEventListener("pointerleave", () => {
      button.style.transform = "";
    });
  }
}

function setupNavigation() {
  const button = document.querySelector("[data-menu-button]");
  const links = document.querySelector("[data-nav-links]");
  if (!button || !links) return;

  button.addEventListener("click", () => {
    const open = links.classList.toggle("is-open");
    button.setAttribute("aria-expanded", String(open));
  });

  links.addEventListener("click", () => {
    links.classList.remove("is-open");
    button.setAttribute("aria-expanded", "false");
  });
}

function makeLaunchModal() {
  const backdrop = document.createElement("div");
  backdrop.className = "modal-backdrop";
  backdrop.setAttribute("role", "presentation");
  backdrop.innerHTML = `
    <section class="modal" role="dialog" aria-modal="true" aria-labelledby="launch-title">
      <div class="status-pill">Review-stage website</div>
      <h2 id="launch-title">Launch list opens after compliance review.</h2>
      <p>We are finishing payment-provider review, public support channels, and Chrome Web Store materials. No payment or email is collected on this review build.</p>
      <div class="modal-actions">
        <a class="button primary" href="support.html">View launch status</a>
        <button class="button secondary" type="button" data-close-modal>Close</button>
      </div>
    </section>`;
  document.body.append(backdrop);

  const closeButton = backdrop.querySelector("[data-close-modal]");
  const close = () => {
    backdrop.classList.remove("is-open");
    window.setTimeout(() => backdrop.remove(), reduceMotion ? 0 : 240);
  };

  closeButton.addEventListener("click", close);
  backdrop.addEventListener("click", (event) => {
    if (event.target === backdrop) close();
  });
  document.addEventListener(
    "keydown",
    (event) => {
      if (event.key === "Escape") close();
    },
    { once: true },
  );

  requestAnimationFrame(() => {
    backdrop.classList.add("is-open");
    closeButton.focus();
  });
}

function setupLaunchActions() {
  for (const action of document.querySelectorAll("[data-launch-list]")) {
    action.addEventListener("click", (event) => {
      event.preventDefault();
      makeLaunchModal();
    });
  }
}

setupReveals();
setupMagneticButtons();
setupNavigation();
setupLaunchActions();
