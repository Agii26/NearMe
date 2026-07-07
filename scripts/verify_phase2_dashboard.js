const { chromium } = require("/home/claude/.npm-global/lib/node_modules/playwright");

const CHROME_PATH = "/home/claude/.cache/puppeteer/chrome/linux-131.0.6778.204/chrome-linux64/chrome";

(async () => {
  const browser = await chromium.launch({ executablePath: CHROME_PATH, args: ["--no-sandbox"] });
  const page = await browser.newPage({ viewport: { width: 375, height: 900 } });

  await page.goto("http://localhost:5173/login", { waitUntil: "networkidle" });
  await page.getByLabel("Username").fill("e2e_owner");
  await page.getByLabel("Password").fill("a-strong-password-123");
  await page.click('button[type="submit"]');
  await page.waitForURL("http://localhost:5173/", { timeout: 10000 });

  await page.goto("http://localhost:5173/dashboard", { waitUntil: "networkidle" });
  await page.waitForSelector("text=Better Days Café", { timeout: 10000 });
  await page.screenshot({ path: "/home/claude/nearme/docs/screenshots/phase2-dashboard.png" });

  await page.click('button:has-text("Edit")');
  await page.waitForSelector('text=Contact phone', { timeout: 5000 });
  await page.screenshot({ path: "/home/claude/nearme/docs/screenshots/phase2-dashboard-edit-open.png" });

  await page.getByLabel("Contact phone").fill("0917 999 8888");

  const testImagePath = "/home/claude/nearme/docs/screenshots/search-light.png";
  await page.setInputFiles('input[type="file"]', testImagePath);
  await page.waitForTimeout(1500);

  await page.click('button:has-text("Save changes")');
  await page.waitForSelector("text=Saved", { timeout: 10000 });
  await page.screenshot({ path: "/home/claude/nearme/docs/screenshots/phase2-dashboard-saved.png" });

  await browser.close();
  console.log("Step 2 done: logged in, viewed dashboard, edited business, uploaded photo, saved.");
})().catch((err) => {
  console.error("Phase 2 E2E script (step 2) failed:", err);
  process.exit(1);
});
