from flask import Flask, request, jsonify
from order_processing import insert_order, generate_barcode_image

app = Flask(__name__)

@app.route('/')
def home():
    return "Flask app is running."

@app.route('/submit_order', methods=['POST'])
def submit_order():
    data = request.get_json(force=True)

    # 1. Validate required fields
    if not data or 'customer_id' not in data:
        return jsonify({"error": "Missing required field: customer_id"}), 400

    try:
        # 2. Insert into Orders and get back (order_id, barcode_value)
        order_id, barcode_value = insert_order(
            customer_id=data['customer_id'],
            status=data.get('status', 'New'),
            notes=data.get('notes')
        )

        # 3. Generate the barcode PNG (Base64)
        barcode_b64 = generate_barcode_image(barcode_value)

        # 4. Return JSON with both order_id and the image data
        return jsonify({
            "message": "Order submitted successfully",
            "order_id": order_id,
            "barcode_value": barcode_value,
            "barcode_base64": barcode_b64
        }), 201

    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
