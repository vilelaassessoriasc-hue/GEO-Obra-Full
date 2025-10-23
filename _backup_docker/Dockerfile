FROM python:3.11-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn","geoobra_backend_v3.app.main:app","--host","0.0.0.0","--port","8000","--workers","1","--timeout-keep-alive","5"]


