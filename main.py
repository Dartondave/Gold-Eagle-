import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

# Set up Chrome options for mobile emulation
mobile_emulation = {
    "deviceMetrics": {"width": 360, "height": 640, "pixelRatio": 3.0},
    "userAgent": "Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Mobile Safari/537.36"
}
chrome_options = Options()
chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")

# Load Bearer token securely from environment variable
bearer_token = os.getenv('BEARER_TOKEN')
if not bearer_token:
    raise EnvironmentError("Bearer token not found in environment variables")

# Set up the WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
driver.execute_cdp_cmd('Network.setExtraHTTPHeaders', {"headers": {"Authorization": f"Bearer {bearer_token}"}})

# Define the mini-app URL with initialization parameters
mini_app_url = "https://telegram.geagle.online/your-mini-app-url-with-hash-parameters"

# Open the mini-app URL
driver.get(mini_app_url)

# Inject initialization parameters into window.Telegram.WebApp and sessionStorage
init_script = """
window.Telegram = {
    WebApp: {
        initParams: {
            tgWebAppData: "your_tgWebAppData",
            tgWebAppThemeParams: "your_tgWebAppThemeParams",
            tgWebAppVersion: "your_tgWebAppVersion",
            tgWebAppPlatform: "your_tgWebAppPlatform"
        }
    }
};
sessionStorage.setItem('tgWebAppData', 'your_tgWebAppData');
sessionStorage.setItem('tgWebAppThemeParams', 'your_tgWebAppThemeParams');
sessionStorage.setItem('tgWebAppVersion', 'your_tgWebAppVersion');
sessionStorage.setItem('tgWebAppPlatform', 'your_tgWebAppPlatform');
"""
driver.execute_script(init_script)

# Verify that the external JS file is loaded or inject it manually
external_js_url = "https://telegram.geagle.online/assets/index-BC9KxTS7.js"
load_external_js = f"""
var script = document.createElement('script');
script.src = '{external_js_url}';
document.head.appendChild(script);
"""
driver.execute_script(load_external_js)

# Wait until the external JS file is fully loaded and initialization routines are complete
time.sleep(5)  # Adjust the sleep time as necessary

# Locate the tap area element by its class or style attribute
tap_area = driver.find_element(By.XPATH, "//*[contains(@class, 'tapAreaContainer_')]")

# Function to simulate a tap event
def simulate_tap(element):
    actions = ActionChains(driver)
    actions.move_to_element(element).click().perform()

# Loop to simulate 200 taps, wait 3 minutes, and repeat as needed
tap_count = 200
wait_time = 180  # 3 minutes in seconds

while True:
    for _ in range(tap_count):
        simulate_tap(tap_area)
        time.sleep(0.1)  # Small delay between taps to mimic natural behavior
    time.sleep(wait_time)

# Close the driver after use (if needed)
# driver.quit()
