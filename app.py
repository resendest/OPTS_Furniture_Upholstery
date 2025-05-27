from flask import Flask, request, jsonify, render_template, request, redirect, url_for, send_from_directory, flash
from backend.order_processing import create_order
from backend.db import query_db, execute_db
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

BASE_URL=os.getenv('BASE_URL').rstrip('/')

# -- Home / new order form --
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        customer = request.form['customer']
        product = request.form['product']
        info = create_order(customer, product, BASE_URL)
        flash('Order created successfully!', 'success')
        return redirect(url_for('order_created', order_id=info['order_id']))
    return render_template('index.html')

# -- Confirmation page --
@app.route('/order_created/<int:order_id>')
def order_created(order_id):
    order = query_db('SELECT * FROM orders WHERE order_id=%s', (order_id,))[0]
    return render_template('order_created.html', order=order)

# -- Update stage via QR --
@app.route('/update_stage/<int:order_id>', methods=['GET', 'POST'])
def update_stage(order_id):
    order = query_db('SELECT * FROM orders WHERE order_id=%s', (order_id,))[0]
    message = None
    if request.method == 'POST':
        if not request.form.get('confirm'):
            message = 'Please confirm details.'
        else:
            new_stage = request.form['stage']
            execute_db('UPDATE orders SET stage=%s, timestamp_updated=NOW() WHERE order_id=%s', (new_stage, order_id))
            order['stage'] = new_stage
            message = f'Stage updated to {new_stage}.'
    return render_template('update_stage.html', **order, message=message)

# -- Manager dashboard --
@app.route('/orders_overview')
def orders_overview():
    orders = query_db('SELECT * FROM orders ORDER BY timestamp_updated DESC')
    return render_template('orders_overview.html', orders=orders)

# -- Customer view --
@app.route('/order_status/<int:order_id>')
def order_status(order_id):
    order = query_db('SELECT * FROM orders WHERE order_id=%s', (order_id,))[0]
    return render_template('order_status.html', order=order)

# -- Serve work‑order PDFs --
@app.route('/work_orders/<path:filename>')
def work_orders(filename):
    return send_from_directory('static/work_orders', filename)

if __name__ == '__main__':
    app.run(debug=True)
