import os
import time
import random
import string
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

class FullSystemAutomator:
    def __init__(self, target):
        self.target = target if target.startswith("http") else "http://" + target
        self.login_page = None
        self.session = requests.Session()
        
        # Identity for Registration
        self.user = "bot_" + ''.join(random.choices(string.ascii_lowercase, k=6))
        self.pwd = "ReplitSystem!123"
        self.email = f"{self.user}@mail7.io"

    def get_headless_driver(self):
        """Standard Replit Headless Configuration"""
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36')
        
        service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=options)

    def phase1_discover(self):
        """Scans for admin/login URLs"""
        print(f"[*] Phase 1: Scanning {self.target}...")
        common_paths = ['admin', 'login', 'administrator', 'wp-login.php', 'register', 'signup']
        for path in common_paths:
            url = f"{self.target}/{path}"
            try:
                r = self.session.get(url, timeout=5)
                if r.status_code == 200:
                    print(f"[+] Found Access Point: {url}")
                    self.login_page = url
                    return url
            except: continue
        self.login_page = self.target
        return self.target

    def phase2_audit(self, username, password):
        """Tests login credentials using Browser Automation"""
        print(f"[*] Phase 2: Auditing Login [{username}]...")
        driver = self.get_headless_driver()
        try:
            driver.get(self.login_page)
            time.sleep(4)
            
            # Universal Field Finder
            inputs = driver.find_elements(By.TAG_NAME, "input")
            for i in inputs:
                t = i.get_attribute("type")
                if t == "text" or t == "email":
                    i.send_keys(username)
                elif t == "password":
                    i.send_keys(password)
                    i.send_keys(Keys.RETURN)
                    break
            
            time.sleep(5)
            # Check for redirect or success text
            if "logout" in driver.page_source.lower() or "dashboard" in driver.page_source.lower():
                print(f"[!!!] LOGIN SUCCESS: {username}:{password}")
                return True
            print("[-] Login failed.")
        except Exception as e:
            print(f"[!] Audit Error: {e}")
        finally:
            driver.quit()
        return False

    def phase3_register(self):
        """Performs Auto-Registration"""
        print(f"[*] Phase 3: Attempting Registration on {self.target}...")
        driver = self.get_headless_driver()
        try:
            driver.get(self.target)
            time.sleep(3)
            # Try to find a link to registration
            try:
                reg_link = driver.find_element(By.PARTIAL_LINK_TEXT, "Register") or \
                           driver.find_element(By.PARTIAL_LINK_TEXT, "Sign Up")
                reg_link.click()
                time.sleep(3)
            except: pass # Already on registration or link not found
            
            # Auto-fill fields
            inputs = driver.find_elements(By.TAG_NAME, "input")
            for i in inputs:
                name = (i.get_attribute("name") or i.get_attribute("id") or "").lower()
                if "user" in name: i.send_keys(self.user)
                elif "mail" in name: i.send_keys(self.email)
                elif "pass" in name: i.send_keys(self.pwd)
            
            inputs[-1].send_keys(Keys.RETURN)
            time.sleep(5)
            print(f"[SUCCESS] Registered: {self.user} | {self.pwd}")
            with open("results.txt", "a") as f:
                f.write(f"SITE: {self.target} | CREDS: {self.user}:{self.pwd}\n")
        except Exception as e:
            print(f"[!] Registration Error: {e}")
        finally:
            driver.quit()

if __name__ == "__main__":
    print("=== REPLIT FULL SYSTEM READY ===")
    url_input = input("Target URL: ")
    bot = FullSystemAutomator(url_input)
    
    # Run the full sequence
    bot.phase1_discover()
    
    print("\nStarting Sequence...")
    # Attempt to register first
    bot.phase3_register()
    
    # Then attempt to audit a common password
    bot.phase2_audit("admin", "admin123")
    
    print("\n[*] All tasks finished. Results saved to results.txt")
