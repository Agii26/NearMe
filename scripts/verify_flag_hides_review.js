const { chromium } = require("/home/claude/.npm-global/lib/node_modules/playwright");

const CHROME_PATH = "/home/claude/.cache/puppeteer/chrome/linux-131.0.6778.204/chrome-linux64/chrome";

(async () => {
  const browser = await chromium.launch({ executablePath: CHROME_PATH, args: ["--no-sandbox"] });
  const page = await browser.newPage({ viewport: { width: 375, height: 900 } });

  await page.goto("http://localhost:5173/register", { waitUntil: "networkidle" });
  await page.getByLabel("Username").fill("e2e_flagger2");
  await page.getByLabel("Email").fill("e2e_flagger2@example.com");
  await page.getByLabel("Password").fill("a-strong-password-123");
  await page.click('button[type="submit"]');
  await page.waitForURL("http://localhost:5173/", { timeout: 10000 });

  await page.click("a[href^='/business/']");
  await page.waitForSelector("text=Reviews", { timeout: 10000 });
  await page.screenshot({ path: "/home/claude/nearme/docs/screenshots/phase3-before-flag-spec-fix.png" });

  const reviewCountBefore = await page.locator("text=e2e_reviewer").count();
  console.log("Review by e2e_reviewer visible before flagging:", reviewCountBefore === 1);

  await page.click('button[aria-label="Report this review"]');
  await page.waitForSelector("text=Review reported", { timeout: 10000 });
  await page.screenshot({ path: "/home/claude/nearme/docs/screenshots/phase3-after-flag-spec-fix.png" });

  const reviewCountAfter = await page.locator("text=e2e_reviewer").count();
  console.log("Review by e2e_reviewer still visible after flagging (should be false):", reviewCountAfter === 1);

  await browser.close();
  console.log(
    reviewCountBefore === 1 && reviewCountAfter === 0
      ? "PASS: flag correctly hid the review immediately, matching the roadmap spec."
      : "FAIL: flag behavior does not match spec."
  );
})().catch((err) => {
  console.error("Flag-hides-review verification failed:", err);
  process.exit(1);
});
