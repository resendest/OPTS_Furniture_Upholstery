from flask import Blueprint, request, jsonify
from db import get_db
import barcode
from barcode.writer import ImageWriter
import os
import uuid

order_bp = Blueprint('order', __name__)
#             raise Error("Failed to connect to database.") 

@order_bp.route('/submit_order', methods=['POST'])
def submit_order():
    data = request.get_json()
    customer_name = data.get('customer_name')
    product = data.get('product')

    barcode_value = str(uuid.uuid4())

    #barcode image generator
    barcode_path = f"static/barcodes/{barcode_value}.png"
    code128 = barcode.get_barcode_class('code128')
    barcode_obj = code128(barcode_value, writer=ImageWriter())
    barcode_obj.save(barcode_path)
    
    # Save order to database
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO orders (customer_name, product, barcode_value, barcode_path) VALUES (%s, %s, %s, %s)",
        (customer_name, product, barcode_value, barcode_path)
    )
    conn.commit()
    cursor.close()
    return jsonify({"message": "Order submitted successfully", "barcode_value": barcode_value})

