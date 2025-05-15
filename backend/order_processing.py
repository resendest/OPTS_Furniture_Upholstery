import uuid
from db import create_connection
import barcode
from barcode.writer import ImageWriter
from io import BytesIO
import base64

def generate_barcode():
    return uuid.uuid4().hex[:12]

def generate_barcode_image(order_id: str) -> str:
    CODE128 = barcode.get_barcode_class('code128')
    barcode_obj = CODE128(order_id, writer=ImageWriter())

    buffer = BytesIO()
    barcode_obj.write(buffer)
    img_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return img_str

def process_order(customer_name, product):
    connection = create_connection()
    if not connection:
        return None

    barcode = generate_barcode()
    try:
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO orders (customer_name, product, barcode)
            VALUES (%s, %s, %s)
        """, (customer_name, product, barcode))
        connection.commit()
        return barcode
    except Exception as e:
        print("Database error:", e)
        return None
    finally:
        connection.close()
