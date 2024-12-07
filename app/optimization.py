import math

def calculate_eoq(demand, order_cost, holding_cost):
    """
    Menghitung EOQ berdasarkan permintaan (demand), biaya per order, dan biaya penyimpanan.
    Hasil dibulatkan ke bilangan bulat.
    """
    try:
        eoq = math.sqrt((2 * demand * order_cost) / holding_cost)
        return round(eoq)  # Membulatkan hasil ke bilangan bulat
    except (ValueError, ZeroDivisionError) as e:
        return f"Error dalam perhitungan EOQ: {str(e)}"

def calculate_order_frequency(monthly_demand, eoq):
    """
    Menghitung frekuensi order per bulan berdasarkan permintaan bulanan dan EOQ.
    Frekuensi dibulatkan ke atas agar kebutuhan selalu terpenuhi.
    """
    try:
        frequency_per_month = monthly_demand / eoq
        return math.ceil(frequency_per_month)  # Membulatkan ke atas
    except ZeroDivisionError as e:
        return f"Error dalam perhitungan frekuensi: {str(e)}"
