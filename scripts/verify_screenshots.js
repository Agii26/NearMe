const { chromium } = require("/home/claude/.npm-global/lib/node_modules/playwright");

const CHROME_PATH = "/home/claude/.cache/puppeteer/chrome/linux-131.0.6778.204/chrome-linux64/chrome";

(async () => {
  const browser = await chromium.launch({
    executablePath: CHROME_PATH,
    args: ["--no-sandbox"],
  });
  const page = await browser.newPage({ viewport: { width: 375, height: 850 } });

  await page.goto("http://localhost:5173/", { waitUntil: "networkidle" });
  await page.waitForTimeout(500);
  await page.screenshot({ path: "/home/claude/nearme/docs/screenshots/search-light.png" });

  // Map view toggle
  await page.click('button[aria-label="Switch to map view"]');
  await page.waitForTimeout(400);
  await page.screenshot({ path: "/home/claude/nearme/docs/screenshots/search-map-view.png" });
  await page.click('button[aria-label="Switch to list view"]');
  await page.waitForTimeout(300);

  // Toggle to dark mode via the theme button
  await page.click('button[aria-label="Switch to dark mode"]');
  await page.waitForTimeout(300);
  await page.screenshot({ path: "/home/claude/nearme/docs/screenshots/search-dark.png" });

  // Open the first business card to verify the profile page
  await page.click("a[href^='/business/']");
  await page.waitForTimeout(500);
  await page.screenshot({ path: "/home/claude/nearme/docs/screenshots/profile-dark.png" });

  await page.click('button[aria-label="Switch to light mode"]');
  await page.waitForTimeout(300);
  await page.screenshot({ path: "/home/claude/nearme/docs/screenshots/profile-light.png" });

  await browser.close();
  console.log("Screenshots captured successfully.");
})().catch((err) => {
  console.error("Screenshot script failed:", err);
  process.exit(1);
});
