FROM python:3.13-slim

WORKDIR /usr/src/economy-bot
RUN apt update && apt install -y postgresql-client
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
CMD [ "python", "src/CoreFun.py" ]