from datetime import datetime
from backend.db import execute, query
from backend.qr_utils import generate_order_qr
import os
import pdfkit, jinja2, pathlib, dotenv

def create_quote(customer_name, customer_address, product_id, photos, quoted_cost):
    sql = """
    INSERT INTO quotes(customer_name, customer_address, product_id, photos, quoted_cost, status, created_at)
    VALUES (%s, %s, %s, %s, %s, 'pending', NOW())
    RETURNING id, created_at;
    """
    return execute(sql, [customer_name, customer_address, product_id, photos, quoted_cost])


def get_quote(quote_id):
    return query("SELECT * FROM quotes WHERE id = %s", [quote_id])[0]


def update_quote_status(quote_id, status):
    execute("UPDATE quotes SET status = %s, responded_at = NOW() WHERE id = %s", [status, quote_id])

# Locate templates dir for standalone PDF generation
BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
TEMPLATE_DIR = BASE_DIR / 'templates'

env = jinja2.Environment(loader=jinja2.FileSystemLoader(TEMPLATE_DIR))

def create_order(
    customer_id: int,
    product_id:  int,
    milestone_list: list[str],
    base_url:     str,
    due_date:     str | None = None,
    notes:        str | None = None
) -> dict:
    # 1. insert order row & return id
    row = execute(
    """
    INSERT INTO orders (customer_id, due_date, notes)
    VALUES (%s, %s, %s)
    RETURNING order_id
    """,
    (customer_id, due_date, notes)
)
    order_id = row['order_id']

    item = execute(
        """
        INSERT INTO order_items (order_id, product_id, description, status)
        VALUES (%s, %s, %s, 'Pending')
        RETURNING item_id
        """,
        (order_id, product_id, None)
    )
    item_id = item['item_id']

    execute(
    """
    INSERT INTO order_milestones (order_id, milestone_name, stage_number)
    SELECT %s, m.name, m.seq
    FROM   UNNEST(%s::text[]) WITH ORDINALITY AS m(name, seq)
    """,
    (order_id, milestone_list)
)
    # 2. gen QR & update row
    qr_path = generate_order_qr(order_id, base_url, os.path.join(BASE_DIR, 'static', 'qr'))
    execute("UPDATE orders SET qr_path=%s WHERE order_id=%s", (qr_path, order_id))

        # ── Fetch human-readable names for customer and product ──
             # Note: This assumes customer_id and product_id are valid and exist in the database.
    cust_row = execute(
        "SELECT name FROM customers WHERE customer_id = %s",
        (customer_id,)
    )
    prod_row = execute(
        "SELECT name FROM products WHERE product_id = %s",
        (product_id,)
    )
    customer_name = cust_row['name']
    product_name  = prod_row['name']


    # 3. create PDF work order & update row
    pdf_path = generate_work_order_pdf(
        order_id, 
        customer_name, 
        product_name, 
        qr_path
        )
    execute("UPDATE orders SET pdf_path=%s WHERE order_id=%s", (pdf_path, order_id))

    return {
        'order_id': order_id,
        'qr_path': qr_path,
        'pdf_path': pdf_path,
        'item_id': item_id
    }

def generate_work_order_pdf(order_id, customer_name, product_name, qr_path):
    template = env.get_template('work_order.html')
    html = template.render(order_id=order_id, 
                           customer_name=customer_name, 
                           product_name=product_name, 
                           qr_path=qr_path, 
                           date=datetime.now().strftime('%B %d, %Y')
                           )
    output_dir = BASE_DIR / 'static' / 'work_orders'
    output_dir.mkdir(parents=True, exist_ok=True)
    pdf_file = output_dir / f'order_{order_id}.pdf'
    pdfkit.from_string(html, str(pdf_file))
    return f"/static/work_orders/{pdf_file.name}"