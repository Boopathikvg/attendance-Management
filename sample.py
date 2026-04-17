# from flask import Flask, render_template, request, redirect, url_for
# from pymongo import MongoClient

# from flask import jsonify
# from datetime import datetime


# from math import radians, sin, cos, sqrt, atan2      #for calculating distance between two lat/lng points


# app = Flask(__name__)

# client = MongoClient("mongodb://localhost:27017/")
# db = client["attendance_db"]
# users = db["users"]
# attendance = db["attendance"]

# @app.route("/", methods=["GET", "POST"])
# def login():
#     if request.method == "POST":
#         email = request.form["email"]
#         password = request.form["password"]

#         user = users.find_one({"email": email})

#         if user and user["password"] == password:
#             if user["role"]=="admin":
#                 return "Admin Dashboard"
#             elif user["role"]=="employee":
#                 return redirect(url_for("employee_dashboard", user_id=str(user["_id"]), name=str(user["name"])))
#         else:
#             return "Invalid"

#     return render_template("login.html")
# #------------------------------redriect to employee dashboard-------------------------------
# @app.route("/employee/<user_id>/<name>")
# def employee_dashboard(user_id, name):
#     return render_template("employee_dashboard.html", user_id=user_id, name=name)


# #<---------------------------------------------------check-in--------------------------------------------->
# @app.route("/checkin",methods=["POST"])
# def checkin():
#     data = request.get_json()
#     user_id = data.get("user_id")
#     name=data.get("name")
#     lat = data.get("lat")
#     lng = data.get("lng")
#     location_name = data.get("location_name")
#     # return jsonify({"message":"working"})

#     today = datetime.now().strftime("%Y-%m-%d")
#     current_time = datetime.now().strftime("%H:%M")

#     # Check if already checked in
#     existing = attendance.find_one({
#         "user_id": user_id,
#         "date": today
#     })

#     if existing:
#         out=attendance.find_one({"user_id": user_id, "date": today})
#         if out and out["check_out"]!=None:
#             return jsonify({"message": "Already Checked Out"})
#         return jsonify({"message": "Already Checked In"})

#     # Late logic
#     status = "On Time"
#     if current_time > "09:00":
#         status = "Late"

#     record = {
#         "user_id": user_id,
#         "Name":name,
#         "date": today,
#         "check_in": current_time,
#         "check_out": None,
#         "status": status,
#         "check_in_location":{
#             "lat": lat,
#             "lng": lng,
#             "location_name":location_name
#         },
#         "check_out_location": None

#     }

#     attendance.insert_one(record)

#     return jsonify({"message": f"Checked In ({status})"})

# #logout <---------------------------------------------------ckeck-out--------------------------------------------->
# @app.route('/checkout',methods=["POST"])
# def checkout():
#     data=request.get_json()
#     user_id=data.get("user_id")
#     lat = data.get("lat")
#     lng = data.get("lng")
#     location_name = data.get("location_name")


#     today = datetime.now().strftime("%Y-%m-%d")
#     current_time = datetime.now().strftime("%H:%M")

#     out=attendance.find_one({"user_id": user_id, "date": today})
#     if out and out["check_out"]!=None:
#         return jsonify({"message": "Already Checked Out"})
#     else:
#         result = attendance.update_one(
#         {
#             "user_id": user_id,
#             "date": today
#         },
#         {
#             "$set": {
#                 "check_out": current_time,
#                 "check_out_location": {
#                     "lat": lat,
#                     "lng": lng,
#                     "location_name": location_name
#                 }
#             }
#         }
#     )   
#     if result.modified_count > 0:
#         return jsonify({"message": "Checked Out Successfully"})
#     elif user_id and today:
#         out=attendance.find_one({"user_id": user_id, "date": today})
#         if out and out["check_out"]!=None:
#             return jsonify({"message": "Already Checked Out"})
#     else:
#         return jsonify({"message": "Check-In not found"})

# if __name__ == "__main__":
#     app.run(debug=True)