import time
import json
import re
import random

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from webdriver_manager.chrome import ChromeDriverManager
from tqdm import tqdm


# -------- lazy sleep --------
def lazy_sleep(a=2,b=4):
    time.sleep(random.uniform(a,b))


# -------- keywords --------
keywords = [

"restaurants in United Kingdom",
"hotels in United Kingdom",
"hospitals in United Kingdom",
"police stations in United Kingdom",
"railway stations in United Kingdom",
"bus stations in United Kingdom",
"airports in United Kingdom",
"universities in United Kingdom",
"shopping malls in United Kingdom",

"restaurants in Qatar",
"hotels in Qatar",
"hospitals in Qatar",
"police stations in Qatar",
"railway stations in Qatar",
"bus stations in Qatar",
"airports in Qatar",
"universities in Qatar",
"shopping malls in Qatar"

]


data=[]


# -------- extract coordinates --------
def get_lat_lon(url):

    match = re.search(r'@(-?\d+\.\d+),(-?\d+\.\d+)',url)

    if match:
        return match.group(1),match.group(2)

    return None,None


# -------- start browser --------
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

wait = WebDriverWait(driver,20)


# -------- main loop --------
for keyword in keywords:

    print("\nSearching:",keyword)

    search_url = "https://www.google.com/maps/search/" + keyword.replace(" ","+")

    driver.get(search_url)

    lazy_sleep(6,8)


    # wait for results panel
    try:
        panel = wait.until(
            EC.presence_of_element_located((By.XPATH,'//div[@role="feed"]'))
        )
    except:
        print("Results panel not found")
        continue


    # scroll results
    for i in range(8):

        driver.execute_script(
            "arguments[0].scrollTop = arguments[0].scrollHeight",
            panel
        )

        lazy_sleep(2,3)


    places = driver.find_elements(By.XPATH,'//a[contains(@href,"/maps/place")]')

    print("Places found:",len(places))


    # scrape each place
    for place in tqdm(places[:30]):

        try:

            driver.execute_script("arguments[0].click();",place)

            lazy_sleep(4,6)

            name=None
            try:
                name = driver.find_element(By.XPATH,'//h1[contains(@class,"DUwDvf")]').text
            except:
                pass

            if not name or name.lower()=="results":
                continue

            url = driver.current_url

            lat,lon = get_lat_lon(url)


            address=None
            try:
                address = driver.find_element(By.XPATH,'//button[@data-item-id="address"]').text
            except:
                pass


            phone=None
            try:
                phone = driver.find_element(By.XPATH,'//button[contains(@data-item-id,"phone")]').text
            except:
                pass


            website=None
            try:
                website = driver.find_element(By.XPATH,'//a[contains(@data-item-id,"authority")]').get_attribute("href")
            except:
                pass


            reviews=None
            try:
                reviews = driver.find_element(By.XPATH,'//span[@role="img"]').get_attribute("aria-label")
            except:
                pass


            price=None
            try:
                price = driver.find_element(By.XPATH,'//span[contains(text(),"£") or contains(text(),"$")]').text
            except:
                pass


            images=[]
            try:
                img_elements = driver.find_elements(By.XPATH,'//img[contains(@src,"googleusercontent")]')
                for img in img_elements[:5]:
                    src = img.get_attribute("src")
                    if src:
                        images.append(src)
            except:
                pass


            item={

                "keyword":keyword,
                "name":name,
                "address":address,
                "phone":phone,
                "website":website,
                "latitude":lat,
                "longitude":lon,
                "reviews":reviews,
                "price":price,
                "images":images

            }

            print("Scraped:",name)

            data.append(item)

        except:
            pass


driver.quit()


# -------- save json --------
with open("places.json","w",encoding="utf-8") as f:

    json.dump(data,f,indent=2)

print("\nSaved dataset → places.json")