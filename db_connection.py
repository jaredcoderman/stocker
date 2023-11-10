from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()
import os
import MySQLdb

def get_db_connection():
  # Connect to the database
  conn = MySQLdb.connect(
    host=os.getenv("DATABASE_HOST"),
    user=os.getenv("DATABASE_USERNAME"),
    passwd=os.getenv("DATABASE_PASSWORD"),
    db=os.getenv("DATABASE"),
    autocommit=True,
    # ssl_mode="VERIFY_IDENTITY",
    # See https://planetscale.com/docs/concepts/secure-connections#ca-root-configuration
    # to determine the path to your operating systems certificate file.
    # ssl={ "ca": "" }
  )

  try:
      # Create a cursor to interact with the database
      cursor = conn.cursor()

      return conn, cursor

  except MySQLdb.Error as e:
      print("MySQL Error:", e)

  finally:
     pass
      # Close the cursor and connection
      # cursor.close()
      # conn.close()