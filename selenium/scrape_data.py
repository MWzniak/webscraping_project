#required libraries
import requests
import re
from bs4 import BeautifulSoup
import os 
import json
import pandas as pd

#Load links form file and check
links_file = 'links.csv'

if os.path.exists(links_file):
    links_df = pd.read_csv(links_file)
    olx_links_df = links_df[links_df['otomoto'] == 0]
    olx_links = olx_links_df['link'].tolist()
    extracted_data = []

    #Extracting data
    for link in olx_links:
        try:
            response = requests.get(link)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                #title extraction : 
                ad_title_div = soup.find('div',attrs={'data-cy': 'ad_title'})
                if ad_title_div:
                    ad_title = ad_title_div.h4.text.strip()
                    print("Ad Title:", ad_title)
                else:
                    print("Ad title not found.")
                price_div = soup.find('div', attrs={'data-testid': 'ad-price-container'})
                if price_div:
                    price = price_div.find('h3').text.strip()
                else:
                    price = "Price not found."
                date_span = soup.find('span',class_='css-fscvqi er34gjf0')
                if date_span:
                    posted_date = date_span.find('span', class_='css-19yf5ek').text.strip()
                else:
                    posted_date = "Date not found."
                image_links = []
                swiper_slides = soup.find_all('div', class_='swiper-slide css-1915wzc')
                for slide in swiper_slides:
                    img_tag = slide.find('img', attrs={'data-testid': 'swiper-image'})
                    if img_tag:
                        image_links.append(img_tag['src'])
                location_div = soup.find('p',class_='css-1w88feb er34gjf0')
                if location_div:
                    location = location_div.text.strip()
                else:
                    location = "Location not found"
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
                    'image_links': image_links,
                    'link': link   
                })
        except Exception as e:
            print(f"Error extracting data from {link}: {e}")

    #saving the data
    extracted_df = pd.DataFrame(extracted_data)
    output_file = 'extracted_data.csv'
    extracted_df.to_csv(output_file, index=False)
    print(f"Extacted data saved to {output_file}.")   
else:
    print(f"File {links_file} not found.")


            

        
    

