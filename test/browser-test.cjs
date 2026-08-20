const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const { chromium } = require("playwright");

const root = path.resolve(__dirname, "..");
const screenshots = path.join(root, "screenshots");
const results = path.join(root, "test-results");
const baseURL = process.env.SITE_URL || "http://127.0.0.1:4174";
// 不设 CHROME_PATH 就用 playwright 自带的 chromium，别写死本机路径
const executablePath = process.env.CHROME_PATH;

fs.mkdirSync(screenshots, { recursive: true });
fs.mkdirSync(results, { recursive: true });

async function collectPageErrors(page) {
  const failures = [];
  page.on("pageerror", (error) => failures.push(`pageerror: ${error.message}`));
  page.on("console", (message) => {
    if (message.type() === "error") failures.push(`console: ${message.text()}`);
  });
  return failures;
}

async function assertNoFailures(failures, label) {
  assert.deepEqual(failures, [], `${label} emitted browser errors:\n${failures.join("\n")}`);
}

async function testDesktop(browser) {
  const context = await browser.newContext({ viewport: { width: 1440, height: 1000 } });
  const page = await context.newPage();
  const failures = await collectPageErrors(page);

  await page.goto(`${baseURL}/`, { waitUntil: "networkidle" });
  const metrics = await page.evaluate(() => {
    const navigation = performance.getEntriesByType("navigation")[0];
    const resources = performance.getEntriesByType("resource");
    return {
      domContentLoadedMs: Math.round(navigation.domContentLoadedEventEnd),
      loadMs: Math.round(navigation.loadEventEnd),
      resourceCount: resources.length,
      transferBytes: resources.reduce((total, resource) => total + resource.transferSize, 0),
    };
  });
  assert.ok(metrics.domContentLoadedMs < 2_000, JSON.stringify(metrics));
  assert.ok(metrics.loadMs < 3_000, JSON.stringify(metrics));
  assert.ok(metrics.resourceCount <= 10, JSON.stringify(metrics));
  assert.ok(metrics.transferBytes < 200_000, JSON.stringify(metrics));
  fs.writeFileSync(
    path.join(results, "browser-metrics.json"),
    `${JSON.stringify(metrics, null, 2)}\n`,
  );
  await assertVisible(page, "h1", "Keep every last pixel.");
  await assertVisible(page, ".product-demo");
  await assertVisible(page, "#pricing");
  assert.equal(await page.locator(".menu-button").isVisible(), false);

  await page.locator("[data-launch-list]").first().click();
  await assertVisible(page, '[role="dialog"]', "Launch list opens after compliance review.");
  await page.locator("[data-close-modal]").click();
  await page.locator(".modal-backdrop").waitFor({ state: "detached" });

  const faq = page.locator("#faq details").first();
  await faq.locator("summary").click();
  assert.equal(await faq.getAttribute("open"), "");

  await revealAll(page);
  await page.screenshot({
    path: path.join(screenshots, "home-desktop.png"),
    fullPage: true,
  });

  for (const pageName of ["privacy", "terms", "refunds", "copyright", "support"]) {
    await page.goto(`${baseURL}/${pageName}.html`, { waitUntil: "networkidle" });
    await assertVisible(page, "main h1");
    await assertVisible(page, ".footer-links");
  }

  await page.goto(`${baseURL}/privacy.html`, { waitUntil: "networkidle" });
  await page.screenshot({
    path: path.join(screenshots, "privacy-desktop.png"),
    fullPage: true,
  });
  await assertNoFailures(failures, "desktop flow");
  await context.close();
}

async function testMobile(browser) {
  const context = await browser.newContext({
    viewport: { width: 390, height: 844 },
    isMobile: true,
  });
  const page = await context.newPage();
  const failures = await collectPageErrors(page);

  await page.goto(`${baseURL}/`, { waitUntil: "networkidle" });
  await assertVisible(page, "h1", "Keep every last pixel.");
  await assertVisible(page, ".menu-button");
  assert.equal(await page.locator("[data-nav-links]").isVisible(), false);

  await page.locator(".menu-button").click();
  assert.equal(await page.locator(".menu-button").getAttribute("aria-expanded"), "true");
  await assertVisible(page, "[data-nav-links]");
  await page.locator('[data-nav-links] a[href="#pricing"]').first().click();
  assert.equal(await page.locator(".menu-button").getAttribute("aria-expanded"), "false");

  await revealAll(page);
  await page.screenshot({
    path: path.join(screenshots, "home-mobile.png"),
    fullPage: true,
  });
  await assertNoFailures(failures, "mobile flow");
  await context.close();
}

async function testReducedMotion(browser) {
  const context = await browser.newContext({
    viewport: { width: 1280, height: 900 },
    reducedMotion: "reduce",
  });
  const page = await context.newPage();
  const failures = await collectPageErrors(page);

  await page.goto(`${baseURL}/`, { waitUntil: "networkidle" });
  const reveals = page.locator(".reveal");
  const count = await reveals.count();
  assert.ok(count > 0);
  for (let index = 0; index < count; index += 1) {
    assert.equal(await reveals.nth(index).evaluate((element) => element.classList.contains("is-visible")), true);
  }
  assert.equal(await page.locator(".ambient-ring").first().evaluate((element) => getComputedStyle(element).animationName), "none");

  await assertNoFailures(failures, "reduced-motion flow");
  await context.close();
}

async function assertVisible(page, selector, text) {
  const locator = page.locator(selector).first();
  await locator.waitFor({ state: "visible" });
  if (text) {
    assert.match((await locator.textContent()).replace(/\s+/g, " ").trim(), new RegExp(text.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"), "i"));
  }
}

async function revealAll(page) {
  const reveals = page.locator(".reveal");
  const count = await reveals.count();
  for (let index = 0; index < count; index += 1) {
    await reveals.nth(index).scrollIntoViewIfNeeded();
  }
  await page.evaluate(() => window.scrollTo({ top: 0, behavior: "instant" }));
  await page.waitForTimeout(100);
}

(async () => {
  const browser = await chromium.launch({ executablePath, headless: true });
  try {
    await testDesktop(browser);
    await testMobile(browser);
    await testReducedMotion(browser);
    console.log("Browser acceptance: desktop, mobile, policies, interactions, and reduced motion passed.");
    console.log(fs.readFileSync(path.join(results, "browser-metrics.json"), "utf8").trim());
  } finally {
    await browser.close();
  }
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
