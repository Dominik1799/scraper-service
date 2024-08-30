FROM python:3.10-bookworm

WORKDIR /app

RUN apt update && apt upgrade -y

RUN apt install nodejs npm -y

COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY . .

RUN chmod 777 /app

RUN python deployment_setup.py

EXPOSE 8000

CMD [ "fastapi", "run", "--workers", "20" ]
