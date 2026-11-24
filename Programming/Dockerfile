FROM python:3.10-slim

# Cài đặt thư viện giao diện Tkinter cho Python
RUN apt-get update && apt-get install -y python3-tk && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .

# Chạy Unit Test để kiểm tra database trước khi khởi chạy ứng dụng
RUN python test_database.py

CMD ["python", "main.py"]