from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()
import os
import psycopg2

def get_db_connection():
  # Connect to the database
  #conn = psycopg2.connect(os.getenv("DATABASE_CONNECTION_STRING"))
  conn = psycopg2.connect(os.environ["DATABASE_CONNECTION_STRING"])


  try:
      # Create a cursor to interact with the database
      cursor = conn.cursor()

      return conn, cursor

  except Exception as e:
      print("Error: Unable to connect to the database")
      print(e)

  finally:
     pass
      # Close the cursor and connection
      # cursor.close()
      # conn.close()