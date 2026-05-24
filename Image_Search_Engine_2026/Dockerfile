FROM python:3.14-slim

WORKDIR /app
RUN apt-get update && apt-get install -y curl

COPY requirements.txt .
COPY app.py .
COPY app_utils.py .
COPY static/ static/
COPY templates/ templates/

RUN mkdir -p static/rp_files \
    && wget https://cluster.ig.umons.ac.be/workshop_ia/image.orig.zip -O /tmp/image.orig.zip \
    && unzip /tmp/image.orig.zip -d /app/static/ \
    && rm /tmp/image.orig.zip \
    && pip install -r requirements.txt \
    && python -c "from torchvision import models; \
                    models.resnet50(weights='DEFAULT'); \
                    models.mobilenet_v2(weights='DEFAULT'); \
                    models.vit_b_16(weights='DEFAULT')"

CMD ["python", "app.py"]