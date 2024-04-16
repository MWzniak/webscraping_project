# Required libraries
import requests
import re
from bs4 import BeautifulSoup
import os 
from scrapy.selector import Selector
import pandas as pd
import dateparser

# Load links form file and check
links_file = 'links.csv'

# Function to extract data using Lambda and regex
def extract_data(data, pattern):
    result = re.search(pattern, data)
    return result.group(1) if result else "Not found."

if os.path.exists(links_file):
    links_df = pd.read_csv(links_file)
    olx_links_df = links_df[links_df['otomoto'] == 0]
    olx_links = olx_links_df['link'].tolist()
    extracted_data = []

    # Extracting data
    for link in olx_links:
        try:
            response = requests.get(link)
            if response.status_code == 200:
                # Parse HTML using BeautifulSoup
                soup = BeautifulSoup(response.text, 'html.parser')

                # Parse HTML using Scrapy Selelctor
                selector = Selector(text=response.text)

                # Title extraction (BeautifulSoup) 
                ad_title_div = soup.find('div',attrs={'data-cy': 'ad_title'})
                ad_title = ad_title_div.h4.text.strip() if ad_title_div else "Title not found."

                # Price extraction using Scrapy selector
                price = selector.css('div[data-testid="ad-price-container"] h3::text').get().strip() if selector.css('div[data-testid="ad-price-container"] h3::text').get() else "Price not found."
                price = int(price[:-3].replace(' ',''))

                # Date extraction using Lambda function and Regex
                posted_date = soup.find('span',class_='css-fscvqi er34gjf0').text.strip()
                posted_date = extract_data(posted_date, r'(\d+\s+\w+\s+\d+)')
                posted_date = dateparser.parse(posted_date, settings=   {
                                                                        'DATE_ORDER':'DMY',
                                                                        'DEFAULT_LANGUAGES':['pl']
                                                                        })

                # Extracting image link - scrapy
                image_link = selector.css('div.swiper-slide img::attr(src)').get()
                    
                # Location extraction - lambda function
                location = soup.find_all('p', class_='css-1w88feb er34gjf0')[1].text.strip() if soup.find_all('p', class_='css-1w88feb er34gjf0') else "Location not found"

                #Extracting seller name using BS.
                seller_div = soup.find('h4', class_='css-1lcz6o7 er34gjf0')
                if seller_div:
                    seller_username = seller_div.text.strip()
                else:
                    seller_username = "Seller username not found"
                extracted_data.append({
                    'title': ad_title,
                    'price': price,
                    'posted_date': posted_date,
                    'location': location,
                    'seller_username': seller_username,
                    'image_links': f"'{image_link}'",
                    'link': f"'{link}'"
                })
        except Exception as e:
            print(f"Error extracting data from {link}: {e}")

    #saving the data
    extracted_df = pd.DataFrame(extracted_data)
    extracted_df['posted_date'] = extracted_df['posted_date'].dt.date
    output_file = 'olx.csv'
    extracted_df.to_csv(output_file, index=False)
    print(f"Extacted data saved to {output_file}.")   
else:
    print(f"File {links_file} not found.")


            

        
    

