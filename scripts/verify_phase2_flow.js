const { chromium } = require("/home/claude/.npm-global/lib/node_modules/playwright");

const CHROME_PATH = "/home/claude/.cache/puppeteer/chrome/linux-131.0.6778.204/chrome-linux64/chrome";

(async () => {
  const browser = await chromium.launch({ executablePath: CHROME_PATH, args: ["--no-sandbox"] });
  const page = await browser.newPage({ viewport: { width: 375, height: 900 } });

  await page.goto("http://localhost:5173/register", { waitUntil: "networkidle" });
  await page.getByLabel("Username").fill("e2e_owner");
  await page.getByLabel("Email").fill("e2e_owner@example.com");
  await page.getByLabel("Password").fill("a-strong-password-123");
  await page.getByLabel("I am a\u2026").selectOption("business_owner");
  await page.screenshot({ path: "/home/claude/nearme/docs/screenshots/phase2-register.png" });
  await page.click('button[type="submit"]');
  await page.waitForURL("http://localhost:5173/", { timeout: 10000 });
  await page.waitForTimeout(500);

  await page.click("a[href^='/business/']");
  await page.waitForTimeout(500);
  await page.screenshot({ path: "/home/claude/nearme/docs/screenshots/phase2-profile-with-claim-button.png" });
  await page.click('button:has-text("Claim this business")');
  await page.waitForSelector('text=Claim submitted', { timeout: 10000 });
  await page.screenshot({ path: "/home/claude/nearme/docs/screenshots/phase2-claim-submitted.png" });

  await browser.close();
  console.log("Step 1 done: registered, viewed profile, submitted claim.");
})().catch((err) => {
  console.error("Phase 2 E2E script (step 1) failed:", err);
  process.exit(1);
});
