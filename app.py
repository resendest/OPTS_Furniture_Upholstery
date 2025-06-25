import os
from datetime import datetime

from flask import (
    Flask, request, render_template,
    redirect, url_for, flash,
    send_from_directory
)
from dotenv import load_dotenv

from backend.order_processing import create_order
from backend.db import execute
from backend.shop_routes import shop_bp
from backend.email_utils import init_mail

# Load environment variables
load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev_secret")
app.config["BASE_URL"] = os.getenv("BASE_URL", "http://localhost:5000").rstrip("/")

init_mail(app)  # Initialize Flask-Mail with app config

# Base URL for QR code links
BASE_URL = os.getenv("BASE_URL", "http://localhost:5000").rstrip("/")

# Register blueprint
app.register_blueprint(shop_bp)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        app.logger.debug("▶▶▶ FORM DATA: %s", dict(request.form))

        # ─── Validate basic customer info ──────────────────
        name  = request.form.get("customer_name", "").strip()
        email = request.form.get("customer_email", "").strip()
        phone = request.form.get("customer_phone", "").strip()
        if not all([name, email, phone]):
            flash("Name, email, and phone are required.", "error")
            return redirect(url_for("index"))

        # ─── Product codes ─────────────────────────────────
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

        # ─── Order specs ──────────────────────────────────
        quantity          = int(request.form.get("quantity", "1"))
        repair_glue       = "repair_glue" in request.form
        replace_springs   = "replace_springs" in request.form
        back_style        = request.form.get("back_style")
        seat_style        = request.form.get("seat_style")
        new_back_insert   = request.form.get("new_back_insert") == "true"
        new_seat_insert   = request.form.get("new_seat_insert") == "true"
        back_insert_type  = request.form.get("back_insert_type")
        seat_insert_type  = request.form.get("seat_insert_type")
        trim_style        = request.form.get("trim_style")
        placement         = request.form.get("placement")
        fabric_specs      = request.form.get("fabric_specs")
        vendor_color      = request.form.get("vendor_color")
        frame_finish      = request.form.get("frame_finish")
        specs_text        = request.form.get("specs")
        topcoat           = request.form.get("topcoat")
        customer_initials = request.form.get("customer_initials")

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
                notes=notes,
                quantity=quantity,
                repair_glue=repair_glue,
                replace_springs=replace_springs,
                back_style=back_style,
                seat_style=seat_style,
                new_back_insert=new_back_insert,
                new_seat_insert=new_seat_insert,
                back_insert_type=back_insert_type,
                seat_insert_type=seat_insert_type,
                trim_style=trim_style,
                placement=placement,
                fabric_specs=fabric_specs,
                vendor_color=vendor_color,
                frame_finish=frame_finish,
                specs_text=specs_text,
                topcoat=topcoat,
                customer_initials=customer_initials,
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
    # execute() now returns a LIST for SELECTs
    rows = execute(
        "SELECT * FROM orders WHERE order_id = %s",
        (order_id,)
    )
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
