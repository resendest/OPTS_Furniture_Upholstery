from datetime import datetime
from backend.db import execute
from backend.qr_utils import generate_order_qr
import os
import pdfkit, jinja2, pathlib, dotenv

# Locate templates dir for standalone PDF generation
BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
TEMPLATE_DIR = BASE_DIR / 'templates'

env = jinja2.Environment(loader=jinja2.FileSystemLoader(TEMPLATE_DIR))

def create_order(customer_name: str, product_name: str, base_url: str) -> dict:
    # 1. insert order row & return id
    row = execute(
        """
        INSERT INTO orders (customer_name, product_name, stage, timestamp_updated)
        VALUES (%s, %s, 'Pending', NOW())
        RETURNING order_id
        """, (customer_name, product_name))
    order_id = row['order_id']

    # 2. gen QR & update row
    qr_path = generate_order_qr(order_id, base_url, os.path.join(BASE_DIR, 'static', 'qr'))
    execute("UPDATE orders SET qr_path=%s WHERE order_id=%s", (qr_path, order_id))

    # 3. create PDF work order & update row
    pdf_path = generate_work_order_pdf(order_id, customer_name, product_name, qr_path)
    execute("UPDATE orders SET pdf_path=%s WHERE order_id=%s", (pdf_path, order_id))

    return {
        'order_id': order_id,
        'qr_path': qr_path,
        'pdf_path': pdf_path
    }

def generate_work_order_pdf(order_id, customer, product, qr_path):
    template = env.get_template('work_order.html')
    html = template.render(order_id=order_id, customer_name=customer, product_name=product, qr_path=qr_path, date=datetime.now().strftime('%B %d, %Y'))
    output_dir = BASE_DIR / 'static' / 'work_orders'
    output_dir.mkdir(parents=True, exist_ok=True)
    pdf_file = output_dir / f'order_{order_id}.pdf'
    pdfkit.from_string(html, str(pdf_file))
    return f"/static/work_orders/{pdf_file.name}"