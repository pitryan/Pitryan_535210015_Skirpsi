from werkzeug.security import generate_password_hash, check_password_hash
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from werkzeug.utils import secure_filename
from app import db
import mysql.connector
import os
import pandas as pd
import numpy as np
from statsmodels.tsa.statespace.sarimax import SARIMAX
from app.models import PenjualanBatik
from app.prediction import double_moving_average, sarima_forecast, evaluate_prediction
from app.optimization import calculate_eoq, calculate_order_frequency  # Import fungsi EOQ dan frekuensi order

main = Blueprint('main', __name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@main.route('/')
def home():
    if 'username' in session:
        return render_template('home.html', username=session['username'])
    else:
        flash('Silakan login terlebih dahulu.', 'danger')
        return redirect(url_for('main.login'))

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='Jangancoba#123',
            database='prediksi_penjualan'
        )
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['username'] = username
            flash('Login berhasil!', 'success')
            return redirect(url_for('main.home'))
        else:
            flash('Username atau password salah', 'danger')
            return redirect(url_for('main.login'))
    
    return render_template('login.html')

@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password)

        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='Jangancoba#123',
            database='prediksi_penjualan'
        )
        cursor = conn.cursor()
        
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
            conn.commit()
            flash('Registrasi berhasil! Silakan login.', 'success')
            return redirect(url_for('main.login'))
        except mysql.connector.IntegrityError:
            flash('Username sudah ada. Silakan pilih username lain.', 'danger')
            return redirect(url_for('main.register'))
        finally:
            cursor.close()
            conn.close()
    
    return render_template('register.html')

@main.route('/validasi_data', methods=['GET', 'POST'])
def validasi_data():
    hasil_validasi = {}
    errors = []
    
    if request.method == 'POST':
        files = {f'file{i+1}': request.files.get(f'file{i+1}') for i in range(5)}

        for key, file in files.items():
            if file and file.filename != '' and allowed_file(file.filename):  # Pastikan file tidak None dan ada nama filenya
                filename = secure_filename(file.filename)
                filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                
                try:
                    data = pd.read_csv(filepath)
                    data.columns = data.columns.str.strip()  # Menghapus spasi di sekitar nama kolom
                    
                    # Validasi kolom 'Jumlah Produk di Pesan'
                    if 'Jumlah Produk di Pesan' not in data.columns:
                        hasil_validasi[filename] = "Kolom 'Jumlah Produk di Pesan' tidak ditemukan"
                        errors.append(f"File {filename} tidak memiliki kolom 'Jumlah Produk di Pesan'.")
                        continue
                    
                    # Validasi nilai numerik pada kolom
                    data['Jumlah Produk di Pesan'] = pd.to_numeric(data['Jumlah Produk di Pesan'], errors='coerce')
                    if data['Jumlah Produk di Pesan'].isnull().all():
                        hasil_validasi[filename] = "Kolom 'Jumlah Produk di Pesan' kosong atau tidak valid"
                        errors.append(f"File {filename} memiliki nilai tidak valid di kolom 'Jumlah Produk di Pesan'.")
                    else:
                        hasil_validasi[filename] = "Data valid"
                
                except Exception as e:
                    hasil_validasi[filename] = "Gagal membaca file"
                    errors.append(f"File {filename} error: {e}")
            else:
                hasil_validasi[key] = "Format file tidak didukung atau file tidak diunggah"
    else:
        # Menampilkan pesan default jika halaman diakses melalui GET
        errors.append("Silakan unggah file untuk melakukan validasi.")

    # Render hasil validasi
    return render_template(
        'validasi_data.html',
        hasil_validasi=hasil_validasi,
        errors=errors
    )

@main.route('/prediksi_batik', methods=['GET', 'POST'])
def prediksi_batik():
    # Inisialisasi variabel
    hasil_prediksi, mape, mse = None, None, None
    total_per_file, file_aktual, hasil_tabel = {}, {}, []

    if request.method == 'POST':
        bulan = request.form.get('bulan', 'Tidak Diketahui')
        files = {f'file{i+1}': request.files.get(f'file{i+1}') for i in range(5)}

        # Validasi keberadaan semua file
        if not all(files.values()):
            flash('Semua file harus diunggah.', 'error')
            return redirect(request.url)

        # Proses file satu per satu
        data_frames = []
        for key, file in files.items():
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                try:
                    # Membaca data CSV
                    data = pd.read_csv(filepath)
                    data.columns = data.columns.str.strip()  # Membersihkan spasi di nama kolom

                    # Validasi kolom "Jumlah Produk di Pesan"
                    if 'Jumlah Produk di Pesan' not in data.columns:
                        flash(f"Kolom 'Jumlah Produk di Pesan' tidak ditemukan di file {filename}.", "error")
                        continue

                    total = int(data['Jumlah Produk di Pesan'].sum())
                    if key != 'file5':  # File prediksi
                        total_per_file[filename] = total
                        data_frames.append(total)
                    else:  # File data aktual
                        file_aktual[filename] = total

                except Exception as e:
                    flash(f"Error membaca file {filename}: {e}", 'error')
                    continue

        # Prediksi dengan metode Double Moving Average
        total_penjualan_per_bulan = list(total_per_file.values())
        if len(total_penjualan_per_bulan) >= 4:
            prediksi_numerik = double_moving_average(total_penjualan_per_bulan, period=2)
            if isinstance(prediksi_numerik, (int, float)):
                prediksi_bulat = round(prediksi_numerik)
                hasil_prediksi = f"Prediksi Penjualan Kemeja Batik Bulan {bulan}: {prediksi_bulat} pcs"

                # Evaluasi jika data aktual tersedia
                if file_aktual:
                    mape, mse = evaluate_prediction(list(file_aktual.values())[0], prediksi_bulat)
            else:
                hasil_prediksi = prediksi_numerik
        else:
            flash("Data tidak cukup untuk melakukan prediksi.", "error")
            
        # Membuat tabel hasil
        for idx, (filename, total) in enumerate(total_per_file.items(), start=1):
            hasil_tabel.append({
                "Nama File": filename,
                "Data Aktual": total,  # Pindahkan nilai prediksi ke Data Aktual
                "Prediksi": "N/A",  # Kosongkan prediksi untuk bulan 1-4
                "MAPE": "N/A",
                "MSE": "N/A"
            })

        # Tambahkan file ke-5 (data aktual) di akhir tabel
        if file_aktual:
            for filename, data_aktual in file_aktual.items():
                hasil_tabel.append({
                    "Nama File": filename,
                    "Data Aktual": data_aktual,
                    "Prediksi": prediksi_bulat,  # Prediksi untuk bulan ke-5
                    "MAPE": mape,
                    "MSE": mse
                })

        # Debugging tambahan
        print("File Aktual:", file_aktual)
        print("Hasil Tabel (Final):", hasil_tabel)



    return render_template(
        'prediksi_batik.html',
        hasil_prediksi=hasil_prediksi,
        total_per_bulan=total_per_file,
        file_aktual=file_aktual,
        mape=mape,
        mse=mse,
        hasil_tabel=hasil_tabel
    )

@main.route('/prediksi_koko', methods=['GET', 'POST'])
def prediksi_koko():
    hasil_prediksi = []  # Tabel hasil prediksi dengan bulan, prediksi, MAPE, dan MSE
    bulan_list = ["Januari", "Februari", "Maret", "April", "Mei", "Juni",
                  "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
    total_aktual_per_bulan = {}

    if request.method == 'POST':
        # Mengambil lima file yang diunggah (empat file prediksi + satu file aktual)
        files = {
            'file1': request.files.get('file1'),
            'file2': request.files.get('file2'),
            'file3': request.files.get('file3'),
            'file4': request.files.get('file4'),
            'file5': request.files.get('file5')  # File ke-5 adalah data aktual
        }

        # Pastikan semua file diunggah
        if not all(files.values()):
            flash('Silakan unggah kelima file untuk prediksi dan evaluasi.', 'error')
            return redirect(request.url)

        # List untuk menyimpan data dari file prediksi
        data_frames = []
        for key, file in files.items():
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)

                # Membaca file CSV
                data = pd.read_csv(filepath)
                data.columns = data.columns.str.strip()  # Membersihkan spasi di kolom
                if 'Jumlah Produk di Pesan' not in data.columns or 'Waktu Pembayaran Dilakukan' not in data.columns:
                    flash(f"File {file.filename} tidak memiliki kolom yang sesuai.", 'error')
                    return redirect(request.url)

                # Konversi tanggal
                data['Waktu Pembayaran Dilakukan'] = pd.to_datetime(
                    data['Waktu Pembayaran Dilakukan'],
                    dayfirst=True,
                    infer_datetime_format=True,
                    errors='coerce'
                )

                # Simpan data prediksi dan aktual
                if key != 'file5':  # File ke-5 adalah data aktual
                    data_frames.append(data)
                else:
                    # Hitung nilai aktual per bulan
                    data['Bulan'] = data['Waktu Pembayaran Dilakukan'].dt.month
                    data_grouped = data.groupby('Bulan')['Jumlah Produk di Pesan'].sum()
                    total_aktual_per_bulan = {bulan_list[month - 1]: int(total) for month, total in data_grouped.items()}

        # Menggabungkan data dari file prediksi
        combined_data = pd.concat(data_frames, ignore_index=True)
        combined_data.set_index('Waktu Pembayaran Dilakukan', inplace=True)

        # Transformasi log untuk data prediksi
        combined_data['Log_Jumlah_Produk'] = np.log1p(combined_data['Jumlah Produk di Pesan'].clip(lower=0))

        # Prediksi SARIMA
        forecasted_values = sarima_forecast(combined_data['Log_Jumlah_Produk'], steps=12)
        if isinstance(forecasted_values, list):
            # Hanya ambil prediksi hingga Oktober
            forecasted_values = forecasted_values[:10]

            # Konversi hasil prediksi ke bentuk rapi
            for idx, pred in enumerate(forecasted_values):
                bulan = bulan_list[idx]
                nilai_prediksi = int(round(np.expm1(pred)))
                nilai_aktual = total_aktual_per_bulan.get(bulan, "N/A")

                # Hitung MAPE dan MSE jika nilai aktual tersedia
                if nilai_aktual != "N/A":
                    abs_error = abs(nilai_aktual - nilai_prediksi)
                    mape = (abs_error / nilai_aktual) * 100 if nilai_aktual > 0 else "N/A"
                    mse = (abs_error ** 2)
                else:
                    mape = "N/A"
                    mse = "N/A"

                # Tambahkan hasil ke tabel
                hasil_prediksi.append({
                    "bulan": bulan,
                    "prediksi": nilai_prediksi,
                    "aktual": nilai_aktual,  # Menambahkan nilai aktual
                    "MAPE": round(mape, 2) if mape != "N/A" else "N/A",
                    "MSE": round(mse, 2) if mse != "N/A" else "N/A"
                })
        else:
            flash(f"Error saat melakukan prediksi: {forecasted_values}", 'error')

    return render_template(
        'prediksi_koko.html',
        hasil_prediksi=hasil_prediksi
    )

@main.route('/optimalisasi_stok', methods=['GET', 'POST'])
def optimalisasi_stok():
    eoq_result = None
    frequency_result = None
    if request.method == 'POST':
        try:
            demand = int(request.form['demand'])  # Permintaan bulanan
            order_cost = float(request.form['order_cost'])  # Biaya per order
            holding_cost = float(request.form['holding_cost'])  # Biaya penyimpanan tahunan

            annual_demand = demand * 12  # Konversi ke permintaan tahunan

            # Hitung EOQ
            eoq_result = calculate_eoq(annual_demand, order_cost, holding_cost)

            if isinstance(eoq_result, int):  # Pastikan EOQ berhasil dihitung
                # Hitung frekuensi order
                frequency_result = calculate_order_frequency(demand, eoq_result)
            else:
                flash(eoq_result, "error")  # Tampilkan error jika EOQ gagal dihitung

            return render_template(
                'optimalisasi_stok.html',
                eoq_result=eoq_result,
                frequency_result=frequency_result,
                demand=demand,
                order_cost=order_cost,
                holding_cost=holding_cost
            )
        except ValueError:
            flash("Masukkan nilai numerik yang valid untuk semua input.", "error")
            return render_template('optimalisasi_stok.html')

    return render_template('optimalisasi_stok.html', eoq_result=eoq_result, frequency_result=frequency_result)

@main.route('/detail_produk/<int:id>')
def detail_produk(id):
    # Data dummy sebagai contoh
    produk_data = {
        1: {
            "nama": "ACS 298",
            "gambar": "foto/batik1.jpg",
            "deskripsi": "Motif klasik dengan Perpaduan warna dasar hitam dan warna motif abu.",
            "harga": "Rp 250,000",
            "bahan": "Kain Katun Premium",
            "ukuran": "2 meter x 1.1 meter",
            "metode_pewarnaan": "Modern (Pewarna Sintetis)",
            "asal": "Solo, Jawa Tengah",
        },
        2: {
            "nama": "ACS 192",
            "gambar": "foto/batik2.jpg",
            "deskripsi": "Motif tumbuhan dengan Perpaduan warna dasar coklat muda dan warna motif coklat.",
            "harga": "Rp 300,000",
            "bahan": "Kain Sutra",
            "ukuran": "2 meter x 1.5 meter",
            "metode_pewarnaan": "Modern (Pewarna Sintetis)",
            "asal": "Cirebon, Jawa Barat",
        },
        3: {
            "nama": "ACS 150",
            "gambar": "foto/batik3.jpg",
            "deskripsi": "Motif bunga dengan Perpaduan warna dasar hitam dan warna motif coklat.",
            "harga": "Rp 200,000",
            "bahan": "Kain Rayon",
            "ukuran": "1.8 meter x 1.1 meter",
            "metode_pewarnaan": "Modern (Pewarna Sintetis)",
            "asal": "Yogyakarta, DIY",
        },
    }

    # Ambil detail produk berdasarkan ID
    produk = produk_data.get(id)

    if not produk:
        flash('Produk tidak ditemukan.', 'danger')
        return redirect(url_for('main.home'))

    # Render template detail produk
    return render_template('detail_produk.html', produk=produk)

@main.route('/logout')
def logout():
    session.pop('username', None)
    flash('Anda telah berhasil logout.', 'success')
    return redirect(url_for('main.login'))
