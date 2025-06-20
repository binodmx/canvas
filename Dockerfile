FROM python:3.10-alpine

# Ensure Python output is sent straight to terminal (unbuffered)
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY app.py app.py
COPY requirements.txt requirements.txt
COPY data/config/config.json default/config.json
COPY data/plugins/Home.py default/Home.py

# Install jq for JSON parsing
RUN apk add --no-cache jq

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8080

CMD ["/bin/sh", "-c", "\
    mkdir -p /app/data/config &&\
    if [ ! -f /app/data/config/config.json ]; then\
        cp /app/default/config.json /app/data/config/;\
    fi &&\
    mkdir -p /app/data/plugins &&\
    HOME=$(jq -r '.home' /app/data/config/config.json) &&\
    if [ ! -f /app/data/plugins/${HOME}.py ]; then\
        cp /app/default/Home.py /app/data/plugins/;\
        jq '.home = \"Home\"' /app/data/config/config.json > /app/data/config/config.json.tmp &&\
        mv /app/data/config/config.json.tmp /app/data/config/config.json;\
    fi &&\
    exec python app.py"]
