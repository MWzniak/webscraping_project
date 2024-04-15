# utils 
import json
from tqdm import tqdm 
import sys
import re

# data manipulation
import numpy as np
import pandas as pd

# selenium
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

# loading config
print('Loading config.json')
with open('config.json', 'r') as f:
    config = json.load(f)

chromepath = ChromeDriverManager().install() # Chrome driver install

# setting up Chrome
print('Setting up Chrome driver')
service_chrome = Service(executable_path = chromepath) 
options_chrome = webdriver.ChromeOptions()

# setting process visibility
if not config["visible_browsing"]:
    options_chrome.add_argument('--headless')

# removing unneccesary features to speed up the process
options_chrome.add_argument('--no-sandbox')
options_chrome.add_argument('--disable-gpu')
options_chrome.add_argument('--disable-notifications')
options_chrome.add_argument('--disable-infobars')
options_chrome.add_argument('--disable-extensions')
options_chrome.add_argument('--disable-web-security')

# keeping the logs clean
options_chrome.add_argument('--log-level=3')
options_chrome.add_argument("--ignore-certificate-error")
options_chrome.add_argument("--ignore-ssl-errors")

# calling Chrome driver
driver_chrome = webdriver.Chrome(service=service_chrome, options=options_chrome)

# opening the OLX page with selected filters
print('Opening initial OLX page')
driver_chrome.get(config['link'])

# accepting cookies
cookies_xpath = '//*[@id="onetrust-accept-btn-handler"]'
WebDriverWait(driver_chrome, 30).until(EC.visibility_of_element_located((By.XPATH, cookies_xpath)))
driver_chrome.find_element('xpath', cookies_xpath).click()

#<span data-testid="total-count">Znaleźliśmy  155 ogłoszeń</span>
# getting links to all pages
elements_page = driver_chrome.find_elements('xpath', '//a[starts-with(@data-testid,"pagination-link-")]')
page_count = int(elements_page[3].text)
ad_count = driver_chrome.find_element('xpath', '/html[1]/body[1]/div[1]/div[2]/div[3]/form[1]/div[4]/div[2]/span[1]/span[1]')
ad_count = re.findall('\s(\d+)\s',ad_count.text)[0]
links_page = [config['link'].replace('?', f'?page={i}&', 1) for i in range(1,page_count+1)]
print(f'{ad_count} ads available on {page_count} pages')

# getting links to ads on each page
xpath_ad_olx = '//a[@class="css-z3gu2d" and starts-with(@href,"/d/oferta")]'
xpath_ad_otomoto = '//a[@class="css-z3gu2d" and starts-with(@href,"https://www.otomoto.pl/")]'
links_ad = []
if config['limit']>0:
    for page in tqdm(links_page):
        if links_page.index(page)!=0: # no need to enter the first page since it is already open
            driver_chrome.get(page)
        WebDriverWait(driver_chrome, 30).until(EC.visibility_of_element_located((By.XPATH, xpath_ad_olx)))
        elements_ad = driver_chrome.find_elements('xpath', xpath_ad_olx)
        elements_ad.extend(driver_chrome.find_elements('xpath', xpath_ad_otomoto))
        elements_ad = [element for element in elements_ad if elements_ad.index(element)%2==0] # each ad is going in twice - removing them early
        for element in elements_ad: # getting only the specified amount of unique links
            link = element.get_attribute('href')
            if len(links_ad)<config['limit']:
                if link not in links_ad:
                    links_ad.append(link)
            else: break
        if len(links_ad)==config['limit']: break
    print(f'Scraped first {config["limit"]} unique links')
            
else:
    for page in tqdm(links_page):
        if links_page.index(page)!=0: # no need to enter the first page since it is already open
            driver_chrome.get(page)
        WebDriverWait(driver_chrome, 30).until(EC.visibility_of_element_located((By.XPATH, xpath_ad_olx)))
        elements_ad = driver_chrome.find_elements('xpath', xpath_ad_olx)
        elements_ad.extend(driver_chrome.find_elements('xpath', xpath_ad_otomoto))
        elements_ad = [element for element in elements_ad if elements_ad.index(element)%2==0]
        for element in elements_ad:
            links_ad.append(element.get_attribute('href'))
    links_ad = list(set(links_ad)) # removing duplicates

# saving links to a .csv file
link_arr = np.array(links_ad)
link_type = np.char.startswith(link_arr,'t',13,14) # identifying otomoto links
link_type = np.where(link_type,1,0)
df = pd.DataFrame()
df['link'] = link_arr
df['otomoto'] = link_type
df.to_csv('links.csv', index=False)
print('Results saved to links.csv')
