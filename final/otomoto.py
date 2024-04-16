# utils 
from tqdm import tqdm 
import sys
import re
import dateparser
import pandas as pd

# bs4
import requests
from bs4 import BeautifulSoup


# loading links
print('Getting links')
links = pd.read_csv('links.csv')
links = links[links['otomoto']==1]['link'].tolist()

# scraping data
print(f'Scraping {len(links)} ads')
df=pd.DataFrame(columns=['title','price','location','seller_type','seller_name','date','image','link'])
error_count = 0
for link in tqdm(links):
    webpage_html=requests.get(link)
    if webpage_html.status_code == 200:
        try:
            soup = BeautifulSoup(webpage_html.text, 'html.parser')
            data_dict={}

            data_dict['title'] = soup.find('h3', class_='offer-title big-text ezl3qpx2 ooa-ebtemw er34gjf0').text

            data_dict['price'] = int(soup.find('h3', class_='offer-price__number eqdspoq4 ooa-o7wv9s er34gjf0').text.replace(' ', ''))

            data_dict['location'] = soup.find('a', attrs=   {
                                                            'href':'#map',
                                                            'class':'e1m6rqv1 ooa-lygf4m',
                                                            'color':'text-global-highlight'
                                                            }).text
            data_dict['location'] = re.search(r'(?:^|\s)([^,\s]+)(?=,)', data_dict['location']).group(0)

            data_dict['seller_type'] = soup.find('p', class_='ooa-1v45bqa er34gjf0').text

            data_dict['seller_name'] = soup.find('p', class_='ern8z622 ooa-hlpbot er34gjf0').text

            data_dict['date'] = soup.find('p', class_='edazosu4 ooa-1afacld er34gjf0').text
            data_dict['date'] = dateparser.parse(data_dict['date'], settings= {
                                                                        'DATE_ORDER':'DMY',
                                                                        'DEFAULT_LANGUAGES':['pl']
                                                                        })
            data_dict['image'] = f"""'{soup.find('img', attrs={
                                                        'data-nimg':'1',
                                                        'decoding':'async',
                                                        'data-ot-ignore':'true'
                                                        })['srcset'].split(';', 1)[0]}'"""
            
            data_dict['link']=f"'{link}'"

            df_data_dict=pd.DataFrame([data_dict])
            df=pd.concat([df,df_data_dict], ignore_index=True)
            
        except Exception as e:
            print(f'\nError extracting data from {link}: {e}')
            error_count +=1
    else: 
        print(f'\nIncorrect response code to {link}')
        error_count += 1
if error_count>0: print(f'Failed to scrape {error_count} ads')

df['date']=df['date'].dt.date
df.to_csv('otomoto.csv', index=False)



