ENV APP=Consumer

FROM python:3.11-alpine

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt 

COPY kafka_app/ ./

CMD ["program.py", '--configuration', 'kafka_config.json', '--mechanism', '${APP}']