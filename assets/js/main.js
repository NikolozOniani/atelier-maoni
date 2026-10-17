/* Progressive navigation: all page links remain usable without JavaScript. */
document.documentElement.classList.add("js");
const menuButton = document.querySelector(".menu-toggle");
const menu = document.querySelector(".main-nav");
if (menuButton && menu) {
  function closeMenu(restoreFocus = false) {
    menuButton.setAttribute("aria-expanded", "false");
    menuButton.querySelector(".menu-text").textContent =
      menuButton.dataset.openLabel;
    menu.classList.remove("is-open");
    if (restoreFocus) menuButton.focus();
  }
  menuButton.addEventListener("click", () => {
    const opening = menuButton.getAttribute("aria-expanded") !== "true";
    menuButton.setAttribute("aria-expanded", String(opening));
    menuButton.querySelector(".menu-text").textContent = opening
      ? menuButton.dataset.closeLabel
      : menuButton.dataset.openLabel;
    menu.classList.toggle("is-open", opening);
  });
  document.addEventListener("keydown", (event) => {
    if (
      event.key === "Escape" &&
      menuButton.getAttribute("aria-expanded") === "true"
    )
      closeMenu(true);
  });
  document.addEventListener("click", (event) => {
    if (!event.target.closest(".site-header")) closeMenu();
  });
  menu.addEventListener("click", (event) => {
    if (event.target.closest("a")) closeMenu();
  });
  matchMedia("(min-width: 761px)").addEventListener("change", () =>
    closeMenu(),
  );
}
