const { chromium } = require("/home/claude/.npm-global/lib/node_modules/playwright");

const CHROME_PATH = "/home/claude/.cache/puppeteer/chrome/linux-131.0.6778.204/chrome-linux64/chrome";

(async () => {
  const browser = await chromium.launch({ executablePath: CHROME_PATH, args: ["--no-sandbox"] });
  const page = await browser.newPage({ viewport: { width: 375, height: 900 } });

  // Search results should now show the rating on Better Days Café's card
  await page.goto("http://localhost:5173/", { waitUntil: "networkidle" });
  await page.waitForTimeout(800);
  await page.screenshot({ path: "/home/claude/nearme/docs/screenshots/phase3-search-with-rating.png" });

  // Register a second user to test flagging someone else's review
  await page.goto("http://localhost:5173/register", { waitUntil: "networkidle" });
  await page.getByLabel("Username").fill("e2e_flagger");
  await page.getByLabel("Email").fill("e2e_flagger@example.com");
  await page.getByLabel("Password").fill("a-strong-password-123");
  await page.click('button[type="submit"]');
  await page.waitForURL("http://localhost:5173/", { timeout: 10000 });

  await page.click("a[href^='/business/']");
  await page.waitForSelector("text=Reviews", { timeout: 10000 });
  await page.click('button[aria-label="Report this review"]');
  await page.waitForTimeout(500);
  await page.screenshot({ path: "/home/claude/nearme/docs/screenshots/phase3-review-flagged.png" });

  await browser.close();
  console.log("Step 2 done: search shows rating, flagged a review as a different user.");
})().catch((err) => {
  console.error("Phase 3 E2E script (step 2) failed:", err);
  process.exit(1);
});
