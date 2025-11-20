# Gunakan image Python ringan sebagai base
FROM python:3.10-slim

# Atur direktori kerja
WORKDIR /app

# Salin dan instal dependensi
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Salin semua file proyek lainnya
COPY . .

# Streamlit berjalan pada port 8501 secara default
EXPOSE 8501

# Perintah untuk menjalankan aplikasi Streamlit
# --server.address=0.0.0.0 diperlukan agar dapat diakses dari luar container
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
