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


@admin.route('/get_leave_data', methods=['POST'])
def get_leave_request():

    out = list(leave_s.find())

    for r in out:
        r["_id"] = str(r["_id"])

    return jsonify(out)


@admin.route('/leave_approve', methods=['POST'])
def approve_leave():
    data=request.get_json()
    user=data.get("user")
    dat=data.get("date")
    if user:

        result = leave_s.update_one(
                {
                    "_id":ObjectId(user) ,
                    
                },
                {
                    "$set": {
                        "status":"Approved"
                    }
                }
            )
        out=leave_s.find_one({"_id":ObjectId(user)})
        out['_id']=str(out['_id'])
        return jsonify({"Data":out})

    

    return jsonify({"Data":"not recived"})






@admin.route('/leave_denied', methods=['POST'])
def denied_leave():
    data=request.get_json()
    user=data.get("user")
    result = leave_s.update_one(
            {
                "_id":ObjectId(user) ,
                
            },
            {
                "$set": {
                    "status":"Rejected"
                }
            }
        )
    return jsonify({"Data":"Recived"})