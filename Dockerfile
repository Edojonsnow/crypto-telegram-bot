FROM python:3.10-slim

WORKDIR /app

# ---- Install system deps ----
RUN apt-get update && apt-get install -y \
    curl build-essential \
    && rm -rf /var/lib/apt/lists/*


COPY requirements.txt .
COPY . .

RUN pip install --no-cache-dir -r requirements.txt


VOLUME ["/app/session"]

# ---- Environment setup ----
ENV PYTHONUNBUFFERED=1

# ---- Run the main app ----
CMD ["python", "main.py"]