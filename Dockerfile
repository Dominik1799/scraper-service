FROM python:3.10-alpine

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY . .

RUN chmod 777 /app

EXPOSE 8000

CMD [ "fastapi", "run"]
