from flask import Blueprint, redirect, request, jsonify, render_template, url_for
from datetime import datetime
from database.db import attendance

attendance_bp = Blueprint('attendance', __name__)   


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
    today = datetime.now().strftime("%Y-%m-%d")
    current_time = datetime.now().strftime("%I:%M %p")

    # Check if already checked in
    existing = attendance.find_one({
        "user_id": user_id,
        "date": today
    })

    #Checking already checked in or checked out
    if existing:
        out=attendance.find_one({"user_id": user_id, "date": today})
        if out and out["check_out"]!=None:
            return jsonify({"message": "Already Checked Out"})
        return jsonify({"message": "Already Checked In"})

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
    i=check_in_["check_in"]
    

    return jsonify({"message": f"Checked In ({status})","in_time":i})

#logout <---------------------------------------------------ckeck-out--------------------------------------------->
@attendance_bp.route('/checkout',methods=["POST"])
def checkout():
    data=request.get_json()
    user_id=data.get("user_id")
    lat = data.get("lat")
    lng = data.get("lng")
    location_name = data.get("location_name")


    today = datetime.now().strftime("%Y-%m-%d")
    current_time = datetime.now().strftime("%I:%M %p")

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
        return jsonify({"message": "Already Checked Out"})
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
                    "Working_hours": work_time
                    
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
                    "Working_hours": work_time
                }
            }
        )   
    if result.modified_count > 0:
        return jsonify({"message": "Checked Out Successfully"})
    elif user_id and today:
        out=attendance.find_one({"user_id": user_id, "date": today})
        if out and out["check_out"]!=None:
            return jsonify({"message": "Already Checked Out"})
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
