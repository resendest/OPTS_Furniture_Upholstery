import uuid
import barcode
from barcode.writer import ImageWriter
from io import BytesIO
import base64
from db import create_connection


def insert_order(customer_id, status='New', notes=None):
    """
    Inserts into Orders:
      (customer_id, order_date, due_date=NULL, status, notes, barcode_value)
    Returns (order_id:int, barcode_value:str).
    """
    # 1. Generate a unique barcode string
    barcode_value = uuid.uuid4().hex[:12]

    conn = create_connection()
    if not conn:
        raise RuntimeError("Database connection failed")

    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO Orders
              (customer_id, order_date, due_date, status, notes, barcode_value)
            VALUES
              (%s, CURDATE(), NULL, %s, %s, %s)
        """, (customer_id, status, notes, barcode_value))
        conn.commit()

        order_id = cursor.lastrowid
        return order_id, barcode_value

    finally:
        cursor.close()
        conn.close()

def generate_barcode_image(order_id):
    """
    Generates a Code128 barcode for `order_id` and returns
    a Base64-encoded PNG image.
    """
    CODE128 = barcode.get_barcode_class('code128')
    barcode_obj = CODE128(order_id, writer=ImageWriter())

    buf = BytesIO()
    barcode_obj.write(buf)
    png_data = buf.getvalue()
    buf.close()

    return base64.b64encode(png_data).decode('utf-8')
