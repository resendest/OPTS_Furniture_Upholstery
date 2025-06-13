import os
from datetime import datetime

from flask import (
    Flask, request, render_template,
    redirect, url_for, flash,
    send_from_directory
)
from dotenv import load_dotenv

from backend.order_processing import create_order
from backend.shop_routes import shop_bp

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev_secret")

# Base URL for QR code links
BASE_URL = os.getenv("BASE_URL", "http://localhost:5000").rstrip("/")

# Register blueprint
app.register_blueprint(shop_bp)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":

        print("▶▶▶ FORM DATA:", dict(request.form))

        # Read customer contact info
        name  = request.form.get("customer_name", "").strip()
        email = request.form.get("customer_email", "").strip()
        phone = request.form.get("customer_phone", "").strip()
        if not all([name, email, phone]):
            flash("Name, email, and phone are required.", "error")
            return redirect(url_for("index"))

        # Parse Product Codes: split textarea into a list of non-empty lines
        raw_codes = request.form.get("product_codes", "").splitlines()
        product_codes = [c.strip() for c in raw_codes if c.strip()]
        if not product_codes:
           flash("Enter at least one product code.", "error")
           return redirect(url_for("index"))

        invoice_no = request.form.get("invoice_no", "").strip()
        if not invoice_no:
            flash("Invoice Number is required.", "error")
            return redirect(url_for("index"))

        milestone_list = request.form.getlist("milestone_list")
        if not milestone_list:
            flash("Select at least one milestone.", "error")
            return redirect(url_for("index"))

        due_date = request.form.get("due_date") or None
        notes    = request.form.get("notes")    or None

       
        try:
            info = create_order(
                name=name,
                email=email,
                phone=phone,
                product_codes=product_codes,
                invoice_no=invoice_no,
                milestone_list=milestone_list,
                base_url=BASE_URL,
                due_date=due_date,
                notes=notes
            )
        except Exception as e:
            app.logger.exception("Error creating order")
            flash(f"Error creating order: {e}", "error")
            return redirect(url_for("index"))

        flash(f"Order #{info['order_id']} created successfully!", "success")
        return redirect(url_for("order_created", order_id=info["order_id"]))

    return render_template("index.html", current_year=datetime.now().year)

@app.route("/order_created/<int:order_id>")
def order_created(order_id):
    from backend.db import execute
    rows = execute("SELECT * FROM orders WHERE order_id = %s", (order_id,))
    if not rows:
        flash(f"Order #{order_id} not found.", "error")
        return redirect(url_for("index"))
    order = rows[0]
    return render_template(
        "order_created.html",
        order=order,
        current_year=datetime.now().year
    )

@app.route("/work_orders/<path:filename>")
def work_orders(filename):
    return send_from_directory("static/work_orders", filename)

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", 5000)),
        debug=True
    )
