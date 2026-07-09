const { chromium } = require("/home/claude/.npm-global/lib/node_modules/playwright");

const CHROME_PATH = "/home/claude/.cache/puppeteer/chrome/linux-131.0.6778.204/chrome-linux64/chrome";

(async () => {
  const browser = await chromium.launch({ executablePath: CHROME_PATH, args: ["--no-sandbox"] });
  const page = await browser.newPage({ viewport: { width: 375, height: 900 } });

  // Register a fresh consumer account
  await page.goto("http://localhost:5173/register", { waitUntil: "networkidle" });
  await page.getByLabel("Username").fill("e2e_reviewer");
  await page.getByLabel("Email").fill("e2e_reviewer@example.com");
  await page.getByLabel("Password").fill("a-strong-password-123");
  // role select left at default "consumer"
  await page.click('button[type="submit"]');
  await page.waitForURL("http://localhost:5173/", { timeout: 10000 });

  await page.click("a[href^='/business/']");
  await page.waitForSelector("text=Reviews", { timeout: 10000 });
  await page.screenshot({ path: "/home/claude/nearme/docs/screenshots/phase3-profile-before-review.png" });

  // Pick 4 stars and submit
  await page.click('button[aria-label="4 stars"]');
  await page.fill("textarea", "Great coffee, friendly staff.");
  await page.click('button:has-text("Post review")');
  await page.waitForSelector("text=Thanks", { timeout: 10000 });
  await page.waitForTimeout(300);
  await page.screenshot({ path: "/home/claude/nearme/docs/screenshots/phase3-profile-after-review.png" });

  await browser.close();
  console.log("Step 1 done: registered, viewed profile, submitted a review.");
})().catch((err) => {
  console.error("Phase 3 E2E script (step 1) failed:", err);
  process.exit(1);
});
