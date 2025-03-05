import os
import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
import requests

def load_tokens(filename="data.txt"):
    """Load Bearer tokens from a file."""
    try:
        with open(filename, "r") as file:
            tokens = [line.strip() for line in file if line.strip()]
            return tokens
    except FileNotFoundError:
        return []

# === Step 1: Load Bearer Token ===
# Using the token provided in our discussions:
# "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyIjp7ImlkIjoiYzA5YTE2MGMtNTFmMC00MjdiLTkxMzktNGQwZDdmYWNhMWU5IiwiZmlyc3RfbmFtZSI6IuawlERBUlRPTuS5iCIsImxhbmd1YWdlX2NvZGUiOiJlbiIsInVzZXJuYW1lIjoiRGFydG9uVFYifSwic2Vzc2lvbl9pZCI6MTQzNzI1NCwic3ViIjoiYzA5YTE2MGMtNTFmMC00MjdiLTkxMzktNGQwZDdmYWNhMWU5IiwiZXhwIjoxNzQyOTc4MjUzfQ.f_0ScBVxthVpykNsiFI-QCqxDxhaxioVqq3PXtyG_Iw
tokens = load_tokens()
if not tokens:
    raise Exception("No tokens available in data.txt")
bearer_token = tokens[0]

# === Step 2: Poll the API for User Balance ===
headers = {
    "authorization": f"Bearer {bearer_token}",
    "content-type": "application/json",
    "user-agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36"
}
progress_api_url = "https://gold-eagle-api.fly.dev/user/me/progress"
user_data_loaded = False
for i in range(30):
    try:
        response = requests.get(progress_api_url, headers=headers, timeout=5)
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
mobile_emulation = {
    "deviceMetrics": {"width": 360, "height": 640, "pixelRatio": 3.0},
    "userAgent": ("Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/83.0.4103.106 Mobile Safari/537.36")
}
chrome_options = Options()
chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
chrome_options.add_argument("--headless")  # Remove this for debugging if needed.
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)
# Attach the Authorization header via CDP so that all requests include it.
driver.execute_cdp_cmd('Network.setExtraHTTPHeaders', {"headers": {"Authorization": f"Bearer {bearer_token}"}})

# === Step 4: Load the Full Mini-App URL ===
# Use the full URL (with hash parameters) as captured from your Kiwi session.
mini_app_url = (
    "https://telegram.geagle.online/#"
    "tgWebAppData=query_id=AAG8XExdAAAAALxcTF2ALyef&"
    "tgWebAppThemeParams=%7B%22bg_color%22%3A%22%23212121%22%2C%22button_color%22%3A%22%238774e1%22%2C%22button_text_color%22%3A%22%23ffffff%22%2C%22hint_color%22%3A%22%23aaaaaa%22%2C%22link_color%22%3A%22%238774e1%22%2C%22secondary_bg_color%22%3A%22%23181818%22%2C%22text_color%22%3A%22%23ffffff%22%2C%22header_bg_color%22%3A%22%23212121%22%2C%22accent_text_color%22%3A%22%238774e1%22%2C%22section_bg_color%22%3A%22%23212121%22%2C%22section_header_text_color%22%3A%22%238774e1%22%2C%22subtitle_text_color%22%3A%22%23aaaaaa%22%2C%22destructive_text_color%22%3A%22%23ff595a%22%7D&"
    "tgWebAppVersion=7.10&"
    "tgWebAppPlatform=ios"
)
driver.get(mini_app_url)
time.sleep(5)

# === Step 5: Inject Session Storage Data from Kiwi ===
# The following values are taken from your session storage:
# - Key: tapps/launchParams
launch_params = (
    "tgWebAppPlatform=ios&tgWebAppThemeParams=%7B%22bg_color%22%3A%22%23212121%22%2C%22button_color%22%3A%22%238774e1%22%2C"
    "%22button_text_color%22%3A%22%23ffffff%22%2C%22hint_color%22%3A%22%23aaaaaa%22%2C%22link_color%22%3A%22%238774e1%22%2C"
    "%22secondary_bg_color%22%3A%22%23181818%22%2C%22text_color%22%3A%22%23ffffff%22%2C%22header_bg_color%22%3A%22%23212121%22%2C"
    "%22accent_text_color%22%3A%22%238774e1%22%2C%22section_bg_color%22%3A%22%23212121%22%2C%22section_header_text_color%22%3A%22%238774e1%22%2C"
    "%22subtitle_text_color%22%3A%22%23aaaaaa%22%2C%22destructive_text_color%22%3A%22%23ff595a%22%7D&tgWebAppVersion=7.10&"
    "tgWebAppData=query_id%3DAAG8XExdAAAAALxcTF2ALyef%26user%3D%257B%2522id%2522%253A1565285564%252C%2522first_name%2522%253A%2522%E6%B0%94DARTON%E4%B9%88%2522%252C%2522last_name%2522%253A%2522%2522%252C%2522username%2522%253A%2522DartonTV%2522%252C%2522language_code%2522%253A%2522en%2522%252C%2522allows_write_to_pm%2522%253Atrue%257D"
)

# __telegram__initParams value:
init_params_value = (
    '{"tgWebAppData":"query_id=AAG8XExdAAAAALxcTF2ALyef&user=%7B%22id%22%3A1565285564%2C%22first_name%22%3A%22%E6%B0%94DARTON%E4%B9%88%22%2C%22last_name%22%3A%22%22%2C%22username%22%3A%22DartonTV%22%2C%22language_code%22%3A%22en%22%2C%22allows_write_to_pm%22%3Atrue%2C%22photo_url%22%3A%22https://t.me/i/userpic/320/iy3Hp0CdIo6mZaYfi83EHd7h2nPyXG1Fd5V50-SkD2I.svg%22%7D",'
    '"auth_date":1741132592,'
    '"signature":"sGfdIFxIBcKtqrq2y6zzeUQNkypsglVlaN_LT8s1bp9EbnZVaNiSS7KapQx0llxh0IIjsx926e4oxpOyTPn5DA",'
    '"hash":"970af2cd5d4ce4b680996870cf21e9762f1d387f096cf9eb1b58366724741d42"}'
)

# __telegram__themeParams value:
theme_params_value = (
    '{"bg_color":"#212121","button_color":"#8774e1","button_text_color":"#ffffff",'
    '"hint_color":"#aaaaaa","link_color":"#8774e1","secondary_bg_color":"#181818",'
    '"text_color":"#ffffff","header_bg_color":"#212121","accent_text_color":"#8774e1",'
    '"section_bg_color":"#212121","section_header_text_color":"#8774e1","subtitle_text_color":"#aaaaaa",'
    '"destructive_text_color":"#ff595a"}'
)

driver.execute_script(f"""
    sessionStorage.setItem('tapps/launchParams', '{launch_params}');
    sessionStorage.setItem('__telegram__initParams', '{init_params_value}');
    sessionStorage.setItem('__telegram__themeParams', '{theme_params_value}');
""")
print("[+] Session storage values injected.")
time.sleep(2)

# === Step 6b: Ensure External Telegram JS is Loaded (if not auto-loaded) ===
external_js_url = "https://telegram.geagle.online/assets/index-BC9KxTS7.js"
driver.execute_script(f"""
    var script = document.createElement('script');
    script.type = 'text/javascript';
    script.src = '{external_js_url}';
    document.head.appendChild(script);
""")
print("[+] External JS injected.")
time.sleep(5)

# === Step 7: Locate the Coin Element ===
# We'll attempt to locate the coin element using an XPath that matches elements with a background image pointing to the coin.
try:
    coin_element = driver.find_element(By.XPATH, "//*[contains(@style, 'gold-eagle-coin.svg')]")
    print("[+] Coin element found.")
except Exception as e:
    print("[-] Could not find coin element:", e)
    driver.get_screenshot_as_file("debug_coin.png")
    print("Screenshot saved as debug_coin.png")
    print(driver.page_source[:2000])
    driver.quit()
    exit()

def simulate_tap(element):
    actions = ActionChains(driver)
    actions.move_to_element(element).click().perform()

# === Step 8: Loop to Simulate Batch Taps and Wait ===
batch_taps = 200
wait_between_batches = 180  # 3 minutes in seconds
cycles = 3  # Adjust cycles as needed

for cycle in range(1, cycles + 1):
    print(f"[+] Starting cycle {cycle}: Sending {batch_taps} taps.")
    for i in range(batch_taps):
        simulate_tap(coin_element)
        time.sleep(0.05)  # Small delay between taps
    print(f"[+] Cycle {cycle} complete. Sleeping for {wait_between_batches} seconds...")
    time.sleep(wait_between_batches)

print("[+] Finished all cycles.")
driver.quit()
