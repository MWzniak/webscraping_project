# utils 
import json

# selenium
import selenium
from selenium import webdriver
import time
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

# loading config
with open('config.json', 'r') as f:
    config = json.load(f)

chromepath = ChromeDriverManager().install() # Chrome driver install

# setting up Chrome
service_chrome = Service(executable_path = chromepath) 
options_chrome = webdriver.ChromeOptions()
#options_chrome.add_argument('--headless')
options_chrome.add_argument('--no-sandbox')
options_chrome.add_argument('--disable-gpu')
options_chrome.add_argument('--disable-notifications')
options_chrome.add_argument('--disable-infobars')
options_chrome.add_argument('--disable-extensions')
options_chrome.add_argument('--disable-web-security')
options_chrome.add_experimental_option('excludeSwitches', ['enable-logging'])

# calling Chrome driver
driver_chrome = webdriver.Chrome(service=service_chrome, options=options_chrome)

# opening the OLX page with selected filters
driver_chrome.get(config['link'])

# accepting cookies
cookies_xpath = '//*[@id="onetrust-accept-btn-handler"]'
WebDriverWait(driver_chrome, 30).until(EC.visibility_of_element_located((By.XPATH, cookies_xpath)))
driver_chrome.find_element('xpath', cookies_xpath).click()

# getting links to all pages
elements_page = driver_chrome.find_elements('xpath', '//a[starts-with(@data-testid,"pagination-link-")]')
links_page=[element.get_attribute('href') for element in elements_page]

# getting links to ads on each page
xpath_ad_olx='//a[@class="css-z3gu2d" and starts-with(@href,"/d/oferta")]'
xpath_ad_otomoto='//a[@class="css-z3gu2d" and starts-with(@href,"https://www.otomoto.pl/")]'
links_ad=[]
if config['limit']>0:
    for page in links_page:
        if links_page.index(page)!=0: # no need to enter the first page since it is already open
            driver_chrome.get(page)
        WebDriverWait(driver_chrome, 30).until(EC.visibility_of_element_located((By.XPATH, xpath_ad_olx)))
        elements_ad=driver_chrome.find_elements('xpath', xpath_ad_olx)
        elements_ad.extend(driver_chrome.find_elements('xpath', xpath_ad_otomoto))
        elements_ad=[element for element in elements_ad if elements_ad.index(element)%2==0] # each ad is going in twice - removing them early
        for element in elements_ad:
            link=element.get_attribute('href')
            if link not in links_ad and len(links_ad)<=config['limit']:
                links_ad.append(link)
else:
    for page in links_page:
        if links_page.index(page)!=0: # no need to enter the first page since it is already open
            driver_chrome.get(page)
        WebDriverWait(driver_chrome, 30).until(EC.visibility_of_element_located((By.XPATH, xpath_ad_olx)))
        elements_ad=driver_chrome.find_elements('xpath', xpath_ad_olx)
        elements_ad.extend(driver_chrome.find_elements('xpath', xpath_ad_otomoto))
        elements_ad=[element for element in elements_ad if elements_ad.index(element)%2==0]
        for element in elements_ad:
            links_ad.append(element.get_attribute('href'))
    links_ad=list(set(links_ad))

# saving links to a .txt file
with open("links.txt", 'w') as file:
    for link in links_ad:
        file.write(link + '\n')
