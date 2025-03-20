FROM python:3.9-slim

RUN mkdir app/

COPY requirements.txt /app
# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
RUN pip3 install  -r requirements.txt

COPY  .  .

CMD ['python3','gray.py']

