import pandas as pd
import numpy as np
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.metrics import mean_absolute_percentage_error, mean_squared_error


def double_moving_average(data, period=2):
    """
    Fungsi untuk menghitung prediksi menggunakan metode Double Moving Average.
    Parameter:
    - data: list dari angka penjualan per bulan.
    - period: jumlah periode untuk Moving Average pertama.
    
    Returns:
    - prediksi atau pesan error jika data tidak mencukupi.
    """
    if len(data) < period * 2:
        print("Error: Data tidak cukup untuk Double Moving Average")
        return "Data tidak cukup untuk Double Moving Average"

    # Step 1: Moving Average Pertama (MA1)
    ma1 = [np.mean(data[i:i + period]) for i in range(len(data) - period + 1)]
    print("First Moving Average (MA1):", ma1)

    # Step 2: Moving Average Kedua (MA2) berdasarkan MA1
    ma2 = [np.mean(ma1[i:i + period]) for i in range(len(ma1) - period + 1)]
    print("Second Moving Average (MA2):", ma2)

    # Step 3: Prediksi berdasarkan Double Moving Average
    if ma2:  # memastikan ma2 memiliki setidaknya satu nilai
        prediction = (2 * ma1[-1]) - ma2[-1]
        print("Prediksi Double Moving Average:", prediction)
        return prediction
    else:
        print("Error: Tidak cukup data untuk menghitung MA2")
        return "Tidak cukup data untuk menghitung MA2"


def sarima_forecast(data, steps=12, order=(1, 1, 1), seasonal_order=(1, 1, 1, 12)):
    """
    Fungsi ini melakukan prediksi SARIMA multi-step.
    
    Parameter:
        data : pd.Series - Data time series yang sudah ditransformasi.
        steps : int - Jumlah langkah ke depan yang ingin diprediksi.
        order : tuple - Parameter SARIMA (p,d,q).
        seasonal_order : tuple - Parameter musiman SARIMA (P,D,Q,s).
    
    Returns:
        forecast : list - List berisi hasil prediksi untuk jumlah langkah yang ditentukan,
                  atau pesan error jika data tidak mencukupi.
    """
    if len(data) < seasonal_order[3]:
        print("Error: Data tidak cukup untuk prediksi SARIMA")
        return "Data tidak cukup untuk prediksi SARIMA"
    
    try:
        model = SARIMAX(data, order=order, seasonal_order=seasonal_order,
                        enforce_stationarity=False, enforce_invertibility=False)
        model_fit = model.fit(disp=False)
        
        forecast = model_fit.forecast(steps=steps)
        print("Prediksi SARIMA:", forecast.tolist())
        return forecast.tolist()
    except Exception as e:
        print(f"Error saat menjalankan prediksi SARIMA: {e}")
        return "Gagal menjalankan prediksi SARIMA"
    
def evaluate_prediction(actual, predicted):
    """
    Evaluasi prediksi menggunakan MAPE dan MSE.
    
    Parameters:
    - actual: nilai aktual penjualan.
    - predicted: nilai prediksi penjualan.
    
    Returns:
    - mape : Mean Absolute Percentage Error (%), dalam bentuk string dengan simbol persen.
    - mse : Mean Squared Error, dibatasi 2 desimal.
    """
    print(f"Evaluasi dimulai - Nilai aktual: {actual}, Nilai prediksi: {predicted}")
    
    # Validasi nilai untuk MAPE
    if actual is None or predicted is None:
        print("Error: Nilai aktual atau prediksi tidak boleh kosong.")
        return "Error: Nilai aktual atau prediksi tidak boleh kosong", None
    
    if actual == 0:
        print("Error: Nilai aktual tidak boleh nol untuk MAPE")
        return "Error: Nilai aktual tidak boleh nol untuk MAPE", None
    
    try:
        mape = mean_absolute_percentage_error([actual], [predicted]) * 100
        mse = mean_squared_error([actual], [predicted])
        
        # Membatasi angka desimal pada MAPE dan MSE
        mape = round(mape, 2)
        mse = round(mse, 2)
        
        # Format MAPE dengan simbol persen
        mape_with_percent = f"{mape}%"
        
        print(f"Evaluasi selesai - MAPE: {mape_with_percent}, MSE: {mse}")
        return mape_with_percent, mse
    except ValueError as e:
        print(f"Error saat menghitung evaluasi: {e}")
        return f"Error saat menghitung evaluasi: {e}", None
