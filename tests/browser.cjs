/* Development-only QA: requires Playwright, axe-core/playwright and Chromium.
 * MAONI_BASE_URL selects either the root or a project-directory deployment.
 */
const assert = require("node:assert/strict");
const { chromium } = require("playwright");
const AxeBuilder = require(
  process.env.MAONI_AXE_MODULE || "@axe-core/playwright",
).default;
const base = (process.env.MAONI_BASE_URL || "http://127.0.0.1:8000").replace(
  /\/$/,
  "",
);
let checks = 0;
function check(condition, message) {
  assert.ok(condition, message);
  checks++;
}

(async () => {
  const browser = await chromium.launch({
    executablePath: process.env.MAONI_CHROMIUM || "/usr/bin/chromium",
    args: ["--no-sandbox"],
  });
  const errors = [];
  const context = await browser.newContext();
  context.on("page", (page) => {
    page.on("pageerror", (error) => errors.push(error.message));
    page.on("response", (response) => {
      if (response.url().startsWith(base) && response.status() >= 400)
        errors.push(`${response.status()} ${response.url()}`);
    });
  });
  try {
    for (const lang of ["ka", "en"]) {
      for (const section of ["", "work/", "contact/"]) {
        const page = await context.newPage();
        for (const width of [320, 390, 768, 1440]) {
          await page.setViewportSize({ width, height: 900 });
          await page.goto(`${base}/${lang}/${section}`);
          await page.evaluate(async () => {
            await document.fonts.ready;
            document
              .querySelectorAll("img[loading=lazy]")
              .forEach((image) => (image.loading = "eager"));
            await Promise.all(
              [...document.images]
                .filter((image) => image.src)
                .map((image) => image.decode()),
            );
          });
          check(
            (await page.locator("html").getAttribute("lang")) === lang,
            `Document language ${lang} ${section}`,
          );
          check(
            (await page.locator("h1").count()) === 1,
            `One main heading ${lang} ${section}`,
          );
          check(
            await page.evaluate(
              () => document.documentElement.scrollWidth <= innerWidth,
            ),
            `Horizontal overflow ${lang}/${section} at ${width}`,
          );
          check(
            (await page.locator(".language-switch a").count()) === 2,
            "Visible language links",
          );
          const other = lang === "ka" ? "en" : "ka";
          check(
            (
              await page
                .locator(`.language-switch a[lang=${other}]`)
                .getAttribute("href")
            ).endsWith(`${other}/${section}`),
            `Equivalent-page language switch ${section}`,
          );
          check(
            (await page.locator('a[href="tel:+995592120806"]').count()) >= 1,
            "Correct telephone",
          );
          if (width === 390 || width === 1440) {
            const audit = await new AxeBuilder({ page })
              .withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"])
              .analyze();
            check(
              audit.violations.length === 0,
              `Accessibility ${lang}/${section} ${width}: ${JSON.stringify(audit.violations.map((v) => ({ id: v.id, nodes: v.nodes.map((n) => n.target) })))}`,
            );
          }
          if (width === 390) {
            const toggle = page.locator(".menu-toggle");
            await toggle.click();
            check(
              (await toggle.getAttribute("aria-expanded")) === "true",
              "Mobile menu opens",
            );
            check(
              await page.locator(".main-nav").isVisible(),
              "Mobile links visible",
            );
            await page.keyboard.press("Escape");
            check(
              (await toggle.getAttribute("aria-expanded")) === "false",
              "Escape closes mobile menu",
            );
          }
        }
        if (section === "contact/") {
          check(
            (await page
              .locator('a[href="https://share.google/f6iwNu64FvXnETX4t"]')
              .count()) === 1,
            "Exact supplied map destination",
          );
          check(
            (await page
              .locator('a[href="https://wa.me/995592120806"]')
              .count()) === 1,
            "Correct WhatsApp destination",
          );
          check(
            (await page
              .locator('a[href="https://www.facebook.com/maoni00/"]')
              .count()) === 1,
            "Correct Facebook destination",
          );
        }
        await page.close();
      }
      const page = await context.newPage();
      await page.goto(`${base}/${lang}/work/`);
      check(
        (await page.locator(".project-card:visible").count()) === 14,
        "All projects initially visible",
      );
      for (const [category, count] of [
        ["evening", 7],
        ["everyday", 2],
        ["children", 3],
        ["bridal", 1],
        ["traditional", 1],
      ]) {
        await page.locator(`[data-filter=${category}]`).click();
        check(
          (await page.locator(".project-card:visible").count()) === count,
          `Filter ${category}`,
        );
        check(
          (await page.locator("[data-results]").textContent()) ===
            `${count} ${await page.locator("[data-results]").getAttribute("data-label")}`,
          "Live results count",
        );
        check(
          new URL(page.url()).searchParams.get("category") === category,
          "Shareable filter URL",
        );
      }
      const other = lang === "ka" ? "en" : "ka";
      await page.locator(`.language-switch a[lang=${other}]`).click();
      check(
        (await page.locator(".project-card:visible").count()) === 1,
        "Selected filter survives language switch",
      );
      check(
        new URL(page.url()).pathname.endsWith(`/${other}/work/`),
        "Actual language navigation preserves work page",
      );
      await page.locator("[data-filter=all]").click();
      const opener = page.locator("#silver .project-image");
      await opener.click();
      check(
        await page.locator(".viewer").evaluate((dialog) => dialog.open),
        "Lightbox opens",
      );
      await page.locator(".viewer-image").evaluate((image) => image.decode());
      const first = await page.locator(".viewer-image").getAttribute("src");
      await page.locator("[data-next]").click();
      check(
        (await page.locator(".viewer-image").getAttribute("src")) !== first,
        "Next photo changes image",
      );
      await page.keyboard.press("ArrowLeft");
      check(
        (await page.locator(".viewer-image").getAttribute("src")) === first,
        "Keyboard previous photo",
      );
      await page.keyboard.press("ArrowLeft");
      check(
        (await page.locator(".viewer-counter").textContent()) === "2 / 2",
        "Previous wraps within garment",
      );
      await page
        .locator(".viewer-image")
        .dispatchEvent("touchstart", {
          changedTouches: [{ identifier: 1, clientX: 200, clientY: 100 }],
        });
      await page
        .locator(".viewer-image")
        .dispatchEvent("touchend", {
          changedTouches: [{ identifier: 1, clientX: 70, clientY: 100 }],
        });
      check(
        (await page.locator(".viewer-counter").textContent()) === "1 / 2",
        "Touch gesture changes photo",
      );
      const dialogAudit = await new AxeBuilder({ page })
        .withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"])
        .analyze();
      check(
        dialogAudit.violations.length === 0,
        `Dialog accessibility: ${JSON.stringify(dialogAudit.violations.map((v) => v.id))}`,
      );
      // Native modal dialog must keep keyboard focus inside until it closes.
      for (let i = 0; i < 7; i++) {
        await page.keyboard.press("Tab");
        check(
          await page.evaluate(
            () => !!document.activeElement.closest(".viewer"),
          ),
          "Focus trapped in image viewer",
        );
      }
      await page.keyboard.press("Escape");
      check(
        !(await page.locator(".viewer").evaluate((dialog) => dialog.open)),
        "Escape closes lightbox",
      );
      check(
        await opener.evaluate((link) => document.activeElement === link),
        "Focus returns to thumbnail",
      );
      await page.locator("#yellow .project-image").click();
      check(
        await page.locator("[data-next]").isDisabled(),
        "Single-image project disables next",
      );
      await page.locator(".viewer-close").click();
      check(
        !(await page.locator(".viewer").evaluate((dialog) => dialog.open)),
        "Close button works",
      );
      await page.close();
    }
    const noJS = await browser.newContext({
      javaScriptEnabled: false,
      viewport: { width: 390, height: 844 },
    });
    for (const lang of ["ka", "en"]) {
      const page = await noJS.newPage();
      await page.goto(`${base}/${lang}/work/`);
      check(
        (await page.locator(".project-card").count()) === 14,
        "Gallery exists without JavaScript",
      );
      check(
        await page.locator(".project-gallery a").first().isVisible(),
        "Alternate images accessible without JavaScript",
      );
      check(
        await page.locator(".main-nav").isVisible(),
        "Navigation accessible without JavaScript",
      );
      check(
        await page.evaluate(
          () => document.documentElement.scrollWidth <= innerWidth,
        ),
        "No-JavaScript mobile layout",
      );
      await page.close();
    }
    await noJS.close();
    const entry = await context.newPage();
    await entry.goto(`${base}/`);
    await entry.waitForURL(`${base}/ka/`);
    check(
      new URL(entry.url()).pathname.endsWith("/ka/"),
      "Root defaults to Georgian",
    );
    check(errors.length === 0, `Browser errors: ${errors.join("; ")}`);
    console.log(
      `PASS: ${checks} browser checks at ${base}; 6 pages × 4 viewports, 12 page accessibility audits, 2 modal audits, interactions and no-JavaScript fallbacks.`,
    );
  } finally {
    await browser.close();
  }
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
