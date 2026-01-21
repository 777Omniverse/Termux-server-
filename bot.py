import time, os, threading
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

running = False

def start_bot(cookies, uid, messages, speed):
    global running
    running = True

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.binary_location = os.getenv("CHROME_BIN")

    service = Service(os.getenv("CHROMEDRIVER_PATH"))
    driver = webdriver.Chrome(service=service, options=options)

    driver.get("https://www.facebook.com")
    time.sleep(3)

    for pair in cookies.split(";"):
        if "=" in pair:
            k, v = pair.strip().split("=", 1)
            driver.add_cookie({
                "name": k,
                "value": v,
                "domain": ".facebook.com",
                "path": "/"
            })

    driver.refresh()
    time.sleep(5)

    driver.get(f"https://www.facebook.com/messages/t/{uid}")
    time.sleep(5)

    while running:
        for msg in messages:
            if not running:
                break
            try:
                box = driver.find_element(By.XPATH, "//div[@role='textbox']")
                box.send_keys(msg)
                box.send_keys(Keys.ENTER)
                time.sleep(speed)
            except:
                time.sleep(5)

    driver.quit()

def stop_bot():
    global running
    running = False
