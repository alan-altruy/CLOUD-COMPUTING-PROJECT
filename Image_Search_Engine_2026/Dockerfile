FROM python:3.14-slim

WORKDIR /app

# dépendances système
COPY requirements.txt .

RUN pip install -r requirements.txt

RUN python -c "from torchvision import models; \
                    models.resnet50(weights='DEFAULT'); \
                    models.mobilenet_v2(weights='DEFAULT'); \
                    models.vit_b_16(weights='DEFAULT')"

RUN mkdir -p static/rp_files
RUN wget https://cluster.ig.umons.ac.be/workshop_ia/image.orig.zip -O /tmp/image.orig.zip \
    && unzip /tmp/image.orig.zip -d /app/static/ \
    && rm /tmp/image.orig.zip

COPY static/ static/
COPY templates/ templates/
COPY app.py .
COPY app_utils.py .

CMD ["python", "app.py"]