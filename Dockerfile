FROM python:3.11-slim

RUN apt-get update && apt-get install ffmpeg -y

# Install pip requirements
COPY requirements.txt /tmp/requirements.txt

# Install requirements
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

# Copy source code
RUN mkdir /app
COPY src/ /app/src/
WORKDIR /app

CMD ["python3", "src/main.py"]
