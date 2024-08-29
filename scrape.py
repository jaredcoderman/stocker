import requests
import modal
from funcs.db import * 
from funcs.time_helpers import *
from StockList import *

import time
from bs4 import BeautifulSoup

# stub = modal.Stub("stock-scrape")

# funcs = modal.Mount.from_local_dir(
#     "~/side-projects/stocker-python/funcs",
#     condition=lambda pth: not ".venv" in pth,
#     remote_path="/root/funcs",
# )

# scrape_image = modal.Image.debian_slim(python_version="3.10").run_commands(
#     "apt-get update",
#     "apt-get install -y software-properties-common",
#     "apt-add-repository non-free",
#     "apt-add-repository contrib",
#     "apt-get update",
#     "apt-get install -y postgresql postgresql-contrib",
#     # "curl --create-dirs -o /root/.postgresql/root.crt 'https://cockroachlabs.cloud/clusters/d2319e21-fcdf-41ce-b515-7e6a529ed87c/cert'",
#     "pip install beautifulsoup4",
#     "pip install requests",
#     "pip install psycopg2-binary",
#     "pip install python-dotenv",
#     "pip install pytz"
# )


# # Send an HTTP GET request to the URL

session = requests.Session()
my_headers = {"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OSX 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36", 
          "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8"}

# Makes a historical_price for every hour
def make_historical_prices():
  print("Getting historical prices...")
  hourly_prices = get_all_hourly_prices_for_all_tickers()
  formatted_hourly_prices = []
  for historical_price in hourly_prices:
    formatted_hourly_prices.append((historical_price[1], historical_price[2], historical_price[3]))
  print("Inserting historical prices...")
  add_historical_prices(formatted_hourly_prices)

def format_for_price_record(stock_data):
    price_record_data = []
    time_stamp = get_current_timestamp()
    for stock in stock_data:
      ticker = stock[0]
      price = float(stock[2])
      price_record_data.append((ticker, price, time_stamp))
    return price_record_data

def format_for_stock_record(stock_data):
    stock_record_data = []
    for stock in stock_data:
      ticker = stock[0]
      company_name = stock[1]
      stock_record_data.append((ticker, company_name))
    return stock_record_data

@decorators.log_execution_time
def scrape():
  stock_data = []

  base_url = f'https://finviz.com/screener.ashx?v=111&f=cap_largeover'
  base_response = session.get(base_url, headers=my_headers)
  soup = BeautifulSoup(base_response.text, 'html.parser')
  num_pages_element = soup.select('.screener-pages')[-2]
  num_pages_text = num_pages_element.text
  num_pages = int(num_pages_text)

  print("Scraping...")
  for i in range(0, num_pages):
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
        new_stock = Stock(stock[1], stock[2], stock[8])
        stock_data.append(new_stock)
    else:
      print(f"Request to {url} failed with status code {response.status_code}.")
    print(f'\r  Page {i + 1} / {num_pages}', end="\r")
    time.sleep(.4)
  return StockList(stock_data)

# @stub.function(image=scrape_image, secret=modal.Secret.from_name("stock-sim-env"), mounts=[funcs], schedule=modal.Cron("30 14 * * *"), timeout=23400)
def init():
  
  while is_weekday() and is_working_hours():
    loop_start_time = time.time()
    # Scrape all the pages
    stock_data: StockList = scrape()

    # Update stocks
    price_record_data = format_for_price_record(stock_data.to_tuple())
    stock_record_data = format_for_stock_record(stock_data.to_tuple())
    # create_stocks(stock_record_data)
    add_prices(price_record_data)

    # Log time
    loop_end_time = time.time()
    loop_time_elapsed = loop_end_time - loop_start_time

    print(f"Total operation took {loop_time_elapsed:.2f} seconds.")
    wait_time = 60 - loop_time_elapsed
    if wait_time < 0:
      wait_time = 0
    break

    print(f"\nWaiting {wait_time:.2f} seconds to restart..")
    time.sleep(wait_time)

  # Now that the day of scraping is done, get the prices that are on the hour and make price_history entries
  # start_time = time.time()
  # print("\nDone scraping!\nMaking historical prices...")
  # make_historical_prices()
  # historical_diff = time.time() - start_time
  # print(f"Finished creating historical prices in {historical_diff:.2f} seconds.")

  # longest_insertion_time = max(insertion_times)
  # print(f"Longest insertion time: {longest_insertion_time:.2f} seconds.")

# @stub.local_entrypoint()
def main():
  # scrape.remote()
  scrape()
# create_tables()
init()

