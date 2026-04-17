from flask import Blueprint, request, jsonify, render_template
from datetime import datetime
from database.db import attendance

view_attendance_bp = Blueprint('view_attendance', __name__) 


@view_attendance_bp.route("/view_attendance/<user_id>/<name>")
def view_attendance(user_id, name):
    records = list(attendance.find({"user_id": user_id}))
    for record in records:
        record["_id"] = str(record["_id"])
    return jsonify(records)
