#required libraries
import requests
import re
from scrapy import Selector
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
                sel = Selector(text=response.text)
            #extracting title and price
            title = sel.xpath('//h1/text()').extract_first().strip()
            price = sel.xpath('//span[contains(text(), "Price:")]/following-sibling::span/text()').extract_first()
            price = re.sub(r'[^\d.]', '', price) if price else None
            price = float(price) if price else None

            extracted_data.append({
                'link': link , 
                'title': title,
                'price': price
            })
        except Exception as e:
            print(f"Error extracting data from {link}: {e}")

    #saving the data
    if extracted_data:
        output_file = 'extracted_data.json'
        with open(output_file, 'w') as f:
            json.dump(extracted_data, f, indent=4)
            print(f"Extracted data saved to {output_file}.")
    else:
        print("No data extracted.")
else:
    print(f"File {links_file} not found.")


            

        
    

