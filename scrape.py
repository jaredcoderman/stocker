import requests
from db import *
from datetime import datetime
import time
from bs4 import BeautifulSoup

# Send an HTTP GET request to the URL

session = requests.Session()
my_headers = {"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OSX 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36", 
          "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8"}

def get_current_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

while True:
  stock_data = []
  print("Scraping...\n")
  for i in range(0, 37):
    url = f'https://finviz.com/screener.ashx?v=111&f=cap_largeover'
        
    if i > 0:
      url += f"&r={1 + (20*i)}"

    response = session.get(url, headers=my_headers)
    if response.status_code == 200:
      soup = BeautifulSoup(response.text, 'html.parser')
      # Example: Extract and print the titles of the table rows
      rows = list(soup.find_all('tr', class_="styled-row is-hoverable is-bordered is-rounded is-striped has-color-text"))
      for row in rows:
        tds = row.find_all('td')
        stock = []
        for td in tds:
          stock.append(td.get_text(strip=True))
        important_data = [stock[1], stock[2], stock[8]]
        stock_data.append(important_data)
    else:
      print(f"Request to {url} failed with status code {response.status_code}.")

    print(f"Page {i + 1} / 37")
    time.sleep(.5)

#   Create Stocks
#   for x in range(len(stock_data)):
#     row = stock_data[x]
#     create_stock(row[0], row[1])
#     print(f"Created {x + 1}/{len(stock_data)}")
#   break

#   Update stocks
  query_stock_data = []
  time_stamp = get_current_timestamp()
  print("Prepping data for query...")
  for stock in stock_data:
    query_stock_data.append((stock[0], float(stock[2]), time_stamp))
  add_prices(query_stock_data)
  print("Prices updated!")
  break


