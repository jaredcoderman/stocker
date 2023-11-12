import requests
import modal
from funcs.db import *
from datetime import datetime, time
import time as sleep_time
import os
import pytz
import random
from bs4 import BeautifulSoup

stub = modal.Stub("stock-scrape")

funcs = modal.Mount.from_local_dir(
    "~/side-projects/stocker-python/funcs",
    condition=lambda pth: not ".venv" in pth,
    remote_path="/root/funcs",
)

bs4_image = modal.Image.debian_slim(python_version="3.10").run_commands(
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

def get_current_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

timezone = pytz.timezone('America/New_York')  # replace with the actual timezone

def is_weekday():
    # Get the current day of the week (Monday is 0, Sunday is 6)
    return datetime.now(timezone).weekday() < 5

def is_working_hours():
    # Get the current time in the specified timezone
    current_time = datetime.now(timezone).time()

    # Check if the current time is between 9:30 am and 4:00 pm
    return time(9, 30) <= current_time <= time(16, 0)


@stub.function(image=bs4_image, secret=modal.Secret.from_name("database_connection_string"), mounts=[funcs], schedule=modal.Cron("30 14 * * *"))
def scrape():
  while is_weekday() and is_working_hours():
    stock_data = []
    print("Scraping...")
    total_start_time = sleep_time.time()
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
      sleep_time.sleep(random.uniform(0.4, 1.0))

    # Create Stocks
    # stocks_data = []
    # for row in stock_data:
    #   stocks_data.append((row[0], row[1]))
    # create_stocks(stocks_data)
    
    # break

    # Update stocks
    query_stock_data = []
    time_stamp = get_current_timestamp()
    for stock in stock_data:
      query_stock_data.append((stock[0], float(stock[2]), time_stamp))
    print("\nInserting prices...")
    start_time = sleep_time.time()
    add_prices(query_stock_data)
    print("Done!")
    end_time = sleep_time.time()
    diff = end_time - start_time
    total_diff = end_time - total_start_time
    print("\nTime Logs:\n")
    print(f"Inserted in {diff:.2f} seconds.")
    print(f"Total operation took {total_diff:.2f} seconds.")
    wait_time = 60 - total_diff
    print(f"\nWaiting {wait_time:.2f} seconds to restart..")
    sleep_time.sleep(wait_time)

  # Now that the day of scraping is done, get the prices that are on the hour and make price_history entries
  

@stub.local_entrypoint()
def main():
  scrape.remote()
  print("Done!")


