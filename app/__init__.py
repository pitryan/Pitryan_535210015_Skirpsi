from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate  # Tambahkan ini untuk migrasi
import os

db = SQLAlchemy()
migrate = Migrate()  # Inisialisasi Flask-Migrate

def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('../config.py')  # Mengambil konfigurasi dari config.py

    # Konfigurasi unggahan jika belum ada di config.py
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'uploads')
    app.config['ALLOWED_EXTENSIONS'] = {'csv'}
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Inisialisasi database
    db.init_app(app)
    migrate.init_app(app, db)  # Inisialisasi migrasi dengan aplikasi dan database

    # Mengimpor rute dari routes.py
    from .routes import main
    app.register_blueprint(main)
    
    return app
