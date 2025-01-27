import re
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def configure_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--remote-debugging-port=9222")
    
    options.binary_location = "/opt/google-chrome/chrome"

    service = Service("/usr/local/bin/chromedriver")
    
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_page_load_timeout(60)
    return driver

def extract_contacts(page_source):
    email_regex = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    phone_regex = r"\b(?:\+7|7|8|375|374|380|996|992|994|995|993|998|373|371|372)\d{7,10}\b"
    emails = re.findall(email_regex, page_source)
    std_phones = re.findall(phone_regex, page_source)
    return {
        "emails": list(set(emails)), 
        "phones": list(set(std_phones))
    }

def crawl_domain(driver, domain, max_pages=20):
    visited = set()
    to_visit = [domain]
    contact_info = {"emails": [], "phones": []}
    
    while to_visit and len(visited) < max_pages:
        url = to_visit.pop(0)
        if url in visited:
            continue
        
        try:
            driver.get(url)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            time.sleep(2)
            
            page_source = driver.page_source
            contacts = extract_contacts(page_source)
            contact_info["emails"].extend(contacts["emails"])
            contact_info["phones"].extend(contacts["phones"])
            # print(url, "\n", contact_info["emails"], "\n", contact_info["phones"])
            
            links = driver.find_elements(By.TAG_NAME, "a")
            for link in links:
                href = link.get_attribute("href")
                if href and href.startswith(domain) and href not in visited:
                    to_visit.append(href)
            
            visited.add(url)
        except Exception as e:
            visited.add(url)
            print(f"Error processing {url}: {e}")
    
    contact_info["emails"] = list(set(contact_info["emails"]))
    contact_info["phones"] = list(set(contact_info["phones"]))
    return contact_info

def main(domains):
    driver = configure_driver()
    results = {}
    
    try:
        for domain in domains:
            if not domain.startswith("http"):
                domain = f"https://{domain}"
            print(f"Processing {domain}...")
            results[domain] = crawl_domain(driver, domain)
    finally:
        driver.quit()
    
    return results

if __name__ == "__main__":
    with open("domains.txt", "rt") as domain_file:
        domain_list = domain_file.read().split("\n")
    extracted_data = main(domains=domain_list)
    
    with open("extracted_data.json", "w") as json_file:
        json.dump(extracted_data, json_file, indent=4)

   
