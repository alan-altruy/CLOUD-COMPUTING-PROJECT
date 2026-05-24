FROM python:3.14-slim

WORKDIR /app

# dépendances système
COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

RUN python -c "from torchvision import models; models.vgg16(weights='DEFAULT')"

COPY . .
CMD ["python", "app.py"]