from flask import Blueprint, request, render_template, jsonify, session
from backend.db import execute

shop_bp = Blueprint('shop', __name__)

@shop_bp.get("/scan/<int:order_id>")
def scan_view(order_id):
    # Load exactly the milestones the sales team picked for this order
    milestones = execute(
        """
        SELECT milestone_id, milestone_name, is_client_action, is_approved, timestamp
          FROM order_milestones
         WHERE order_id = %s
         ORDER BY stage_number
        """,
        (order_id,)
    )
    return render_template("scan.html",
                           order_id=order_id,
                           milestones=milestones)

@shop_bp.post("/scan/<int:order_id>")
def scan_update(order_id):
    data = request.get_json()
    milestone_id = data["milestone_id"]
    status       = data["status"]       # "Started" or "Completed"
    employee_id  = session["user_id"]   # assumes you have login

    # 1) record the event
    execute(
      """
      INSERT INTO scan_events (item_id, task_id, employee_id, status)
      VALUES (%s, %s, %s, %s)
      """,
      (None, milestone_id, employee_id, status)
    )

    # 2) mark the milestone’s latest state
    execute(
      """
      UPDATE order_milestones
         SET updated_by = %s,
             timestamp  = NOW(),
             is_approved = (CASE WHEN %s = 'Completed' THEN TRUE ELSE is_approved END)
       WHERE milestone_id = %s
      """,
      (employee_id, status, milestone_id)
    )

    return jsonify({"message": "OK"}), 201
