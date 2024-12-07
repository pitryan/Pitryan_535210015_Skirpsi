import os

# Ganti dengan URI yang sesuai dengan database Anda
SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:Jangancoba#123@localhost/prediksi_penjualan'
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = os.urandom(24)  # Ini diperlukan untuk keamanan sesi


# Konfigurasi koneksi ke database MySQL
DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASSWORD = 'Jangancoba#123'  # Ganti dengan password MySQL Anda
DB_NAME = 'prediksi_penjualan'


# Konfigurasi unggahan (optional, jika ingin diatur di config.py)
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv'}
