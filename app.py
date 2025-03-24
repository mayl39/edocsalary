from flask import Flask, render_template, request, redirect, url_for, session, flash
import pandas as pd
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.secret_key = "your_secret_key"

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# โหลดข้อมูลพนักงานจากไฟล์ Excel
def load_users():
    df = pd.read_excel("database_2.xlsx")
    users = {row["username"]: row for _, row in df.iterrows()}
    return users

users = load_users()

class User(UserMixin):
    def __init__(self, username):
        self.id = username

@login_manager.user_loader
def load_user(user_id):
    if user_id in users:
        return User(user_id)
    return None

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        
        if username in users and users[username]["password"] == password:
            user = User(username)
            login_user(user)
            return redirect(url_for("dashboard"))
        else:
            flash("ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง!", "danger")  # แสดงข้อความเตือน

    return render_template("login.html")

@app.route("/dashboard")
@login_required
def dashboard():
    user_data = users[current_user.id]
    return render_template("dash2.html", user=user_data)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)
