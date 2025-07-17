# This file is the main entry point for the Flask application.
# It initializes the app, sets up routes, and handles order creation.
# It also includes user registration, login, and email sending functionality.
# Ultimately, it serves as the core of the OPTS application.

import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import os
import secrets
from datetime import datetime


from flask import (
    Flask, request, render_template,
    redirect, url_for, flash,
    send_from_directory, current_app,
    session, g
)
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

# Define this before any @login_required decorators are used:
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

# Load environment variables
load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev_secret")
app.config["BASE_URL"] = os.getenv("BASE_URL", "http://localhost:5000").rstrip("/")

from backend.order_processing import create_order
from backend.db import execute
from backend.shop_routes import shop_bp
from backend.email_utils import init_mail

init_mail(app)  # Initialize Flask-Mail with app config

# Base URL for QR code links
# Note: This should match the .env BASE_URL as well as your deployment server public URL
BASE_URL = os.getenv("BASE_URL", "http://localhost:5000").rstrip("/") 

# Register blueprint
app.register_blueprint(shop_bp)


@app.route("/", methods=["GET"])
def home():
    if session.get("customer_id"):
        # Redirect staff to portal, others to client dashboard
        if session.get("is_staff"):
            return redirect(url_for("portal"))
        else:
            return redirect(url_for("client_dashboard"))
    return render_template("home.html", current_year=datetime.now().year)

@app.route("/create_order", methods=["GET", "POST"])
def create_order_page():
    if request.method == "POST":
        app.logger.debug("▶▶▶ FORM DATA: %s", dict(request.form))

        # ─── Validate basic customer info ──────────────────
        name  = request.form.get("customer_name", "").strip()
        email = request.form.get("customer_email", "").strip()
        phone = request.form.get("customer_phone", "").strip()
        if not all([name, email, phone]):
            flash("Name, email, and phone are required.", "error")
            return redirect(url_for("create_order_page"))

        # ─── Product codes ─────────────────────────────────
        # Split by newlines, strip whitespace, ignore empty lines
        # This allows pasting multiple codes at once
        raw_codes = (request.form.get("product_codes") or "").splitlines()
        product_codes = [c.strip() for c in raw_codes if c.strip()]
        if not product_codes:
            flash("Enter at least one product code.", "error")
            return redirect(url_for("create_order_page"))

        invoice_no = request.form.get("invoice_no", "")
        if not invoice_no:
            flash("Invoice Number is required.", "error")
            return redirect(url_for("create_order_page"))

        milestone_list = request.form.getlist("milestone_list")
        if not milestone_list:
            flash("Select at least one milestone.", "error")
            return redirect(url_for("create_order_page"))

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
            return redirect(url_for("create_order_page"))

        flash(f"Order #{info['order_id']} created successfully!", "success")

        # ————— Generate & persist a one-time registration token —————
        customer_id = info["customer_id"]
        token = secrets.token_urlsafe(16)
        # store it on the customer record
        execute(
            "UPDATE customers SET register_token=%s WHERE customer_id=%s",
            (token, customer_id)
        )

        # ————— Email the “complete your registration” link —————
        from backend.email_utils import send_registration_email
        try:
            send_registration_email(
                user_id=customer_id,
                to_addr=email,
                token=token,
                order_id=info["order_id"],
            )
            app.logger.info("Registration email queued to %s", email)
        except Exception as ex:
            app.logger.error("Failed to send registration email: %s", ex)

        # ————— Redirect to order confirmation page —————
        return redirect(url_for("order_created", order_id=info["order_id"]))
    # For GET, show the order form
    return render_template("index.html", current_year=datetime.now().year)

@app.route("/email-config")
def email_config():
    return {
      "HOST":   app.config.get("MAIL_SERVER"),
      "PORT":   app.config.get("MAIL_PORT"),
      "TLS":    app.config.get("MAIL_USE_TLS"),
      "USER":   app.config.get("MAIL_USERNAME"),
      "PW":     repr(app.config.get("MAIL_PASSWORD"))  # show quotes if any
    }


@app.route("/test-email")
def test_email():
    from backend.email_utils import send_registration_email
    try:
        send_registration_email(
            user_id=0,
            to_addr=current_app.config["MAIL_USERNAME"],
            token="dummy"
        )
        return "Email send() returned OK—check inbox/spam"
    except Exception as e:
        return f"SEND ERROR: {e}", 500



@app.route("/order_created/<int:order_id>")
def order_created(order_id):
    # execute() now returns a LIST for SELECTs
    rows = execute(
        "SELECT * FROM orders WHERE order_id = %s",
        (order_id,)
    )
    if not rows:
        flash(f"Order #{order_id} not found.", "error")
        return redirect(url_for("home"))  # changed from "index"

    order = rows[0]
    return render_template(
        "order_created.html",
        order=order,
        current_year=datetime.now().year
    )


@app.route("/work_orders/<path:filename>")
def work_orders(filename):
    return send_from_directory("static/work_orders", filename)

# ————— Customer registration via token —————
@app.route("/register", methods=["GET", "POST"])
def register():
    token = request.args.get("token", "")
    order_id = request.args.get("order_id", type=int)
    if not token or not order_id:
        # Show info page if accessed directly (no token/order_id)
        return render_template(
            "register.html",
            email=None,
            info_message="To register, please use the link sent to your email after placing an order."
        )
    rows = execute(
        "SELECT customer_id, email FROM customers WHERE register_token = %s",
        (token,)
    )
    if not rows:
        flash("Invalid or expired registration link.", "danger")
        return redirect(url_for("home"))  # changed from "index"
    cust = rows[0]

    if request.method == "POST":
        pw  = request.form.get("password", "")
        pw2 = request.form.get("confirm_password", "")

        if len(pw) < 8:
            flash("Password must be at least 8 characters.", "warning")
        elif pw != pw2:
            flash("Passwords must match and be at least 8 characters.", "warning")
        else:
            pw_hash = generate_password_hash(pw)
            execute(
                """UPDATE customers
                      SET password_hash   = %s,
                          register_token  = NULL,
                          registered_at   = %s
                    WHERE customer_id    = %s""",
                (pw_hash, datetime.utcnow(), cust["customer_id"])
            )
            session["customer_id"] = cust["customer_id"]
            session["user_id"] = cust["customer_id"]  # or whatever your user ID field is
            flash("Registration complete! Welcome.", "success")
            return redirect(url_for("client_dashboard"))
        # now send directly to the status page
        return redirect(url_for("order_status", order_id=order_id))

    return render_template("register.html", email=cust["email"], info_message=None)


# ————— Customer login & logout —————
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip()
        pw    = request.form["password"]
        rows = execute(
            "SELECT customer_id, password_hash, is_staff FROM customers WHERE email = %s",
            (email,)
        )
        if rows and rows[0]["password_hash"] and check_password_hash(rows[0]["password_hash"], pw):
            session["customer_id"] = rows[0]["customer_id"]
            session["user_id"] = rows[0]["customer_id"]  # or whatever your user ID field is
            session["is_staff"] = bool(rows[0].get("is_staff", False))
            if session["is_staff"]:
                return redirect(url_for("portal"))
            else:
                return redirect(url_for("client_dashboard"))
        flash("Invalid email or password.", "danger")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("customer_id", None)
    session.pop("user_id", None)
    session.pop("is_staff", None)
    flash("You have been logged out.", "info")
    return redirect(url_for("home"))


# ————— Customer portal (their orders only) —————
@app.route("/dashboard")
def client_dashboard():
    cid = session.get("customer_id")
    if not cid:
        return redirect(url_for("login"))
    
    orders = execute(
        "SELECT order_id, invoice_no, due_date, notes, status, client_pdf_path "
        "FROM orders WHERE customer_id=%s "
        "ORDER BY invoice_no DESC",
        (cid,)
    ) or []

    # Add computed status logic for client dashboard too
    if orders:
        order_ids = [o["order_id"] for o in orders]
        
        # Pull milestone statuses for these orders
        ms = execute(
            "SELECT order_id, status FROM order_milestones WHERE order_id IN %s",
            (tuple(order_ids),)
        ) or []

        # Group statuses per order
        from collections import defaultdict
        grouped = defaultdict(list)
        for r in ms:
            grouped[r["order_id"]].append(r["status"])

        # Compute master status per order
        for o in orders:
            sts = grouped[o["order_id"]]
            if not sts or all(s == "Not Started" for s in sts):
                o["computed_status"] = "Not Started"
            elif all(s == "Completed" for s in sts):
                o["computed_status"] = "Completed"
            else:
                o["computed_status"] = "In Progress"

    return render_template("client_dashboard.html", orders=orders)

@app.route("/order/<int:order_id>")
def view_order(order_id):
    print(f"🔥🔥🔥 VIEW_ORDER ROUTE CALLED FOR ORDER {order_id} 🔥🔥🔥")
    
    cid = session.get("customer_id")
    is_staff = session.get("is_staff")
    
    print(f"🔥 Customer ID: {cid}, Is Staff: {is_staff}")
    
    if not cid and not is_staff:
        return redirect(url_for("login"))

    if is_staff:
        rows = execute(
            """
            SELECT o.order_id, o.invoice_no, o.created_at, o.due_date, o.notes, o.status,
                   c.name AS customer_name, c.email AS customer_email, c.phone AS customer_phone
            FROM orders o
            JOIN customers c ON o.customer_id = c.customer_id
            WHERE o.order_id = %s
            """,
            (order_id,)
        )
    else:
        rows = execute(
            """
            SELECT o.order_id, o.invoice_no, o.created_at, o.due_date, o.notes, o.status,
                   c.name AS customer_name, c.email AS customer_email, c.phone AS customer_phone
            FROM orders o
            JOIN customers c ON o.customer_id = c.customer_id
            WHERE o.order_id = %s AND o.customer_id = %s
            """,
            (order_id, cid)
        )
    
    if not rows:
        flash(f"Order #{order_id} not found.", "danger")
        return redirect(url_for("client_dashboard") if not is_staff else url_for("portal"))

    order = rows[0]
    order["id"] = order["order_id"]

    # CRITICAL DEBUG: Let's see what's actually in the database
    print(f"DEBUG: Looking for milestones for order_id = {order_id}")
    
    # Try a simpler query first
    test_milestones = execute(
        "SELECT * FROM order_milestones WHERE order_id = %s",
        (order_id,)
    )
    print(f"DEBUG: Raw milestone query returned: {test_milestones}")
    
    # Now the original query
    milestones = execute(
        "SELECT milestone_id, milestone_name, stage_number, status, is_client_action, is_approved "
        "FROM order_milestones WHERE order_id = %s ORDER BY stage_number",
        (order_id,)
    ) or []

    print(f"DEBUG: Fetched {len(milestones)} milestones for order {order_id}")
    for i, m in enumerate(milestones):
        print(f"DEBUG: Milestone {i}: {dict(m)}")

    return render_template("order_detail.html", order=order, milestones=milestones)

@app.route("/status/<int:order_id>")
def order_status(order_id):
    cid = session.get("customer_id")
    if not cid:
        return redirect(url_for("login"))

    # fetch the single order, ensure it belongs to them
    rows = execute(
        "SELECT order_id, invoice_no, created_at, due_date, notes "
        "FROM orders WHERE order_id=%s AND customer_id=%s",
        (order_id, cid)
    )
    if not rows:
        flash(f"Order #{order_id} not found.", "danger")
        return redirect(url_for("client_dashboard"))
    order = rows[0]

    # fetch the milestone history
    milestones = execute(
        "SELECT milestone, created_at "
        "FROM order_milestones WHERE order_id=%s ORDER BY created_at",
        (order_id,)
    ) or []

    return render_template(
        "status.html",
        order=order,
        milestones=milestones
    )

@app.route("/portal")
def portal():
    if not session.get("is_staff"):
        flash("Staff login required.", "danger")
        return redirect(url_for("login"))

    # fetch all orders
    orders = execute(
        """
        SELECT o.*, c.name AS customer_name, c.email AS customer_email
        FROM orders o
        JOIN customers c ON o.customer_id = c.customer_id
        ORDER BY o.order_id DESC
        """
    ) or []

    # fetch counts by milestone name (you already have this)
    milestone_counts = {}
    if orders:
        order_ids = [o["order_id"] for o in orders]
        rows = execute(
            "SELECT milestone_name, COUNT(*) AS count "
            "FROM order_milestones WHERE order_id IN %s "
            "GROUP BY milestone_name",
            (tuple(order_ids),)
        ) or []
        for row in rows:
            milestone_counts[row["milestone_name"]] = row["count"]

        # now pull every milestone status for those orders
        ms = execute(
            "SELECT order_id, status FROM order_milestones WHERE order_id IN %s",
            (tuple(order_ids),)
        ) or []

        # group statuses per order
        from collections import defaultdict
        grouped = defaultdict(list)
        for r in ms:
            grouped[r["order_id"]].append(r["status"])

        # compute a master status per order
        for o in orders:
            sts = grouped[o["order_id"]]
            if not sts or all(s == "Not Started" for s in sts):
                o["computed_status"] = "Not Started"
            elif all(s == "Completed" for s in sts):
                o["computed_status"] = "Completed"
            else:
                o["computed_status"] = "In Progress"

    return render_template(
        "master_dashboard.html",
        orders=orders,
        milestone_counts=milestone_counts
    )

@app.route("/order/<int:order_id>/edit", methods=["POST"])
@login_required
def edit_order(order_id):
    if not session.get("is_staff"):
        flash("Unauthorized", "danger")
        return redirect(url_for("view_order", order_id=order_id))

    updated = 0
    for field, value in request.form.items():
        if field.startswith("milestone_status_"):
            try:
                milestone_id = int(field.replace("milestone_status_", ""))
                execute(
                    "UPDATE order_milestones SET status = %s WHERE milestone_id = %s",
                    (value, milestone_id)
                )
                updated += 1
            except (ValueError, IndexError):
                continue

    if updated:
        flash(f"{updated} milestone(s) updated.", "success")
    else:
        flash("No milestones updated.", "info")

    return redirect(url_for("view_order", order_id=order_id))

@app.route("/add_staff", methods=["GET", "POST"])
def add_staff():
    # Only allow current staff to add new staff
    if not session.get("is_staff"):
        flash("Unauthorized", "danger")
        return redirect(url_for("login"))
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template("add_staff.html")

        password_hash = generate_password_hash(password)
        # Insert new staff user
        execute(
            "INSERT INTO customers (name, email, password_hash, is_staff) VALUES (%s, %s, %s, TRUE)",
            (name, email, password_hash)
        )

        # Send welcome email to staff
        from backend.email_utils import mail, Message
        msg = Message(
            subject="Your Staff Account Has Been Created",
            recipients=[email],
            body=f"Hello {name},\n\nYour staff account for Lousso Designs has been created.\nYou can now log in at {app.config['BASE_URL']}/login\n\nIf you did not request this, please contact your administrator."
        )
        try:
            mail.send(msg)
        except Exception as e:
            flash(f"Staff user added, but failed to send email: {e}", "warning")

        flash("Staff user added!", "success")
        return redirect(url_for("portal"))
    return render_template("add_staff.html")

@app.route("/scan/<int:order_id>", methods=["GET"])
@login_required
def scan_view(order_id):
    milestones = execute(
        "SELECT milestone_id, milestone_name, stage_number, status, is_client_action, is_approved "
        "FROM order_milestones WHERE order_id = %s ORDER BY stage_number",
        (order_id,)
    ) or []
    return render_template(
        "scan.html",
        order_id=order_id,
        milestones=milestones
    )

@app.route("/order/<int:order_id>/delete", methods=["POST"])
def delete_order(order_id):
    if not session.get("is_staff"):
        flash("Unauthorized", "danger")
        return redirect(url_for("home"))
    # Delete from all child tables first
    execute("DELETE FROM order_items WHERE order_id=%s", (order_id,))
    execute("DELETE FROM order_specs WHERE order_id=%s", (order_id,))
    # Add more deletes here if you have other related tables (e.g., order_milestones)
    execute("DELETE FROM order_milestones WHERE order_id=%s", (order_id,))
    # Then delete the order
    execute("DELETE FROM orders WHERE order_id=%s", (order_id,))
    flash(f"Order #{order_id} has been deleted. This action cannot be reversed.", "success")
    return redirect(url_for("portal"))

@app.before_request
def load_customer():
    g.customer_name = None
    cid = session.get("customer_id")
    if cid:
        rows = execute("SELECT name FROM customers WHERE customer_id=%s", (cid,))
        if rows:
            g.customer_name = rows[0]["name"]

@app.context_processor
def inject_customer_name():
    return {"customer_name": getattr(g, "customer_name", None)}

# Client-provided milestone choices
# This list can be extended with new milestones as needed
MILESTONE_CHOICES = [
  "Custom Material Preparation",
  "Project Approved, Production Kicking Off",
  "In Production",
  "Awaiting Quality Check",
  "Passed Quality Check",
  "Out for Delivery",
  # …any new ones…
]

# inject into ALL templates
@app.context_processor
def inject_milestone_choices():
    return dict(milestone_choices=MILESTONE_CHOICES)

@app.route("/debug_order/<int:order_id>")
def debug_order(order_id):
    print(f"🔥 DEBUG ROUTE CALLED FOR ORDER {order_id}")
    
    milestones = execute(
        "SELECT milestone_id, milestone_name, status FROM order_milestones WHERE order_id = %s",
        (order_id,)
    )
    
    result = f"<h1>Debug for Order {order_id}</h1>"
    if milestones:
        for m in milestones:
            result += f"<p>ID: {m.get('milestone_id')}, Name: {m.get('milestone_name')}, Status: {m.get('status')}</p>"
    else:
        result += "<p>No milestones found</p>"
    
    return result

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")