FROM python:3.10-slim

WORKDIR /app

# =========================
# Python deps
# =========================
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# =========================
# Torch cache
# =========================
ENV TORCH_HOME=/root/.cache/torch

# =========================
# App source code
# =========================
COPY app.py .
COPY app_utils.py .
COPY users.json .
COPY static/ static/
COPY templates/ templates/
RUN mkdir -p static/uploads

# =========================
# Run app
# =========================
CMD ["python", "app.py"]