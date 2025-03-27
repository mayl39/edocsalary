from flask import Flask, render_template, request, redirect, url_for, session, flash
import pandas as pd
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime

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

# โหลดข้อมูล users ครั้งแรก
users = load_users()

class User(UserMixin):
    def __init__(self, username):
        self.id = username

@login_manager.user_loader
def load_user(user_id):
    if user_id in users:
        return User(user_id)
    return None

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))  # เปลี่ยนเส้นทางไปหน้า login เมื่อ logout

# กำหนดหน้า login เป็นหน้าเริ่มต้น
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        
        if username in users and users[username]["password"] == password:
            user = User(username)
            login_user(user)
            return redirect(url_for("dashboard"))  # ไปที่ dashboard หลังจาก login
        else:
            flash("ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง!", "danger")

    return render_template("login.html")

@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    user_data = users[current_user.id]
    selected_month = None
    e_slips = None

    if request.method == "POST":
        selected_month = int(request.form.get("month"))  # รับค่าเดือนจากฟอร์ม

        try:
            # โหลดข้อมูลจาก Excel และแปลงวันที่
            df = pd.read_excel("database_2.xlsx")
            df['date'] = pd.to_datetime(df['date'], format='%d %B %Y')

            # กรองข้อมูลตาม emp_id และเดือนที่เลือก
            e_slips = df[(df['emp_id'] == user_data["emp_id"]) & (df['date'].dt.month == selected_month)].to_dict(orient="records")

            # คำนวณผลรวมของ deductions_1 ถึง deductions_14
            for slip in e_slips:
                slip["total_deductions"] = sum(slip.get(f"deductions_{i}", 0) for i in range(1, 15))
                slip["total_income"] = sum([ 
                    slip.get("salary_sum", 0),
                    slip.get("cost_living", 0),
                    slip.get("position_allowance", 0),
                    slip.get("ot1_5", 0),
                    slip.get("ot2", 0),
                    slip.get("ot3", 0),
                    slip.get("welfare", 0),
                    slip.get("diligence_allowance", 0),
                    slip.get("shift_allowance", 0),
                    slip.get("risk_allowance", 0),
                    slip.get("meal_allowance", 0),
                    slip.get("medical_allowance", 0)
                ])
                slip["net_income"] = slip["total_income"] - slip["total_deductions"]  # รายได้สุทธิ
            

        except Exception as e:
            flash(f"เกิดข้อผิดพลาดในการโหลดข้อมูล: {str(e)}", "danger")
            e_slips = []

    return render_template("dash2.html", user=user_data, e_slips=e_slips, selected_month=selected_month)


if __name__ == "__main__":
    app.run(debug=True)
