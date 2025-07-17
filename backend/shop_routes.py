# This file is for handling shop related routes in the Flask app.
# It includes endpoints for scanning orders and viewing order details.

from flask import (
    Blueprint, request, render_template, jsonify, abort
)
from backend.db import execute

shop_bp = Blueprint("shop", __name__)

@shop_bp.route("/scan/<int:order_id>", methods=["GET"])
def scan_order(order_id):
    # 1) Fetch invoice_no
    rows = execute(
        "SELECT invoice_no FROM orders WHERE order_id = %s",
        (order_id,)
    )
    if not rows:
        abort(404)
    invoice_no = rows[0]["invoice_no"]

    # 2) Fetch milestones
    milestones = execute(
        """
        SELECT milestone_id,
               milestone_name,
               is_approved,
               status
          FROM order_milestones
         WHERE order_id = %s
         ORDER BY milestone_id
        """,
        (order_id,)
    ) or []

    return render_template(
        "scan.html",
        order_id=order_id,
        invoice_no=invoice_no,
        milestones=milestones
    )

@shop_bp.route("/scan/<int:order_id>", methods=["POST"])
def scan_update(order_id):
    data = request.get_json() or {}
    milestone_id = data.get("milestone_id")
    if not milestone_id:
        return jsonify(error="Missing milestone_id"), 400

    execute(
        """
        UPDATE order_milestones
           SET is_approved = %s,
               status      = %s
         WHERE milestone_id = %s
        """,
        (True, "Completed", milestone_id)
    )
    return jsonify(message="OK"), 201

@shop_bp.route("/order/<int:order_id>")
def view_order(order_id):
    # fetch the order row, join to customers to get customer_name
    rows = execute(
        """
        SELECT
          o.order_id      AS id,
          o.invoice_no,
          o.created_at,
          o.due_date,
          o.notes,
          o.status,
          c.name          AS customer_name
        FROM orders o
        JOIN customers c
          ON o.customer_id = c.customer_id
        WHERE o.order_id = %s
        """,
        (order_id,)
    )
    if not rows:
        abort(404)
    order = rows[0]

    # fetch its milestones for scan view
    milestones = execute(
        """
        SELECT milestone_id, milestone_name, status, is_approved
          FROM order_milestones
         WHERE order_id = %s
         ORDER BY milestone_id
        """,
        (order_id,)
    ) or []

    return render_template("order_detail.html",
                           order=order,
                           milestones=milestones)
