# This file pertains to the order creation and processing logic for the OPTS application.
# It handles the creation of new orders, including customer details, product codes,
# and order specifications. 
import pathlib
from datetime import datetime
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors



from backend.db import execute
from backend.qr_utils import generate_order_qr

BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
QR_DIR = BASE_DIR / "static" / "qr"
WORK_DIR = BASE_DIR / "static" / "work_orders"
QR_DIR.mkdir(parents=True, exist_ok=True)
WORK_DIR.mkdir(parents=True, exist_ok=True)

# Get the order details and generate a PDF
def make_work_order_pdf(  
    path: pathlib.Path,
    order_id: int,
    client_name: str,
    invoice_no: str,
    quantity: int,
    product_codes: list[str],
    item_images: list[str],
    fabric_inside: list[str],
    fabric_outside: list[str],
    repair_req: str,
    fabric_specs: str,
    upholstery: dict,
    inserts: dict,
    insert_types: dict,
    trim: dict,
    finish: dict,
    notes: str,
    initials: str,
    qr_path: str | None,
):
    # Create a PDF canvas for the work order
    c = canvas.Canvas(str(path), pagesize=LETTER)
    w, h = LETTER
    margin = 0.5 * inch
    y = h - margin

    # Title and date addition
    c.setFont("Helvetica-Bold", 16)
    c.drawString(margin, y, f"Work Order #{order_id}")
    c.setFont("Helvetica", 10)
    date_str = datetime.now().strftime("%Y-%m-%d")
    c.drawRightString(w - margin, y, f"Date: {date_str}")
    y -= 0.3 * inch

    # Information table
    data = [
        ["Client", client_name, "Invoice #", invoice_no],
        ["Product Codes", ", ".join(product_codes), "Quantity", str(quantity)],
        ["Repair/Glue", repair_req, "", ""],
        ["Back Style", upholstery.get("back", ""), "Seat Style", upholstery.get("seat", "")],
        ["New Back Insert", inserts.get("back", ""), "New Seat Insert", inserts.get("seat", "")],
        ["Back Insert Type", insert_types.get("back", ""), "Seat Insert Type", insert_types.get("seat", "")],
        ["Trim Style", trim.get("style", ""), "Placement", trim.get("placement", "")],
        ["Vendor Color", trim.get("vendor", ""), "Frame Finish", finish.get("type", "")],
        ["Finish Specs", finish.get("specs", ""), "Topcoat", finish.get("topcoat", "")],
        ["Fabric Specs", fabric_specs or "", "Initials", initials or ""],
    ]
    table = Table(data, colWidths=[1.2*inch, 2.3*inch, 1.2*inch, 2.3*inch])
    table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    tw, th = table.wrap(w - 2*margin, h)
    table.drawOn(c, margin, y - th)
    y -= th + 0.2 * inch

    # Notes section
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin, y, "Notes:")
    y -= 0.2 * inch
    c.setFont("Helvetica", 10)
    for line in (notes or "").splitlines():
        c.drawString(margin + 10, y, line)
        y -= 0.15 * inch
    y -= 0.2 * inch

    # QR code (if exists)
    if qr_path:
        qr_file = QR_DIR / qr_path.split("/")[-1]
        if qr_file.exists():
            qr_size = 1.5 * inch
            c.drawImage(
                str(qr_file),
                w - margin - qr_size,
                margin,
                width=qr_size, height=qr_size
            )

    c.showPage()
    c.save()

# Create a new order with all details from order creation form in app.
def create_order(
    name: str,
    email: str,
    phone: str,
    product_codes: list[str],
    invoice_no: str,
    milestone_list: list[str],
    base_url: str,
    due_date: str | None = None,
    notes: str | None = None,
    *,
    quantity: int,
    repair_glue: bool,
    replace_springs: bool,
    back_style: str,
    seat_style: str,
    new_back_insert: bool,
    new_seat_insert: bool,
    back_insert_type: str | None,
    seat_insert_type: str | None,
    trim_style: str | None,
    placement: str | None,
    fabric_specs: str | None,
    vendor_color: str | None,
    frame_finish: str | None,
    specs_text: str | None,
    topcoat: str | None,
    customer_initials: str | None,
) -> dict:
    # Lookup or create customer
    cust_rows = execute(
        "SELECT customer_id FROM customers WHERE email=%s",
        (email,)
    )
    if cust_rows:
        customer_id = cust_rows[0]["customer_id"]
    else:
        new_cust = execute(
            "INSERT INTO customers(name,email,phone) VALUES(%s,%s,%s) RETURNING customer_id",
            (name, email, phone)
        )
        customer_id = new_cust["customer_id"]

    # Create order and grab its ID
    order_res = execute(
        "INSERT INTO orders(customer_id,invoice_no,due_date,notes) VALUES(%s,%s,%s,%s) RETURNING order_id",
        (customer_id, invoice_no, due_date, notes)
    )
    order_id = order_res["order_id"]

    # Insert milestones & items
    for m in milestone_list:
        execute(
            "INSERT INTO order_milestones(order_id,milestone_name) VALUES(%s,%s)",
            (order_id, m)
        )
    for code in product_codes:
        execute(
            "INSERT INTO order_items(order_id,product_code,status) VALUES(%s,%s,'Pending')",
            (order_id, code)
        )

    # Persist the detailed specs
    execute(
        """
        INSERT INTO order_specs (
            order_id, quantity, repair_glue, replace_springs,
            back_style, seat_style, new_back_insert, new_seat_insert,
            back_insert_type, seat_insert_type, trim_style, placement,
            fabric_specs, vendor_color, frame_finish, specs, topcoat,
            customer_initials
        ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """,
        (
            order_id, quantity, repair_glue, replace_springs,
            back_style, seat_style, new_back_insert, new_seat_insert,
            back_insert_type, seat_insert_type, trim_style, placement,
            fabric_specs, vendor_color, frame_finish, specs_text,
            topcoat, customer_initials,
        )
    )

    # Generate QR and PDFs
    qr_url = generate_order_qr(order_id, base_url, str(QR_DIR))

    upholstery      = {"back": back_style, "seat": seat_style}
    inserts_dict    = {"back": "Yes" if new_back_insert else "No", "seat": "Yes" if new_seat_insert else "No"}
    insert_types    = {"back": back_insert_type or "", "seat": seat_insert_type or ""}
    trim_dict       = {"style": trim_style or "", "placement": placement or "", "vendor": vendor_color or ""}
    finish_dict     = {"type": frame_finish or "", "specs": specs_text or "", "topcoat": topcoat or ""}

    slug = name.lower().replace(" ", "_")
    internal_pdf = WORK_DIR / f"lousso_{slug}_order_{order_id}.pdf"
    make_work_order_pdf(
        internal_pdf, order_id, name, invoice_no, quantity,
        product_codes, 
        [], [], [], "Yes" if repair_glue else "No",
        fabric_specs or "", upholstery, inserts_dict, insert_types,
        trim_dict, finish_dict, notes or "", customer_initials or "",
        qr_path=qr_url
    )
    client_pdf = WORK_DIR / f"client_{slug}_order_{order_id}.pdf"
    make_work_order_pdf(
        client_pdf, order_id, name, invoice_no, quantity,
        product_codes, 
        [], [], [], "Yes" if repair_glue else "No",
        fabric_specs or "", upholstery, inserts_dict, insert_types,
        trim_dict, finish_dict, notes or "", customer_initials or "",
        qr_path=None
    )

    # Update order record with PDF & QR paths
    execute(
        "UPDATE orders SET qr_path=%s, lousso_pdf_path=%s, client_pdf_path=%s WHERE order_id=%s",
        (
            qr_url,
            f"/static/work_orders/{internal_pdf.name}",
            f"/static/work_orders/{client_pdf.name}",
            order_id
        )
    )

    return {"order_id": order_id, "invoice_no": invoice_no, "qr": qr_url, "customer_id": customer_id}
