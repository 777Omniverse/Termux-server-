import os
import time
import sys
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ---------- COLORS ----------
class Colors:
    RESET = '\033[0m'
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'

# ---------- HELPERS ----------
def log_ok(msg): print(f"{Colors.GREEN}✓ {msg}{Colors.RESET}")
def log_err(msg): print(f"{Colors.RED}✗ {msg}{Colors.RESET}")
def log_info(msg): print(f"{Colors.BLUE}ℹ {msg}{Colors.RESET}")
def log_warn(msg): print(f"{Colors.YELLOW}⚠ {msg}{Colors.RESET}")

# ---------- BOT ----------
class FacebookMessenger:

    def __init__(self):
        self.driver = None
        self.wait = None
        self.messages = []
        self.speed = int(os.getenv("SPEED", "10"))
        self.target_uid = os.getenv("TARGET_UID")
        self.cookies = os.getenv("FB_COOKIES")

    # ---- DRIVER ----
    def setup_driver(self):
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless=new")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.binary_location = os.getenv("CHROME_BIN")

            service = Service(os.getenv("CHROMEDRIVER_PATH"))

            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.wait = WebDriverWait(self.driver, 30)

            log_ok("Chrome started")
            return True
        except Exception as e:
            log_err(f"Driver error: {e}")
            return False

    # ---- COOKIES ----
    def load_cookies(self):
        self.driver.get("https://www.facebook.com")
        time.sleep(3)

        for pair in self.cookies.split(";"):
            if "=" in pair:
                name, value = pair.strip().split("=", 1)
                self.driver.add_cookie({
                    "name": name,
                    "value": value,
                    "domain": ".facebook.com",
                    "path": "/"
                })

        self.driver.refresh()
        time.sleep(5)

        if "facebook.com" in self.driver.current_url:
            log_ok("Login successful")
            return True

        log_err("Login failed")
        return False

    # ---- LOAD MESSAGES ----
    def load_messages(self):
        if not os.path.exists("messages.txt"):
            log_err("messages.txt not found")
            return False

        with open("messages.txt", "r", encoding="utf-8") as f:
            self.messages = [x.strip() for x in f if x.strip()]

        log_ok(f"{len(self.messages)} messages loaded")
        return True

    # ---- SEND MESSAGE ----
    def send_message(self, text):
        try:
            box = self.wait.until(EC.presence_of_element_located(
                (By.XPATH, "//div[@role='textbox']")
            ))
            box.click()
            box.send_keys(text)
            box.send_keys(Keys.ENTER)
            return True
        except:
            return False

    # ---- START ----
    def start(self):
        if not self.cookies or not self.target_uid:
            log_err("ENV variables missing")
            return

        if not self.setup_driver():
            return

        if not self.load_messages():
            return

        if not self.load_cookies():
            return

        self.driver.get(f"https://www.facebook.com/messages/t/{self.target_uid}")
        time.sleep(5)

        count = 0
        while True:
            for msg in self.messages:
                ok = self.send_message(msg)
                count += 1
                now = datetime.now().strftime("%H:%M:%S")

                if ok:
                    log_ok(f"[{now}] Sent #{count}")
                else:
                    log_err(f"[{now}] Failed")

                time.sleep(self.speed)

# ---------- RUN ----------
if __name__ == "__main__":
    bot = FacebookMessenger()
    bot.start()
