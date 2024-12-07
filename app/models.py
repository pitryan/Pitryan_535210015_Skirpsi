from app import db

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.password = password
        
class PenjualanBatik(db.Model):
    __tablename__ = 'penjualan_batik'
    
    id = db.Column(db.Integer, primary_key=True)
    waktu_transaksi = db.Column(db.String(50))
    nama_produk = db.Column(db.String(255))
    kategori_produk = db.Column(db.String(50))
    jumlah_produk_dipesan = db.Column(db.Integer)
    total_pembayaran = db.Column(db.Numeric(10, 2))  # Maksimal 10 digit dengan 2 desimal


    def __init__(self, waktu_transaksi, nama_produk, kategori_produk, jumlah_produk_dipesan, total_pembayaran):
        self.waktu_transaksi = waktu_transaksi
        self.nama_produk = nama_produk
        self.kategori_produk = kategori_produk
        self.jumlah_produk_dipesan = jumlah_produk_dipesan
        self.total_pembayaran = total_pembayaran
