import os
from datetime import datetime

from flask import (
    Flask, request, jsonify, render_template,
    redirect, url_for, send_from_directory, flash
)
from dotenv import load_dotenv

# Backend imports
from backend.order_processing import create_order
from backend.db import query, execute
from backend.shop_routes import shop_bp

# Load environment variables from .env
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev_secret")

# Register the Blueprint that handles /scan/<order_id>
app.register_blueprint(shop_bp)

# Ensure BASE_URL is set in .env (used internally by create_order)
BASE_URL = os.getenv("BASE_URL", "http://localhost:5000").rstrip("/")


# ----------------------------
# HOME / NEW ORDER FORM
# ----------------------------
@app.route("/", methods=["GET", "POST"])
def index():
    """
    Renders a form (index.html) to create a new order.
    On POST, validates inputs and calls create_order().
    """
    if request.method == "POST":
        # Validate and parse customer_id
        try:
            customer_id = int(request.form["customer_id"])
        except (KeyError, ValueError):
            flash("Invalid customer ID.", "error")
            return redirect(url_for("index"))

        # Validate invoice_no
        invoice_no = request.form.get("invoice_no", "").strip()
        if not invoice_no:
            flash("Invoice number cannot be empty.", "error")
            return redirect(url_for("index"))

        # (Optional) Build lists from form inputs
        items = []           # e.g., [{"product_id": 2, "quantity": 1}, …]
        milestone_list = []  # e.g., ["Cutting", "Assembly", "Inspection"]

        # Call create_order() without passing base_url explicitly
        try:
            info = create_order(
                customer_id=customer_id,
                invoice_no=invoice_no,
                items=items,
                milestone_list=milestone_list
            )
        except Exception as e:
            flash(f"Error creating order: {e}", "error")
            return redirect(url_for("index"))

        flash(f"Order #{info['order_id']} created successfully!", "success")
        return redirect(url_for("order_created", order_id=info["order_id"]))

    # On GET, render the new-order form
    return render_template("index.html", current_year=datetime.now().year)


# ----------------------------
# ORDER CONFIRMATION PAGE
# ----------------------------
@app.route("/order_created/<int:order_id>")
def order_created(order_id):
    order = query("SELECT * FROM orders WHERE order_id = %s", (order_id,))
    if not order:
        flash(f"Order #{order_id} not found.", "error")
        return redirect(url_for("index"))

    return render_template(
        "order_created.html",
        order=order[0],                # includes order.lousso_pdf_path
        current_year=datetime.now().year
    )


# ----------------------------
# MANAGER DASHBOARD
# ----------------------------
@app.route("/orders_overview")
def orders_overview():
    """
    Displays all orders ordered by last updated timestamp
    (orders_overview.html).
    """
    orders = query("SELECT * FROM orders ORDER BY timestamp_updated DESC", ())
    return render_template(
        "orders_overview.html",
        orders=orders,
        current_year=datetime.now().year
    )


# ----------------------------
# CUSTOMER VIEW
# ----------------------------
@app.route("/order_status/<int:order_id>")
def order_status(order_id):
    order = query("SELECT * FROM orders WHERE order_id = %s", (order_id,))
    if not order:
        flash(f"Order #{order_id} not found.", "error")
        return redirect(url_for("index"))

    milestones = query(
        "SELECT milestone_id, stage_number, milestone_name, is_client_action, is_approved "
        "FROM order_milestones WHERE order_id = %s ORDER BY stage_number;",
        (order_id,)
    )

    return render_template(
        "order_status.html",
        order=order[0],           # includes order.client_pdf_path
        milestones=milestones,    # list of milestone dicts
        current_year=datetime.now().year
    )


# ----------------------------
# SERVE WORK-ORDER PDFs
# ----------------------------
@app.route("/work_orders/<path:filename>")
def work_orders(filename):
    """
    Serves generated PDF files under static/work_orders.
    """
    return send_from_directory("static/work_orders", filename)


# ----------------------------
# RUN THE APP
# ----------------------------
if __name__ == "__main__":
    app.run(debug=True)
