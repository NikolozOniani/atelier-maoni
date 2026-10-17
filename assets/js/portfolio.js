/* The complete project HTML is present before this enhancement runs. */
const cards = [...document.querySelectorAll(".portfolio .project-card")];
const filters = [...document.querySelectorAll("[data-filter]")];
const resultCount = document.querySelector("[data-results]");
if (cards.length && filters.length) {
  const applyFilter = (category) => {
    const selected =
      filters.find((button) => button.dataset.filter === category) ||
      filters[0];
    filters.forEach((button) =>
      button.setAttribute("aria-pressed", String(button === selected)),
    );
    cards.forEach((card) => {
      card.hidden =
        selected.dataset.filter !== "all" &&
        card.dataset.category !== selected.dataset.filter;
    });
    if (resultCount)
      resultCount.textContent = `${cards.filter((card) => !card.hidden).length} ${resultCount.dataset.label}`;
    document.querySelectorAll(".language-switch a").forEach((link) => {
      const target = new URL(link.href);
      if (selected.dataset.filter === "all")
        target.searchParams.delete("category");
      else target.searchParams.set("category", selected.dataset.filter);
      link.href = target.href;
    });
  };
  document.querySelector(".filters").hidden = false;
  filters.forEach((button) =>
    button.addEventListener("click", () => {
      applyFilter(button.dataset.filter);
      const url = new URL(location.href);
      if (button.dataset.filter === "all") url.searchParams.delete("category");
      else url.searchParams.set("category", button.dataset.filter);
      history.replaceState(null, "", url);
    }),
  );
  applyFilter(new URLSearchParams(location.search).get("category") || "all");
}

const viewer = document.querySelector(".viewer");
if (viewer && typeof viewer.showModal === "function") {
  document.documentElement.classList.add("gallery-enhanced");
  const projects = new Map(
    [...document.querySelectorAll(".project-card")].map((card) => [
      card.id,
      {
        title: card.querySelector("h3").textContent,
        images: [...card.querySelectorAll(".project-gallery a")].map(
          (link) => ({ src: link.href, alt: link.dataset.alt }),
        ),
      },
    ]),
  );
  const photo = viewer.querySelector(".viewer-image");
  const title = viewer.querySelector(".viewer-title");
  const caption = viewer.querySelector(".viewer-caption");
  const counter = viewer.querySelector(".viewer-counter");
  const previous = viewer.querySelector("[data-previous]");
  const next = viewer.querySelector("[data-next]");
  let active,
    index = 0,
    opener,
    touchStart = null;
  const render = () => {
    const item = active.images[index];
    photo.src = item.src;
    photo.alt = item.alt;
    title.textContent = active.title;
    caption.textContent = item.alt;
    counter.textContent = `${index + 1} / ${active.images.length}`;
    viewer.querySelector(".viewer-label").textContent =
      `${viewer.dataset.imageLabel} ${index + 1} ${viewer.dataset.ofLabel} ${active.images.length}`;
    previous.disabled = active.images.length < 2;
    next.disabled = active.images.length < 2;
  };
  const move = (amount) => {
    index = (index + amount + active.images.length) % active.images.length;
    render();
  };
  document.addEventListener("click", (event) => {
    const link = event.target.closest("[data-view-project]");
    if (
      !link ||
      event.ctrlKey ||
      event.metaKey ||
      event.shiftKey ||
      event.altKey
    )
      return;
    active = projects.get(link.dataset.viewProject);
    if (!active) return;
    event.preventDefault();
    opener = link;
    index = Number(link.dataset.imageIndex || 0);
    render();
    viewer.showModal();
    viewer.querySelector(".viewer-close").focus();
  });
  viewer
    .querySelector(".viewer-close")
    .addEventListener("click", () => viewer.close());
  previous.addEventListener("click", () => move(-1));
  next.addEventListener("click", () => move(1));
  viewer.addEventListener("keydown", (event) => {
    if (event.key === "ArrowRight") {
      event.preventDefault();
      move(1);
    }
    if (event.key === "ArrowLeft") {
      event.preventDefault();
      move(-1);
    }
    if (event.key === "Tab") {
      const controls = [...viewer.querySelectorAll("button:not(:disabled)")];
      const first = controls[0],
        last = controls.at(-1);
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    }
  });
  viewer.addEventListener("close", () => {
    photo.removeAttribute("src");
    opener?.focus();
  });
  viewer.addEventListener("click", (event) => {
    if (event.target === viewer) viewer.close();
  });
  photo.addEventListener(
    "touchstart",
    (event) => {
      touchStart = event.changedTouches[0].clientX;
    },
    { passive: true },
  );
  photo.addEventListener(
    "touchend",
    (event) => {
      if (touchStart === null) return;
      const distance = event.changedTouches[0].clientX - touchStart;
      if (Math.abs(distance) > 55) move(distance < 0 ? 1 : -1);
      touchStart = null;
    },
    { passive: true },
  );
}
