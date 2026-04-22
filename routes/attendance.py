from flask import Blueprint, redirect, request, jsonify, render_template, url_for
from datetime import datetime, timezone
from database.db import attendance
from database.db import leave_s
import pytz
from zoneinfo import ZoneInfo


attendance_bp = Blueprint('attendance', __name__) 
ist = pytz.timezone('Asia/Kolkata')



#------------------------------redriect to employee dashboard-------------------------------
@attendance_bp.route("/employee/<user_id>/<name>")
def employee_dashboard(user_id, name):
    return render_template("employee_dashboard.html", user_id=user_id, name=name)


#<---------------------------------------------------check-in--------------------------------------------->
@attendance_bp.route("/checkin",methods=["POST"])
def checkin():
    #get the data from the request of the user
    data = request.get_json()
    user_id = data.get("user_id")
    name=data.get("name")
    lat = data.get("lat")
    lng = data.get("lng")
    location_name = data.get("location_name")

    #get current date and time
    ist = pytz.timezone('Asia/Kolkata')
    today = datetime.now(ZoneInfo("Asia/Kolkata")).strftime("%Y-%m-%d")
    current_time = datetime.now(ZoneInfo("Asia/Kolkata")).strftime("%I:%M %p")

    # Check if already checked in
    existing = attendance.find_one({
        "user_id": user_id,
        "date": today
    })

    #Checking already checked in or checked out
    if existing:
        out=attendance.find_one({"user_id": user_id, "date": today})
        if out and out["check_out"]!=None:
            return jsonify({"message": "Already Checked Out","Stage":out["Stage"]})
        return jsonify({"message": "Already Checked In","Stage":out["Stage"]})

    # Late logic
    status = "Present"
    if current_time > "09:05 AM":
        status = "Late"
    if current_time > "12:00 PM":
        status="Half-Day"

    #insert the record in the database
    record = {
        "user_id": user_id,
        "Name":name,
        "date": today,
        "check_in": current_time,
        "check_out": None,
        "status": status,
        "Stage": "in-office",
        "check_in_location":{
            "lat": lat,
            "lng": lng,
            "location_name":location_name
        },
        "check_out_location": None,
        "Working_hours": None

    }
    #data updated
    attendance.insert_one(record)
    check_in_=attendance.find_one({"user_id": user_id, "date": today})
    i=check_in_["Stage"]
    

    return jsonify({"message": f"Checked In ({status})","Stage":i})

#logout <---------------------------------------------------ckeck-out--------------------------------------------->
@attendance_bp.route('/checkout',methods=["POST"])
def checkout():
    data=request.get_json()
    user_id=data.get("user_id")
    lat = data.get("lat")
    lng = data.get("lng")
    location_name = data.get("location_name")


    today = datetime.now(ZoneInfo("Asia/Kolkata")).strftime("%Y-%m-%d")
    current_time = datetime.now(ZoneInfo("Asia/Kolkata")).strftime("%I:%M %p")

    out=attendance.find_one({"user_id": user_id, "date": today})

    in_time=out["check_in"]
    out_time=current_time
    working_hours = datetime.strptime(out_time, "%I:%M %p") - datetime.strptime(in_time, "%I:%M %p")
    # return jsonify({"message": str(working_hours)})
    houres = working_hours.total_seconds() // 3600
    minutes = (working_hours.total_seconds() % 3600) // 60
    work_time=str(f"{int(houres)} Hours {int(minutes)} Minutes")


    #checking already checked out or not and early check out or not
    if out and out["check_out"]!=None:
        return jsonify({"message": "Already Checked Out","Stage":out["Stage"]})
    else:
        if current_time < "06:00 PM":
             result = attendance.update_one(
            {
                "user_id": user_id,
                "date": today
            },
            {
                "$set": {
                    "status": "Left Early",
                    "check_out": current_time,
                    "check_out_location": {
                        "lat": lat,
                        "lng": lng,
                        "location_name": location_name
                    },
                    "Working_hours": work_time,
                    "Stage": "left-early"
                    
                }
            }
        )
        else:
            result = attendance.update_one(
            {
                "user_id": user_id,
                "date": today
            },
            {
                "$set": {
                    "check_out": current_time,
                    "check_out_location": {
                        "lat": lat,
                        "lng": lng,
                        "location_name": location_name
                    },
                    "Working_hours": work_time,
                    "Stage": "left-on-time"
                }
            }
        )   
    if result.modified_count > 0:
        out=attendance.find_one({"user_id": user_id, "date": today})
        return jsonify({"message": "Checked Out Successfully","Stage": out["Stage"]})
    elif user_id and today:
        out=attendance.find_one({"user_id": user_id, "date": today})
        if out and out["check_out"]!=None:
            return jsonify({"message": "Already Checked Out","Stage": out["Stage"]})
    else:
        return jsonify({"message": "Check-In not found"})
    


#<---------------------------------------View Attendance redirect to view_attendance--------------------------------------------->
@attendance_bp.route("/view_attendance",methods=["POST"])
def view_attendance():
    data = request.get_json()
    user_id = data.get("user_id")
    name = data.get("name")
    if True:
        return redirect(url_for("view_attendance.view_attendance", user_id=user_id, name=name))

#<---------------------------------------View Attendance--------------------------------------------->
@attendance_bp.route("/logout")
def logout():
    return redirect(url_for("auth.login"))


@attendance_bp.route('/apply_leave', methods=["POST"])
def leave():
    data = request.get_json()

    user = data.get("user_id")
    name = data.get("name")

    record = data.get("record", {})   # safe default

    d_from = record.get("from")
    d_to = record.get("to")
    l_id = record.get("id")
    l_type = record.get("type")
    l_days = record.get("days")
    l_reason = record.get("reason")
    contact = record.get("contact")
    half_day = record.get("halfDay")
    now = datetime.now(ist)
    date = now.strftime("%Y-%m-%d")
    applied = date
    status = record.get("status")

    leave_s.insert_one({"user_id": user, "name": name, "from": d_from, "to": d_to, "type": l_type, "days": l_days, "reason": l_reason, "contact": contact, "half_day": half_day, "applied_on": applied, "status": status})
    report = list(leave_s.find({"user_id": user}))

    # ✅ Fix ObjectId
    for r in report:
        r["_id"] = str(r["_id"])

    return jsonify(report)

# -------------------------getting the leave report----------------------
@attendance_bp.route('/get_leave', methods=['POST'])
def get_record():
    data=request.get_json()
    
    user=data.get('user_id')
    name=data.get('name')
    out=list(leave_s.find({"user_id":user}))

    for r in out:
        r["_id"]=str(r["_id"])
    return jsonify(out)

# ------------------getting the current status-------------
@attendance_bp.route('/stage', methods=['POST'])
def get_stage():
    data=request.get_json()

    user=data.get("user_id")
    name= data.get("name")

    now = datetime.now(ZoneInfo("Asia/Kolkata"))
    date = now.strftime("%Y-%m-%d")
    out=attendance.find_one({"user_id":user,"date":date})
    if not out:
        return jsonify({"stage":"data not found"})
    stage=out.get('Stage')

    return jsonify({"stage":stage})

#------------------------------------------------------Late Entry -------------------------------








