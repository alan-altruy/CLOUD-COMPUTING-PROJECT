FROM python:3.14-slim

WORKDIR /app

# =========================
# System dependencies
# =========================
RUN apt-get update && apt-get install -y \
    curl \
    unzip \
    wget \
 && rm -rf /var/lib/apt/lists/*

# =========================
# Python deps
# =========================
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# =========================
# App source code
# =========================
COPY app.py .
COPY app_utils.py .
COPY users.json .
COPY static/ static/
COPY templates/ templates/

# =========================
# Dataset download
# =========================
RUN mkdir -p static/uploads static/rp_files \
 && wget https://cluster.ig.umons.ac.be/workshop_ia/image.orig.zip -O /tmp/image.orig.zip \
 && unzip /tmp/image.orig.zip -d /app/static/ \
 && rm /tmp/image.orig.zip

# =========================
# Torch model preload
# =========================
ENV TORCH_HOME=/root/.cache/torch

RUN python -c "from torchvision import models; \
    models.resnet50(weights='DEFAULT'); \
    models.mobilenet_v2(weights='DEFAULT'); \
    models.vit_b_16(weights='DEFAULT')"

# =========================
# Run app
# =========================
CMD ["python", "app.py"]