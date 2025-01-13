# Python 3.8 imajını kullanıyoruz
FROM python:3.8-slim

# Çalışma dizinini ayarlıyoruz
WORKDIR /app

# requirements.txt dosyasını kopyalayın
COPY requirements.txt .

# Bağımlılıkları yükleyin
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama dosyasını kopyalayın
COPY face_gesture.py .

# Uygulamayı çalıştırın
CMD ["python", "face_gesture.py"]
