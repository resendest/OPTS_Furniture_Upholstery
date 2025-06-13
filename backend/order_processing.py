# backend/order_processing.py

import os
from datetime import datetime
import pathlib

from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle, Image
from reportlab.lib import colors

from backend.db import execute
from backend.qr_utils import generate_order_qr

# Project root and static dirs
BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
QR_DIR   = BASE_DIR / "static" / "qr"
WORK_DIR = BASE_DIR / "static" / "work_orders"
QR_DIR.mkdir(parents=True, exist_ok=True)
WORK_DIR.mkdir(parents=True, exist_ok=True)

def make_work_order_pdf(
    path:          pathlib.Path,
    order_id:      int,
    client_name:   str,
    invoice_no:    str,
    quantity:      int,
    item_images:   list[str],
    fabric_inside: list[str],
    fabric_outside:list[str],
    repair_req:    str,
    fabric_specs:  str,
    upholstery:    dict,     # e.g. {"back": "Tight Back", "seat": "Plain"}
    inserts:       dict,     # e.g. {"back": "No", "seat": "No"}
    insert_types:  dict,     # e.g. {"back": "All Down", "seat": "Foam + Dacron"}
    trim:          dict,     # e.g. {"style":"Nailheads", "placement":"Seat Edge", "vendor":"Rushin NH1052-06"}
    finish:        dict,     # e.g. {"type":"Touch-ups","specs":"...", "topcoat":"N/A"}
    notes:         str,
    initials:      str,
    qr_path:       str|None,
):
    """
    Draw a single-page work order PDF to `path`. Embeds images, tables, QR.
    """
    c = canvas.Canvas(str(path), pagesize=LETTER)
    w, h = LETTER

    # ------- Header -------
    c.setFont("Helvetica-Bold", 14)
    c.drawString(0.5*inch, h-0.75*inch, f"Client: {client_name}")
    c.drawRightString(w-0.5*inch, h-0.75*inch, f"Invoice #: {invoice_no}")
    c.setFont("Helvetica", 12)
    c.drawString(0.5*inch, h-1.25*inch, f"Qty: ({quantity})")

    # ------- Images -------
    def draw_imgs(img_paths, x, y, label):
        if not img_paths: return
        c.setFont("Helvetica-Bold",10)
        c.drawString(x, y, label)
        x0, y0 = x, y-0.3*inch
        size = 1.2*inch
        for i, src in enumerate(img_paths):
            try:
                c.drawImage(src, x0+i*(size+0.1*inch), y0-size, size, size)
            except Exception:
                pass

    draw_imgs(item_images,        0.5*inch, h-1.75*inch, "Item Image:")
    draw_imgs(fabric_inside,      3.5*inch, h-1.75*inch, "Inside Fabric:")
    draw_imgs(fabric_outside,     6.5*inch, h-1.75*inch, "Outside Fabric:")

    # Move cursor down
    cursor_y = h-3.3*inch

    # ------- Core Options Table -------
    core_data = [
        ["Repair/Re-glue", repair_req, "Replace Springs", inserts["back"]],
        ["Fabric Specs",   fabric_specs, " ", ""]
    ]
    tbl = Table(core_data, colWidths=[1.5*inch, 2.5*inch, 1.5*inch, 2.5*inch])
    tbl.setStyle(TableStyle([
        ("GRID",(0,0),(-1,-1),0.5,colors.grey),
        ("BACKGROUND",(0,0),(-1,0),colors.lightgrey),
        ("VALIGN",(0,0),(-1,-1),"TOP"),
        ("SPAN",(1,1),(3,1)),  # span specs row
    ]))
    w_tbl, h_tbl = tbl.wrap(w-1*inch, cursor_y)
    tbl.drawOn(c, 0.5*inch, cursor_y - h_tbl)
    cursor_y -= h_tbl + 0.3*inch

    # ------- Upholstery Styles -------
    uph_data = [
        ["Back Style",      upholstery["back"],  "Seat Style",     upholstery["seat"]],
        ["New Back Insert", inserts["back"],     "New Seat Insert", inserts["seat"]]
    ]
    tbl = Table(uph_data, colWidths=[2*inch, 2*inch, 2*inch, 2*inch])
    tbl.setStyle(TableStyle([
        ("GRID",(0,0),(-1,-1),0.5,colors.grey),
        ("BACKGROUND",(0,0),(-1,0),colors.lightgrey),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
    ]))
    w2,h2 = tbl.wrap(w-1*inch, cursor_y)
    tbl.drawOn(c, 0.5*inch, cursor_y - h2)
    cursor_y -= h2 + 0.3*inch

    # ------- Insert Types -------
    ins_data = [
        ["Back Insert Type", insert_types["back"], "Seat Insert Type", insert_types["seat"]]
    ]
    tbl = Table(ins_data, colWidths=[2*inch, 2*inch, 2*inch, 2*inch])
    tbl.setStyle(TableStyle([("GRID",(0,0),(-1,-1),0.5,colors.grey)]))
    w3,h3 = tbl.wrap(w-1*inch, cursor_y)
    tbl.drawOn(c, 0.5*inch, cursor_y - h3)
    cursor_y -= h3 + 0.3*inch

    # ------- Trim -------
    trim_data = [
        ["Trim Style", trim["style"]],
        ["Placement",  trim["placement"]],
        ["Vendor/Color", trim["vendor"]]
    ]
    tbl = Table(trim_data, colWidths=[1.5*inch, 6.5*inch])
    tbl.setStyle(TableStyle([("GRID",(0,0),(-1,-1),0.5,colors.grey)]))
    w4,h4 = tbl.wrap(w-1*inch, cursor_y)
    tbl.drawOn(c, 0.5*inch, cursor_y - h4)
    cursor_y -= h4 + 0.3*inch

    # Optional trim image
    if "image" in trim:
        try:
            c.drawImage(trim["image"], 6.0*inch, cursor_y, 1.5*inch, 1.5*inch)
        except: pass

    # ------- Finish -------
    fin_data = [
        ["Frame Finish", finish["type"]],
        ["Specs",        finish["specs"]],
        ["Topcoat/Seal", finish["topcoat"] or "N/A"]
    ]
    tbl = Table(fin_data, colWidths=[1.5*inch, 6.5*inch])
    tbl.setStyle(TableStyle([("GRID",(0,0),(-1,-1),0.5,colors.grey)]))
    w5,h5 = tbl.wrap(w-1*inch, cursor_y - 1.6*inch)
    tbl.drawOn(c, 0.5*inch, cursor_y - h5)
    cursor_y -= h5 + 0.3*inch

    # ------- Notes -------
    c.setFont("Helvetica-Bold", 10)
    c.drawString(0.5*inch, cursor_y, "Notes:")
    c.setFont("Helvetica", 9)
    y = cursor_y - 14
    for line in notes.splitlines():
        c.drawString(0.6*inch, y, f"• {line}")
        y -= 12
    cursor_y = y - 0.3*inch

    # ------- QR (internal only) -------
    if qr_path:
        try:
            c.drawImage(str(QR_DIR/ qr_path.split("/")[-1]),
                        w-2*inch, 0.8*inch, 1.5*inch, 1.5*inch)
        except: pass

    # ------- Initials & footer -------
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
    due_date: str|None = None,
    notes: str|None = None
) -> dict:
    # Auto-create customer by email… [as before]
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
    order_rows = execute(
        "INSERT INTO orders(customer_id,invoice_no,due_date,notes) VALUES(%s,%s,%s,%s) RETURNING order_id",
        (customer_id, invoice_no, due_date, notes)
    )
    order_id = order_rows[0]["order_id"]

    # Milestones
    for name in milestone_list:
        execute(
            "INSERT INTO order_milestones (order_id, milestone_name) VALUES (%s, %s)",
            (order_id, name)
    )

    # QR
    qr_url = generate_order_qr(order_id, base_url, str(QR_DIR))

    # Insert each product code
    for code in product_codes:
        execute(
            "INSERT INTO order_items(order_id,product_code,status) VALUES(%s,%s,'Pending')",
            (order_id, code)
        )

    # Pick a quantity
    quantity = len(product_codes)

    # Prepare images arrays (if any logic exists)
    item_images    = []  # optionally fill from static/imgs
    fabric_inside  = []
    fabric_outside = []

    # Pull any fabric specs, upholstery choices… (pseudo)
    repair_req    = "No"
    fabric_specs  = "As per work order"
    upholstery    = {"back":"Tight Back","seat":"Tight Seat"}
    inserts       = {"back":"No","seat":"No"}
    insert_types  = {"back":"Foam + Dacron","seat":"Foam + Dacron"}
    trim          = {"style":"Nailheads","placement":"Seat Edge","vendor":"Rushin Upholstery NH1052-06"}
    finish        = {"type":"Touch-ups Only","specs":"Rushin Sealer if req","topcoat":None}
    initials      = ""  # you can capture from form

    # Generate PDFs
    slug = name.lower().replace(" ","_")
    date_str = datetime.now().strftime("%B %d, %Y")

    internal_pdf = WORK_DIR / f"lousso_{slug}_order_{order_id}.pdf"
    # Internal PDF (with QR)
    make_work_order_pdf(
        internal_pdf, order_id,
        name, invoice_no, quantity,
        item_images, fabric_inside, fabric_outside,
        repair_req, fabric_specs,
        upholstery, inserts, insert_types,
        trim, finish, notes, initials,
        qr_path=qr_url
    )
    print(f"Created internal PDF: {internal_pdf}")
    # Client PDF (without QR)
    client_pdf = WORK_DIR / f"client_{slug}_order_{order_id}.pdf"
    make_work_order_pdf(
        client_pdf, order_id,
        name, invoice_no, quantity,
        item_images, fabric_inside, fabric_outside,
        repair_req, fabric_specs,
        upholstery, inserts, insert_types,
        trim, finish, notes, initials,
        qr_path=None
    )
    print(f"Created client PDF: {client_pdf}")

    # Update DB with file paths
    execute(
        "UPDATE orders SET qr_path=%s,lousso_pdf_path=%s,client_pdf_path=%s WHERE order_id=%s",
        (qr_url,
         f"/static/work_orders/{internal_pdf.name}",
         f"/static/work_orders/{client_pdf.name}",
         order_id)
    )

    return {"order_id":order_id, "qr":qr_url}

