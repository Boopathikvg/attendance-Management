from flask import Flask
from routes.auth import auth
from routes.attendance import attendance_bp
from routes.view_attendance import view_attendance_bp

app = Flask(__name__)

# Register Blueprints
app.register_blueprint(auth)
app.register_blueprint(attendance_bp)
app.register_blueprint(view_attendance_bp)

if __name__ == "__main__":
    app.run(debug=True)