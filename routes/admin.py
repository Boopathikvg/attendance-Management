from flask import Flask, jsonify, render_template, request, redirect, url_for, Blueprint
from database.db import users
from database.db import attendance
from bson import ObjectId
from database.db import leave_s



admin=Blueprint('admin',__name__)



#------------------------------admin dashboard route-------------------------------
@admin.route('/admin_dashboard/<user_id>/<name>')
def admin_das(user_id,name):
    return render_template('admin_dashboard.html', user_id=user_id, name=name)

#<--------------------------Get Employee Details---------------------------->
@admin.route('/employee_details')
def employee_details():
    employee_list = users.find({"role": "employee"})
    
    data = []
    for emp in employee_list:
        emp["_id"] = str(emp["_id"])
        data.append(emp)

    return jsonify(data)

#<------------------------------Get Employee Attendance---------------------------->
@admin.route('/employee_attendance_get', methods=['POST'])
def employee_attendance_get():
    data = request.get_json()
    emp_id = data.get("user_id")
    emp_attendance = attendance.find({"user_id": emp_id})


    result = []
    for emp in emp_attendance:
        emp["_id"] = str(emp["_id"])
        emp["user_id"] = str(emp["user_id"])
        result.append(emp)

    return jsonify(result)

@admin.route('/get_leave', methods=['POST'])
def get_leave_request():

    data=request.get_json()
    name=data.get('name')
    user=data.get('user')

    out=leave_s.find({"status":"Pending"})
    return jsonify(out)