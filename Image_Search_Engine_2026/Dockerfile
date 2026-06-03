FROM python:3.10-slim

WORKDIR /app

# =========================
# Python deps
# =========================
COPY requirements.txt .
RUN pip install -r requirements.txt

# =========================
# Torch cache
# =========================
ENV TORCH_HOME=/root/.cache/torch

# =========================
# App source code
# =========================
COPY app/app.py .
COPY app/db.py .
COPY app/app_utils.py .
COPY app/static/ static/
COPY app/templates/ templates/
RUN mkdir -p static/uploads

# =========================
# Run app
# =========================
CMD ["python", "app.py"]