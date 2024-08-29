from funcs.db_connection import get_db_connection
from datetime import datetime
import tempfile 
import funcs.decorators as decorators
import time
import csv

def do_query(query, values=None):
  conn, cursor = get_db_connection()

  print("running query..")
  cursor.execute(query, values)

  conn.commit()
  cursor.close()
  conn.close()

def print_query(query):
  conn, cursor = get_db_connection()

  cursor.execute(query)
  rows = cursor.fetchall()
  
  for row in rows:
    print(row)

  cursor.close()
  conn.close()

def create_tables():
  do_query(
  """
CREATE TABLE stock (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(10) UNIQUE,
    company_name VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
  """)
  do_query(
  """
    CREATE TABLE price (
        id SERIAL PRIMARY KEY,
        ticker VARCHAR(10),
        price DECIMAL(10, 2),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
  """
  )

def show_tables():
  return do_query("SHOW TABLES;")

def create_stocks(stocks_data):
  conn, cursor = get_db_connection()
  query = "INSERT INTO stock (ticker, company_name) VALUES (%s, %s)"
  
  # Execute the query with multiple sets of values
  cursor.executemany(query, stocks_data)

  # Commit the changes to the database
  conn.commit()

  cursor.close()
  conn.close()

def add_price(ticker, price):
  conn, cursor = get_db_connection()

  query = f"INSERT INTO price (ticker, price) VALUES (%s, %s)"
  values = (ticker, price)
  do_query(query, values)
  print("Price added...")
  # Close the cursor and connection
  cursor.close()
  conn.close()

@decorators.log_execution_time
def add_prices(prices):
  print("Adding prices")
  conn, cursor = get_db_connection()
  query = "INSERT INTO price (ticker, price, created_at) VALUES (%s, %s, %s)"
  

  batch_size = len(prices) // 4  # Divide into 4 batches
  print(f"Inserting {len(prices)} prices...")
  insert_start = time.time()
  for i in range(0, len(prices), batch_size):
      batch = prices[i:i + batch_size]
      
      # Execute the query with a batch of values
      cursor.executemany(query, batch)
      
      # Commit the changes to the database after each batch
  conn.commit()
  cursor.close()
  conn.close()


def add_historical_prices(prices):
  conn, cursor = get_db_connection()
  query = "INSERT INTO historical_price (ticker, price, time_in_history) VALUES (%s, %s, %s)"
  
  # Execute the query with multiple sets of values
  cursor.executemany(query, prices)

  # Commit the changes to the database
  conn.commit()

  cursor.close()
  conn.close()


def get_prices(ticker):
  conn, cursor = get_db_connection()
  query = f"SELECT * FROM price WHERE ticker = %s"
  values = (ticker,)
  cursor.execute(query, values)
  rows = cursor.fetchall()
  cursor.close()
  conn.close()
  return rows

def get_all_tickers():
  conn, cursor = get_db_connection()
  query = f"SELECT * FROM stock"
  cursor.execute(query)
  rows = cursor.fetchall()
  tickers = []
  for row in rows:
    tickers.append(row[1])
  cursor.close()
  conn.close()
  return tickers

def get_all_hourly_prices_for_all_tickers():
    conn, cursor = get_db_connection()

    tickers = get_all_tickers()
    all_prices = []

    # Create a parameterized query with placeholders for tickers
    query = "SELECT * FROM price WHERE ticker IN %s AND EXTRACT(MINUTE FROM created_at) = 0"

    # Execute the query with the list of tickers
    cursor.execute(query, (tuple(tickers),))
    rows = cursor.fetchall()

    # Extend the all_prices list with the results
    all_prices.extend(rows)

    cursor.close()
    conn.close()
    return all_prices

def delete_all_but_last_60_prices():
   print("Deleting...")
   do_query("""
WITH ranked_prices AS (
    SELECT
        id,
        ticker,
        price,
        created_at,
        ROW_NUMBER() OVER (PARTITION BY ticker ORDER BY created_at DESC) AS row_num
    FROM
        price
)
DELETE FROM price
USING ranked_prices
WHERE price.id = ranked_prices.id AND ranked_prices.row_num > 60;""")
   print("Done!")   
