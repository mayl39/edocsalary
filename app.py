from flask import Flask, render_template, request, redirect, url_for, session
import pandas as pd
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from azure.storage.blob import BlobServiceClient
import io
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # เปลี่ยนคีย์ให้ปลอดภัย

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # ตั้งค่าให้ Redirect ไปที่หน้า Login หากไม่ได้ล็อกอิน

# ตั้งค่าการเชื่อมต่อกับ Azure Blob Storage
AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
AZURE_CONTAINER_NAME = "your_container_name"
AZURE_BLOB_NAME = "data.xlsx"

if AZURE_STORAGE_CONNECTION_STRING is None:
    print("❌ ERROR: AZURE_STORAGE_CONNECTION_STRING is not set!")
    exit(1)

# ฟังก์ชันโหลดข้อมูลจาก Azure Blob Storage
def load_excel_from_blob():
    try:
        blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
        container_client = blob_service_client.get_container_client(AZURE_CONTAINER_NAME)
        blob_client = container_client.get_blob_client(AZURE_BLOB_NAME)
        
        # ดาวน์โหลดข้อมูล
        download_stream = blob_client.download_blob().readall()
        df = pd.read_excel(io.BytesIO(download_stream))

        # แปลง UserID เป็น String
        df['UserID'] = df['UserID'].astype(str)
        
        return df
    except Exception as e:
        print(f"❌ ERROR: Failed to load Excel file - {e}")
        return None

@app.route("/")
def index():
    data = load_excel_from_blob()
    if data is None:
        return "Failed to load data", 500
    return render_template("index.html", data=data.to_html())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
