import os
import time
import json
from seleniumwire import webdriver  # For request interception if needed
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager

def load_tokens(filename="data.txt"):
    """Load Bearer tokens from a file."""
    try:
        with open(filename, "r") as file:
            tokens = [line.strip() for line in file if line.strip()]
            return tokens
    except FileNotFoundError:
        return []

# === Step 1: Load Bearer Token ===
# In production, you can load from an environment variable (e.g., os.getenv('BEARER_TOKEN'))
# For this example, we use the token provided earlier:
# Bearer token:
# "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyIjp7ImlkIjoiYzA5YTE2MGMtNTFmMC00MjdiLTkxMzktNGQwZDdmYWNhMWU5IiwiZmlyc3RfbmFtZSI6IuawlERBUlRPTuS5iCIsImxhbmd1YWdlX2NvZGUiOiJlbiIsInVzZXJuYW1lIjoiRGFydG9uVFYifSwic2Vzc2lvbl9pZCI6MTQzNzI1NCwic3ViIjoiYzA5YTE2MGMtNTFmMC00MjdiLTkxMzktNGQwZDdmYWNhMWU5IiwiZXhwIjoxNzQyOTc4MjUzfQ.f_0ScBVxthVpykNsiFI-QCqxDxhaxioVqq3PXtyG_Iw"
tokens = load_tokens()
if not tokens:
    raise Exception("No tokens available in data.txt")
# Use the first token (without the "Bearer " prefix, which we'll add when needed)
bearer_token = tokens[0]

# === Step 2: Verify User Balance ===
headers = {
    "authorization": f"Bearer {bearer_token}",
    "content-type": "application/json",
    "user-agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36"
}
progress_api_url = "https://gold-eagle-api.fly.dev/user/me/progress"
user_data_loaded = False
for i in range(30):
    try:
        response =  __import__('requests').get(progress_api_url, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            coins = data.get("coins_amount", 0)
            print("[+] User coins:", coins)
            user_data_loaded = True
            break
    except Exception as e:
        print("Error polling API:", e)
    time.sleep(1)

if not user_data_loaded:
    raise Exception("User data not loaded; exiting.")

# === Step 3: Set Up Selenium with Mobile Emulation ===
# Use mobile emulation matching Kiwi
mobile_emulation = {
    "deviceMetrics": {"width": 360, "height": 640, "pixelRatio": 3.0},
    "userAgent": ("Mozilla/5.0 (Linux; Android 10; SM-G973F) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 "
                  "Mobile Safari/537.36")
}
chrome_options = Options()
chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
chrome_options.add_argument("--headless")  # Remove for debugging
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# Attach the Bearer token to all requests using Chrome DevTools Protocol.
driver.execute_cdp_cmd('Network.setExtraHTTPHeaders', {"headers": {"Authorization": f"Bearer {bearer_token}"}})

# === Step 4: Load the Full Mini-App URL with Initialization Parameters ===
# Use the URL captured from your Kiwi session; here is an example:
mini_app_url = ("https://telegram.geagle.online/#"
                "tgWebAppData=query_id=AAG8XExdAAAAALxcTF0fzld9&"
                "tgWebAppThemeParams=%7B%22bg_color%22%3A%22%23212121%22%2C%22button_color%22%3A%22%238774e1%22%2C%22button_text_color%22%3A%22%23ffffff%22%2C%22hint_color%22%3A%22%23aaaaaa%22%2C%22link_color%22%3A%22%238774e1%22%2C%22secondary_bg_color%22%3A%22%23181818%22%2C%22text_color%22%3A%22%23ffffff%22%2C%22header_bg_color%22%3A%22%23212121%22%2C%22accent_text_color%22%3A%22%238774e1%22%2C%22section_bg_color%22%3A%22%23212121%22%2C%22section_header_text_color%22%3A%22%238774e1%22%2C%22subtitle_text_color%22%3A%22%23aaaaaa%22%2C%22destructive_text_color%22%3A%22%23ff595a%22%7D&"
                "tgWebAppVersion=7.10&"
                "tgWebAppPlatform=ios")
driver.get(mini_app_url)
time.sleep(5)  # Allow page to load

# === Step 5: Inject Telegram Initialization Data into the Page ===
init_params = {
    "tgWebAppData": "query_id=AAG8XExdAAAAALxcTF0fzld9&user=%7B%22id%22%3A1565285564%2C%22first_name%22%3A%22%E6%B0%94DARTON%E4%B9%88%22%2C%22last_name%22%3A%22%22%2C%22username%22%3A%22DartonTV%22%2C%22language_code%22%3A%22en%22%2C%22allows_write_to_pm%22%3Atrue%2C%22photo_url%22%3A%22https%3A//t.me/i/userpic/320/iy3Hp0CdIo6mZaYfi83EHd7h2nPyXG1Fd5V50-SkD2I.svg%22%7D",
    "tgWebAppVersion": "7.10",
    "tgWebAppPlatform": "ios",
    "tgWebAppThemeParams": "{\"bg_color\":\"#212121\",\"button_color\":\"#8774e1\",\"button_text_color\":\"#ffffff\",\"hint_color\":\"#aaaaaa\",\"link_color\":\"#8774e1\",\"secondary_bg_color\":\"#181818\",\"text_color\":\"#ffffff\",\"header_bg_color\":\"#212121\",\"accent_text_color\":\"#8774e1\",\"section_bg_color\":\"#212121\",\"section_header_text_color\":\"#8774e1\",\"subtitle_text_color\":\"#aaaaaa\",\"destructive_text_color\":\"#ff595a\"}"
}
driver.execute_script(f"""
    window.Telegram = window.Telegram || {{}};
    window.Telegram.WebApp = window.Telegram.WebApp || {{}};
    window.Telegram.WebApp.initParams = {json.dumps(init_params)};
    sessionStorage.setItem('__telegram__initParams', JSON.stringify({json.dumps(init_params)}));
""")
print("[+] Telegram initParams injected.")
time.sleep(2)

# === Step 6: Ensure External Telegram JS is Loaded ===
external_js_url = "https://telegram.geagle.online/assets/index-BC9KxTS7.js"
driver.execute_script(f"""
    var script = document.createElement('script');
    script.type = 'text/javascript';
    script.src = '{external_js_url}';
    document.head.appendChild(script);
""")
print("[+] External JS injected.")
time.sleep(5)

# === Step 7: Simulate Genuine UI Tap on the Coin Element ===
# Attempt to locate the coin element by a partial class name; adjust selector if needed.
try:
    coin_element = driver.find_element(By.XPATH, "//*[contains(@class, 'tapAreaContainer_')]")
    print("[+] Coin element found.")
except Exception as e:
    print("[-] Could not find coin element:", e)
    driver.get_screenshot_as_file("debug_coin.png")
    print("Screenshot saved as debug_coin.png")
    print(driver.page_source[:2000])
    driver.quit()
    exit()

def simulate_tap(element):
    # Use ActionChains to simulate a genuine tap event
    actions = ActionChains(driver)
    actions.move_to_element(element).click().perform()

# === Step 8: Loop to Simulate Batch Taps and Wait ===
# Instead of continuous rapid taps, this version sends a batch of 200 taps,
# then sleeps for 3 minutes before repeating.
batch_taps = 200
wait_between_batches = 180  # seconds (3 minutes)
cycles = 3  # Adjust the number of cycles as needed

for cycle in range(1, cycles + 1):
    print(f"[+] Starting cycle {cycle}: Sending {batch_taps} taps.")
    for i in range(batch_taps):
        simulate_tap(coin_element)
        time.sleep(0.05)  # Small delay between taps; adjust as necessary
    print(f"[+] Cycle {cycle} complete. Sleeping for {wait_between_batches} seconds...")
    time.sleep(wait_between_batches)

print("[+] Finished all cycles.")
driver.quit()
