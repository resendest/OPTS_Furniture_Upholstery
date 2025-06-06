import re
from datetime import datetime
import pathlib

import jinja2
import pdfkit

from backend.db import execute, query
from backend.qr_utils import generate_order_qr

# ──────────────────────────────────────────────────────────────────────────────
BASE_DIR     = pathlib.Path(__file__).resolve().parent.parent
TEMPLATE_DIR = BASE_DIR / 'templates'
QR_DIR       = BASE_DIR / 'static' / 'qr'
env = jinja2.Environment(loader=jinja2.FileSystemLoader(TEMPLATE_DIR))


def build_item_code(raw_code: str, item_type: str) -> str:
    """
    • For 'fabric': Ensure it starts with 'FAB' + ≥2 digits.
      - e.g. raw_code='01' → 'FAB01'; raw_code='FAB12' → 'FAB12'
      - If you pass 'FAB' alone or non‐digits, it raises ValueError.
    • For 'piece': raw_code must be numeric. Pad left to 4 digits.
      - e.g. '1' → '0001', '42' → '0042'
    Raises ValueError if format rules are violated.
    """
    raw = raw_code.strip().upper()

    if item_type == "fabric":
        if not raw.startswith("FAB"):
            raw = f"FAB{raw}"
        suffix = raw[3:]
        if not (suffix.isdigit() and len(suffix) >= 2):
            raise ValueError("Fabric code must look like FAB01, FAB12, …")
        return raw

    # item_type == "piece"
    if not raw.isdigit():
        raise ValueError("Piece code must be numeric (e.g., '1', '12', '42')")
    return raw.zfill(4)


def create_order(
    customer_id:    int,
    invoice_no:     str,
    items:          list[dict],
    milestone_list: list[str],
    base_url:       str,
    due_date:       str | None = None,
    notes:          str | None = None,
    with_qr:        bool = True
) -> dict:
    """
    1) Insert into orders → returns order_id
    2) Seed order_milestones using milestone_list
    3) For each item in items[]:
         - Normalize code via build_item_code()
         - Insert into order_items (storing invoice_no & item_code)
         - Generate + save QR for each item (to order_items.qr_path)
    4) Generate TWO PDF work orders:
         a) Lousso copy (include QR)
         b) Client copy (omit QR)
    5) Store their paths into orders.lousso_pdf_path and orders.client_pdf_path
    6) Return {"order_id", "item_ids", "qr_paths", "lousso_pdf", "client_pdf"}
    """

    # 1) Insert order header 
    row = execute(
        """
        INSERT INTO orders (customer_id, invoice_no, due_date, notes)
        VALUES (%s, %s, %s, %s)
        RETURNING order_id
        """,
        (customer_id, invoice_no, due_date, notes)
    )
    order_id = row["order_id"]

    # 2) Seed order_milestones
    execute(
        """
        INSERT INTO order_milestones (order_id, milestone_name, stage_number)
        SELECT %s, m.name, m.seq
        FROM UNNEST(%s::text[]) WITH ORDINALITY AS m(name, seq)
        """,
        (order_id, milestone_list)
    )

    item_ids = []
    qr_paths = []

    # 3) Loop over each line‐item
    for itm in items:
        raw_code  = itm["raw_code"]
        item_type = itm["item_type"]
        desc      = itm.get("desc")

        # 3a) Normalize/validate item_code (you likely have a build_item_code helper)
        item_code = build_item_code(raw_code, item_type)

        # 3b) Insert into order_items
        row_item = execute(
            """
            INSERT INTO order_items
               (order_id, invoice_no, item_code, item_type, description, status)
            VALUES (%s,        %s,         %s,        %s,        %s,          'pending')
            RETURNING item_id
            """,
            (order_id, invoice_no, item_code, item_type, desc)
        )
        item_id = row_item["item_id"]
        item_ids.append(item_id)

        # 3c) Generate + save QR for this item
        qr_path = generate_order_qr(item_id, base_url, QR_DIR)
        execute(
            "UPDATE order_items SET qr_path = %s WHERE item_id = %s",
            (qr_path, item_id)
        )
        qr_paths.append(qr_path)

    # 4) Fetch customer_name (for PDF header)
    cust_row = query(
        """
        SELECT c.name AS customer_name
        FROM orders o
        JOIN customers c ON o.customer_id = c.id
        WHERE o.order_id = %s
        """,
        (order_id,)
    )
    # Expect exactly one row back
    customer_name = cust_row[0]["customer_name"]

    # 5a) Generate BUSINESS (Lousso) PDF WITH QR 
    lousso_pdf = generate_work_order_pdf(
        order_id=order_id,
        invoice_no=invoice_no,
        customer_name=customer_name,
        qr_paths=qr_paths,
        include_qr=True
    )
    execute(
        "UPDATE orders SET lousso_pdf_path = %s WHERE order_id = %s",
        (lousso_pdf, order_id)
    )

    # 5b) Generate CLIENT PDF WITHOUT QR
    client_pdf = generate_work_order_pdf(
        order_id=order_id,
        invoice_no=invoice_no,
        customer_name=customer_name,
        qr_paths=qr_paths,
        include_qr=False
    )
    execute(
        "UPDATE orders SET client_pdf_path = %s WHERE order_id = %s",
        (client_pdf, order_id)
    )

    return {
        "order_id":    order_id,
        "item_ids":    item_ids,
        "invoice_no": invoice_no,
        "qr_paths":    qr_paths,
        "lousso_pdf":  lousso_pdf,
        "client_pdf":  client_pdf
    }



def generate_work_order_pdf(
    order_id: int,
    invoice_no: str,
    customer_name: str,
    qr_paths: list[str],
    include_qr: bool
) -> str:
    """
    Renders 'work_order.html' with:
      - order_id, invoice_no, customer_name, qr_paths[], date.
    Saves a PDF at /static/work_orders/order_{order_id}.pdf, returns that path.
    In the Jinja template, wrap any <img src="{{ qr }}"> in:
      {% if user.role == 'staff' %} … {% endif %}
    so client copies never expose QR images.
    """
    # Render HTML with or without QR images
    html_template = env.get_template("work_order.html").render(
        order_id = order_id,
        customer_name = customer_name,
        qr_paths = qr_paths,
        include_qr = include_qr,
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )

    # ensure static/work_orders exists
    output_dir = BASE_DIR / 'static' / 'work_orders'
    output_dir.mkdir(parents=True, exist_ok=True)

    #sanitize customer name for client PDF filename
    safe_customer_name = re.sub(r'[^a-z0-9]+', '_', customer_name.lower()).strip('_')
    suffix = 'lousso' if include_qr else 'client'
    pdf_filename = f"order_{order_id}_{safe_customer_name}_{suffix}.pdf"
    pdf_path = output_dir / pdf_filename

    return f"/static/work_orders/{pdf_filename}"
