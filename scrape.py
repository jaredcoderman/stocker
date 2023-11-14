import requests
import modal
from funcs.db import *
from funcs.time_helpers import *
import time
from bs4 import BeautifulSoup

stub = modal.Stub("stock-scrape")

funcs = modal.Mount.from_local_dir(
    "~/side-projects/stocker-python/funcs",
    condition=lambda pth: not ".venv" in pth,
    remote_path="/root/funcs",
)

scrape_image = modal.Image.debian_slim(python_version="3.10").run_commands(
    "apt-get update",
    "apt-get install -y software-properties-common",
    "apt-add-repository non-free",
    "apt-add-repository contrib",
    "apt-get update",
    "apt-get install -y postgresql postgresql-contrib",
    "pip install beautifulsoup4",
    "pip install requests",
    "pip install psycopg2-binary",
    "pip install python-dotenv",
    "pip install pytz"
)


# Send an HTTP GET request to the URL

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

@stub.function(image=scrape_image, secret=modal.Secret.from_name("database_connection_string"), mounts=[funcs], schedule=modal.Cron("30 14 * * *"), timeout=23400)
def scrape():
  insertion_times = []
  stock_data = []
  while is_weekday() and is_working_hours():
    
    # Scrape all the pages
    print("Scraping...")
    total_start_time = time.time()
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
      print(f'\r  Page {i + 1} / 37', end="\r")
      time.sleep(.3)

    # Update stocks
    query_stock_data = []
    time_stamp = get_current_timestamp()
    for stock in stock_data:
      query_stock_data.append((stock[0], float(stock[2]), time_stamp))

    print("\nInserting prices...")
    start_time = time.time()
    add_prices(query_stock_data)
    print("Done!")

    end_time = time.time()
    insertion_diff = end_time - start_time
    total_diff = end_time - total_start_time

    insertion_times.append(insertion_diff)

    print("\nTime Logs:\n")
    print(f"Inserted in {insertion_diff:.2f} seconds.")
    print(f"Total operation took {total_diff:.2f} seconds.")
    wait_time = 60 - total_diff
    if wait_time < 0:
      wait_time = 0

    print(f"\nWaiting {wait_time:.2f} seconds to restart..")
    time.sleep(wait_time)

  # Now that the day of scraping is done, get the prices that are on the hour and make price_history entries
  start_time = time.time()
  if len(stock_data) > 0:
    print("\nDone scraping!\nMaking historical prices...")
    make_historical_prices()
    historical_diff = time.time() - start_time
    print(f"Finished creating historical prices in {historical_diff:.2f} seconds.")

    longest_insertion_time = max(insertion_times)
    print(f"Longest insertion time: {longest_insertion_time:.2f} seconds.")
  else:
    print("No stock data... Quitting")

@stub.local_entrypoint()
def main():
  scrape.remote()


