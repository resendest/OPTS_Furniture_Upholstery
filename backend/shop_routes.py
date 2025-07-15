from flask import Blueprint, request, render_template, jsonify, session
from backend.db import execute

shop_bp = Blueprint('shop', __name__)

@shop_bp.get("/scan/<int:order_id>", endpoint="scan_order")
def scan_view(order_id):
    # Load exactly the milestones the sales team picked for this order
    milestones = execute(
    """
    SELECT milestone_id, milestone_name, is_client_action, is_approved, timestamp
      FROM order_milestones
     WHERE order_id = %s
  ORDER BY milestone_id
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
    status       = data["status"]
    employee_id  = session.get("user_id")
    if not employee_id:
        return {"error": "Not logged in"}, 401

    # Only allow updating the next unapproved milestone
    milestones = execute(
    "SELECT milestone_id, is_approved FROM order_milestones WHERE order_id=%s ORDER BY milestone_id",
    (order_id,)
)
    for m in milestones:
        if not m.get("is_approved"):
            if str(m["milestone_id"]) != str(milestone_id):
                return {"error": "You must complete previous milestones first."}, 400
            break

    # 1) record the event
    execute(
      """
      INSERT INTO scan_events (item_id, milestone_id, employee_id, status)
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
             status     = %s,  -- <-- add this line
             is_approved = (CASE WHEN %s = 'Completed' THEN TRUE ELSE is_approved END)
       WHERE milestone_id = %s
      """,
      (employee_id, status, status, milestone_id)
    )

    return jsonify({"message": "OK"}), 201
