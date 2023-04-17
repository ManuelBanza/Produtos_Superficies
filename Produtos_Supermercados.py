import requests
import pandas as pd
from datetime import datetime, timedelta
import io
import urllib3
from urllib3.exceptions import InsecureRequestWarning

# Lista de produtos a pesquisar
SHEET_ID = '1ZGw9064Dj07dKZbKxFUNQVBYS9fDPWhbTLwE0pfjXK4'
SHEET_NAME = 'Folha1'
url = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}'
df = pd.read_csv(url)

keywords = df['Palavras a pesquisar'].to_list()

# Obter dados
# disable SSL certificate verification warnings
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

url = "https://content-api.prices-crawler.duckdns.org/api/v1/products/search"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/112.0",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "pt-PT,pt;q=0.8,en;q=0.5,en-US;q=0.3",
    "Accept-Encoding": "gzip, deflate, br",
    "Content-Type": "application/json",
    "Origin": "https://prices-crawler.vercel.app",
    "Connection": "keep-alive",
    "Referer": "https://prices-crawler.vercel.app/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "cross-site",
}

json_data = []

for keyword in keywords:
    data = {
        "catalogs": ["pt.auchan", "pt.continente", "pt.minipreco", "pt.pingo-doce"],
        "query": keyword,
    
    }

    response = requests.post(url, headers=headers, json=data, verify=False)

    if response.ok:
        response_data = response.json()
        # append a dictionary with the keyword value to json_data
        json_data.append({"keyword": keyword, "response": response_data})
    else:
        print(f"API request failed with status code {response.status_code}")


# define the columns for the dataframe
columns = ['keyword', 'locale', 'catalog', 'id', 'reference', 'name', 'regularPrice', 'campaignPrice', 'pricePerQuantity', 'quantity', 'brand', 'description', 'productUrl', 'imageUrl', 'eanUpcList', 'date', 'data']

# create an empty list to hold each row of data
data = []

for dictionary in json_data:
    response = dictionary['response']
    locale = response[0]['locale']
    for catalog_data in response:
        catalog = catalog_data['catalog']
        for product in catalog_data['products']:
            # add the relevant data to the 'data' list
            data.append([
                dictionary['keyword'], locale, catalog, product.get('id'), product.get('reference'), product.get('name'),
                product.get('regularPrice'), product.get('campaignPrice'), product.get('pricePerQuantity'), product.get('quantity'),
                product.get('brand'), product.get('description'), product.get('productUrl'), product.get('imageUrl'),
                product.get('eanUpcList'), product.get('date'), product.get('data')
            ])

# create the Pandas dataframe
df = pd.DataFrame(data, columns=columns)


# Get today date now to file name when export to csv or excel with encoding utf8
df.to_csv((datetime.now()+timedelta(hours=1)).strftime('data_sources/data_transformed/produtos_online_scrap-%Y-%m-%d.csv'), encoding='utf8', index=False)
