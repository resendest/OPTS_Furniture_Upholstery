from flask import Flask, request, jsonify, render_template, redirect, url_for, send_from_directory, flash
from backend.order_processing import create_order
from backend.db import query, execute
import os
from dotenv import load_dotenv
from backend.shop_routes import shop_bp
from backend.qr_utils import generate_order_qr

# Load environment variables
load_dotenv()


# Create Flask app and register shop blueprint

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

app.register_blueprint(shop_bp)


BASE_URL=os.getenv('BASE_URL').rstrip('/')

# -- Home / new order form --
def index():
    if request.method == 'POST':
        # Example: if your form fields are named "customer_id" and "invoice_no"
        try:
            customer_id = int(request.form['customer_id'])
        except (KeyError, ValueError):
            flash('Invalid customer ID.', 'error')
            return redirect(url_for('index'))

        invoice_no = request.form.get('invoice_no', '').strip()
        if not invoice_no:
            flash('Invoice number cannot be empty.', 'error')
            return redirect(url_for('index'))

        # If you eventually collect item‐line dictionaries, build them here.
        items = []            # e.g. [{"description": "...", "quantity": 1, …}, …]
        milestone_list = []   # e.g. ["Cutting", "Assembly", "Finishing"], etc.

        # Call create_order with the correct signature
        info = create_order(
            customer_id=customer_id,
            invoice_no=invoice_no,
            items=items,
            milestone_list=milestone_list,
            base_url=BASE_URL
        )

        flash(f'Order #{info["order_id"]} created successfully!', 'success')
        return redirect(url_for('order_created', order_id=info['order_id']))

    return render_template('index.html')


# -- Confirmation page --
@app.route('/order_created/<int:order_id>')
def order_created(order_id):
    order = query('SELECT * FROM orders WHERE order_id=%s', (order_id,))[0]
    return render_template('order_created.html', order=order)

# -- Update stage via QR --
@app.route('/scan/<int:order_id>', methods=['GET', 'POST'])
def update_stage(order_id):
    order = query('SELECT * FROM orders WHERE order_id=%s', (order_id,))[0]
    message = None
    if request.method == 'POST':
        if not request.form.get('confirm'):
            message = 'Please confirm details.'
        else:
            new_stage = request.form['stage']
            execute('UPDATE orders SET stage=%s, timestamp_updated=NOW() WHERE order_id=%s', (new_stage, order_id))
            order['stage'] = new_stage
            message = f'Stage updated to {new_stage}.'
    return render_template('update_stage.html', **order, message=message)

# -- Manager dashboard --
@app.route('/orders_overview')
def orders_overview():
    orders = query('SELECT * FROM orders ORDER BY timestamp_updated DESC')
    return render_template('orders_overview.html', orders=orders)

# -- Customer view --
@app.route('/order_status/<int:order_id>')
def order_status(order_id):
    order = query('SELECT * FROM orders WHERE order_id=%s', (order_id,))[0]
    return render_template('order_status.html', order=order)

# -- Serve work‑order PDFs --
@app.route('/work_orders/<path:filename>')
def work_orders(filename):
    return send_from_directory('static/work_orders', filename)

if __name__ == '__main__':
    app.run(debug=True)
