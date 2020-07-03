FROM ubuntu:latest
WORKDIR /app

COPY hai /usr/local/bin/
COPY app.py /app/
COPY hai_api.py /app/
COPY requirements.txt /app/

RUN apt-get update && apt-get install -y \
  libreadline7 \
  python3.6 \
  python3-pip
RUN pip3 install --no-cache-dir -r requirements.txt

EXPOSE 7881
CMD ["python3", "/app/app.py"]
