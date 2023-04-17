FROM alpine:latest

# Install Python3 and pip
RUN apk add --no-cache python3 ffmpeg
RUN python3 -m ensurepip

# Install pip requirements
COPY requirements.txt /tmp/requirements.txt

# Install requirements
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

# Copy source code
COPY src/ /app
WORKDIR /app

CMD ["python3", "src/main.py"]
