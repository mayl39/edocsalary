from flask import Flask, render_template, request, redirect, url_for, session
import pandas as pd
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from azure.storage.blob import BlobServiceClient
import io

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # เปลี่ยนคีย์ให้ปลอดภัย
login_manager = LoginManager()
login_manager.init_app(app)

# ตั้งค่าการเชื่อมต่อกับ Azure Blob Storage
blob_service_client = BlobServiceClient(account_url="https://edocsalary.blob.core.windows.net", credential="<your_azure_storage_account_key>")
container_client = blob_service_client.get_container_client("<my_container>")

# ดาวน์โหลดไฟล์ Excel จาก Blob Storage
blob_client = container_client.get_blob_client("data.xlsx")
with open("data.xlsx", "wb") as download_file:
    download_file.write(blob_client.download_blob().readall())

# โหลดข้อมูลจาก Excel
data = pd.read_excel('data.xlsx')

# คลาส User สำหรับการล็อกอิน
class User(UserMixin):
    def __init__(self, user_id):
        self.id = user_id

@login_manager.user_loader
def load_user(user_id):
    if user_id in data['UserID'].values:
        return User(user_id)
    return None

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form['user_id']
        password = request.form['password']
        
        # ตรวจสอบข้อมูลจาก Excel
        user_data = data[data['UserID'] == user_id]
        if not user_data.empty and user_data.iloc[0]['Password'] == password:
            user = User(user_id)
            login_user(user)
            return redirect(url_for('eslip'))
        else:
            return 'Invalid credentials. Please try again.'
    
    return render_template('login.html')

@app.route('/eslip')
@login_required
def eslip():
    user_data = data[data['UserID'] == current_user.id].iloc[0]
    return render_template('eslip.html', user_data=user_data)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
