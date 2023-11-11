from funcs.db_connection import get_db_connection
from datetime import datetime

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
        stock_ticker VARCHAR(10),
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

  query = f"INSERT INTO price (stock_ticker, price) VALUES (%s, %s)"
  values = (ticker, price)
  do_query(query, values)
  print("Price added...")
  # Close the cursor and connection
  cursor.close()
  conn.close()

def add_prices(prices):
    conn, cursor = get_db_connection()
    query = "INSERT INTO price (stock_ticker, price, created_at) VALUES (%s, %s, %s)"
    
    # Execute the query with multiple sets of values
    cursor.executemany(query, prices)

    # Commit the changes to the database
    conn.commit()

    cursor.close()
    conn.close()

def get_prices(ticker):
  conn, cursor = get_db_connection()
  query = f"SELECT * FROM price WHERE stock_ticker = %s"
  values = (ticker,)
  cursor.execute(query, values)
  rows = cursor.fetchall()
  cursor.close()
  conn.close()
  return rows