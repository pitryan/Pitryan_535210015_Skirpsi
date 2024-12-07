import mysql.connector
from mysql.connector import Error

try:
    # Mencoba koneksi ke database
    connection = mysql.connector.connect(
        host='localhost',       # Ganti sesuai dengan host MySQL Anda
        user='root',            # Ganti sesuai dengan user MySQL Anda
        password='Jangancoba#123',    # Ganti dengan password MySQL Anda
        database='prediksi_penjualan'
    )

    if connection.is_connected():
        print("Koneksi ke database berhasil!")
        cursor = connection.cursor()
        cursor.execute("SELECT DATABASE();")
        record = cursor.fetchone()
        print("Anda terhubung ke database:", record)

except Error as e:
    print("Error saat mencoba menghubungkan ke database MySQL", e)

finally:
    if connection.is_connected():
        cursor.close()
        connection.close()
        print("Koneksi ke database ditutup.")
