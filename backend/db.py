import mysql.connector
import os
from dotenv import load_dotenv

# Load .env from the parent directory (project root)
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

def create_connection():
    try:
        connection = mysql.connector.connect(
            host=os.getenv("MYSQL_HOST"),
            user=os.getenv("MYSQL_USER"),
            password=os.getenv("MYSQL_PASSWORD"),
            database=os.getenv("MYSQL_DB")
        )
        return connection
    except mysql.connector.Error as e:
        print("Error connecting to MySQL:", e)
        return None
