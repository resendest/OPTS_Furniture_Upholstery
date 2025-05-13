import mysql.connector
import os
from mysql.connector import Error
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Fetch credentials from environment variables
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

# Create a reusable connection function
def create_connection():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )

def insert_order(order_id, customer_name, item, barcode_path):
    conn = None
    cursor = None
    try:
        conn = create_connection()
        if conn is None:
            raise Error("Failed to connect to database.")
        cursor = conn.cursor()
        sql = "INSERT INTO orders (order_id, customer_name, item, barcode_path) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql, (order_id, customer_name, item, barcode_path))
        conn.commit()
    except Error as e:
        print(f"Error inserting order: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def get_order_by_id(order_id):
    conn = None
    cursor = None
    try:
        conn = create_connection()
        if conn is None:
            raise Error("Failed to connect to database.")
        cursor = conn.cursor(dictionary=True)
        sql = "SELECT * FROM orders WHERE order_id = %s"
        cursor.execute(sql, (order_id,))
        order = cursor.fetchone()
        return order
    except Error as e:
        print(f"Error fetching order: {e}")
        return None
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def get_all_orders():
    conn = None
    cursor = None
    try:
        conn = create_connection()
        if conn is None:
            raise Error("Failed to connect to database.")
        cursor = conn.cursor(dictionary=True)
        sql = "SELECT * FROM orders ORDER BY created_at DESC"
        cursor.execute(sql)
        orders = cursor.fetchall()
        return orders
    except Error as e:
        print(f"Error fetching orders: {e}")
        return []
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
