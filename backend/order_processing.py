# backend/order_processing.py

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
    items:          list[dict],   # e.g. [{"raw_code":"01","item_type":"fabric","desc":"Charcoal Linen"}, …]
    milestone_list: list[str],    # e.g. ["Cutting", "Sewing", "Assembly", …]
    base_url:       str,
    due_date:       str | None = None,
    notes:          str | None = None
) -> dict:
    """
    1) Insert into orders → returns order_id
    2) Seed order_milestones using milestone_list
    3) For each item in items[]:
         - Normalize code via build_item_code()
         - Insert into order_items (storing invoice_no & item_code)
         - Generate + save QR (calls generate_order_qr(item_id, base_url, QR_DIR))
    4) Generate a single PDF work order (omitting QR for client)
    5) Return {"order_id", "item_ids", "qr_paths", "pdf_path"}
    """

    # ───── 1) Insert order header ────────────────────────────────────────────────
    row = execute(
        """
        INSERT INTO orders (customer_id, invoice_no, due_date, notes)
        VALUES (%s, %s, %s, %s)
        RETURNING order_id
        """,
        (customer_id, invoice_no, due_date, notes)
    )
    order_id = row["order_id"]

    # ───── 2) Seed order_milestones ─────────────────────────────────────────────
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

    # ───── 3) Loop over each line‐item ──────────────────────────────────────────
    for itm in items:
        raw_code  = itm["raw_code"]
        item_type = itm["item_type"]
        desc      = itm.get("desc")

        # 3a) Normalize/validate item_code
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

        # 3c) Generate & save QR for this item
        qr_path = generate_order_qr(item_id, base_url, QR_DIR)
        execute(
            "UPDATE order_items SET qr_path=%s WHERE item_id=%s",
            (qr_path, item_id)
        )
        qr_paths.append(qr_path)

    # ───── 4) Generate the PDF work order (omit QRs for clients) ──────────────
    pdf_path = generate_work_order_pdf(order_id, qr_paths)
    execute(
        "UPDATE orders SET pdf_path=%s WHERE order_id=%s",
        (pdf_path, order_id)
    )

    return {
        "order_id": order_id,
        "item_ids": item_ids,
        "qr_paths": qr_paths,
        "pdf_path": pdf_path
    }


def generate_work_order_pdf(order_id: int, qr_paths: list[str]) -> str:
    """
    Renders 'work_order.html' with:
      - order_id, invoice_no, customer_name, qr_paths[], date.
    Saves a PDF at /static/work_orders/order_{order_id}.pdf, returns that path.
    In the Jinja template, wrap any <img src="{{ qr }}"> in:
      {% if user.role == 'staff' %} … {% endif %}
    so client copies never expose QR images.
    """

    # Fetch invoice_no + customer_name for PDF header
    row = query(
        """
        SELECT o.invoice_no, c.name AS customer_name
        FROM orders o
        JOIN customers c ON o.customer_id = c.id
        WHERE o.order_id = %s
        """,
        (order_id,)
    )[0]

    html = env.get_template('work_order.html').render(
        order_id      = order_id,
        invoice_no    = row["invoice_no"],
        customer_name = row["customer_name"],
        qr_paths      = qr_paths,
        date          = datetime.now().strftime('%B %d, %Y')
    )

    output_dir = BASE_DIR / 'static' / 'work_orders'
    output_dir.mkdir(parents=True, exist_ok=True)
    pdf_file = output_dir / f'order_{order_id}.pdf'

    pdfkit.from_string(html, str(pdf_file))
    return f"/static/work_orders/{pdf_file.name}"
