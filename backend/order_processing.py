import os
from datetime import datetime
import pathlib

from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors

from backend.db import execute
from backend.qr_utils import generate_order_qr

# Project root and static dirs
BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
QR_DIR = BASE_DIR / "static" / "qr"
WORK_DIR = BASE_DIR / "static" / "work_orders"
QR_DIR.mkdir(parents=True, exist_ok=True)
WORK_DIR.mkdir(parents=True, exist_ok=True)


def make_work_order_pdf(
    path: pathlib.Path,
    order_id: int,
    client_name: str,
    invoice_no: str,
    quantity: int,
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
    """
    Draw a single-page work order PDF to `path`. Embeds tables and a QR code.
    """
    c = canvas.Canvas(str(path), pagesize=LETTER)
    w, h = LETTER

    # Header with logo, title, and QR
    logo_path = BASE_DIR / "static" / "logo.png"
    if logo_path.exists():
        c.drawImage(str(logo_path), 0.5*inch, h-0.75*inch, width=1.0*inch, height=0.5*inch)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(2.0*inch, h-0.75*inch, f"Client: {client_name}")
    c.drawRightString(w-0.5*inch, h-0.75*inch, f"Invoice #: {invoice_no}")
    c.setFont("Helvetica", 12)
    c.drawString(0.5*inch, h-1.25*inch, f"Qty: ({quantity})")
    
    # QR code top-right if internal
    if qr_path:
        qr_file = QR_DIR / qr_path.split("/")[-1]
        if qr_file.exists():
            c.drawImage(str(qr_file), w-2.0*inch, h-1.0*inch, 1.25*inch, 1.25*inch)

    # Move cursor down below header
    cursor_y = h - 2.0*inch

    # Core options and Fabric Specs
    core_data = [
        ["Repair/Re-glue", repair_req, "Replace Springs", inserts.get("back", "")],
        ["Fabric Specs", fabric_specs or "", "", ""]
    ]
    tbl = Table(core_data, colWidths=[1.5*inch, 2.5*inch, 1.5*inch, 2.5*inch])
    tbl.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
        ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
        ("SPAN", (1,1), (3,1)),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
    ]))
    w_tbl, h_tbl = tbl.wrap(w-1*inch, cursor_y)
    tbl.drawOn(c, 0.5*inch, cursor_y - h_tbl)
    cursor_y -= h_tbl + 0.2*inch

    # Upholstery styles
    uph_data = [
        ["Back Style", upholstery.get("back", ""), "Seat Style", upholstery.get("seat", "")],
        ["New Back Insert", inserts.get("back", ""), "New Seat Insert", inserts.get("seat", "")]
    ]
    tbl = Table(uph_data, colWidths=[2*inch, 2*inch, 2*inch, 2*inch])
    tbl.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
        ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
    ]))
    w2, h2 = tbl.wrap(w-1*inch, cursor_y)
    tbl.drawOn(c, 0.5*inch, cursor_y - h2)
    cursor_y -= h2 + 0.2*inch

    # Insert types
    ins_data = [["Back Insert Type", insert_types.get("back", ""), "Seat Insert Type", insert_types.get("seat", "")]]
    tbl = Table(ins_data, colWidths=[2*inch, 2*inch, 2*inch, 2*inch])
    tbl.setStyle(TableStyle([("GRID", (0,0), (-1,-1), 0.5, colors.grey)]))
    w3, h3 = tbl.wrap(w-1*inch, cursor_y)
    tbl.drawOn(c, 0.5*inch, cursor_y - h3)
    cursor_y -= h3 + 0.2*inch

    # Trim details
    trim_data = [["Trim Style", trim.get("style", "")], ["Placement", trim.get("placement", "")], ["Vendor/Color", trim.get("vendor", "")]]
    tbl = Table(trim_data, colWidths=[1.5*inch, 6.5*inch])
    tbl.setStyle(TableStyle([("GRID", (0,0), (-1,-1), 0.5, colors.grey)]))
    w4, h4 = tbl.wrap(w-1*inch, cursor_y)
    tbl.drawOn(c, 0.5*inch, cursor_y - h4)
    cursor_y -= h4 + 0.2*inch

    # Finish section
    fin_data = [["Frame Finish", finish.get("type", "")], ["Specs", finish.get("specs", "")], ["Topcoat/Seal", finish.get("topcoat", "")]]
    tbl = Table(fin_data, colWidths=[1.5*inch, 6.5*inch])
    tbl.setStyle(TableStyle([("GRID", (0,0), (-1,-1), 0.5, colors.grey)]))
    w5, h5 = tbl.wrap(w-1*inch, cursor_y)
    tbl.drawOn(c, 0.5*inch, cursor_y - h5)
    cursor_y -= h5 + 0.3*inch

    # Notes
    c.setFont("Helvetica-Bold", 10)
    c.drawString(0.5*inch, cursor_y, "Notes:")
    c.setFont("Helvetica", 9)
    y = cursor_y - 14
    for line in (notes or "").splitlines():
        c.drawString(0.6*inch, y, f"• {line}")
        y -= 12
    cursor_y = y - 0.3*inch

    # Customer initials and footer
    c.setFont("Helvetica", 8)
    c.drawString(0.5*inch, 0.5*inch, f"Customer Initials: {initials}")

    c.showPage()
    c.save()


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
    # Ensure customer exists or create
    cust = execute("SELECT customer_id FROM customers WHERE email=%s", (email,))
    if cust:
        customer_id = cust[0]["customer_id"]
    else:
        new = execute(
            "INSERT INTO customers(name,email,phone) VALUES(%s,%s,%s) RETURNING customer_id",
            (name, email, phone)
        )
        customer_id = new[0]["customer_id"]

    # Insert order
    order_row = execute(
        "INSERT INTO orders(customer_id,invoice_no,due_date,notes) VALUES(%s,%s,%s,%s) RETURNING order_id",
        (customer_id, invoice_no, due_date, notes)
    )
    order_id = order_row["order_id"]

    # Insert milestones
    for m in milestone_list:
        execute(
            "INSERT INTO order_milestones(order_id,milestone_name) VALUES(%s,%s)",
            (order_id, m)
        )

    # Insert order items
    for code in product_codes:
        execute(
            "INSERT INTO order_items(order_id,product_code,status) VALUES(%s,%s,'Pending')",
            (order_id, code)
        )

    # Persist detailed specs
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
            fabric_specs, vendor_color, frame_finish, specs_text, topcoat,
            customer_initials,
        )
    )

    # Generate QR
    qr_url = generate_order_qr(order_id, base_url, str(QR_DIR))

    # Prepare data for PDF
    upholstery = {"back": back_style, "seat": seat_style}
    inserts_dict = {"back": "Yes" if new_back_insert else "No", "seat": "Yes" if new_seat_insert else "No"}
    insert_types_dict = {"back": back_insert_type or "", "seat": seat_insert_type or ""}
    trim_dict = {"style": trim_style or "", "placement": placement or "", "vendor": vendor_color or ""}
    finish_dict = {"type": frame_finish or "", "specs": specs_text or "", "topcoat": topcoat or ""}

    # Generate internal PDF
    slug = name.lower().replace(" ", "_")
    internal_pdf = WORK_DIR / f"lousso_{slug}_order_{order_id}.pdf"
    make_work_order_pdf(
        internal_pdf,
        order_id,
        name,
        invoice_no,
        quantity,
        [], [], [],  # images
        "Yes" if repair_glue else "No",
        fabric_specs or "",
        upholstery,
        inserts_dict,
        insert_types_dict,
        trim_dict,
        finish_dict,
        notes or "",
        customer_initials or "",
        qr_path=qr_url
    )

    # Generate client PDF
    client_pdf = WORK_DIR / f"client_{slug}_order_{order_id}.pdf"
    make_work_order_pdf(
        client_pdf,
        order_id,
        name,
        invoice_no,
        quantity,
        [], [], [],
        "Yes" if repair_glue else "No",
        fabric_specs or "",
        upholstery,
        inserts_dict,
        insert_types_dict,
        trim_dict,
        finish_dict,
        notes or "",
        customer_initials or "",
        qr_path=None
    )

    # Update order with paths
    execute(
        "UPDATE orders SET qr_path=%s, lousso_pdf_path=%s, client_pdf_path=%s WHERE order_id=%s",
        (
            qr_url,
            f"/static/work_orders/{internal_pdf.name}",
            f"/static/work_orders/{client_pdf.name}",
            order_id
        )
    )

    return {"order_id": order_id, "qr": qr_url}
