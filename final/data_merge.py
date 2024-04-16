import pandas as pd

olx_df = pd.read_csv('olx.csv')
otomoto_df = pd.read_csv('otomoto.csv')


olx_df['seller_type'] = 'Osoba prywatna'
olx_df = olx_df.rename(columns= {
                                'seller_username':'seller_name',
                                'image_links':'image'
                                })
otomoto_df = otomoto_df.rename(columns= {
                                        'date':'posted_date'
                                        })

df = pd.concat([olx_df,otomoto_df])
df.to_csv('result.csv', index=False)

