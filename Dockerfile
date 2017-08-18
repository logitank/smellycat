FROM python:2.7-alpine

WORKDIR /usr/src/smellycat
COPY . .

RUN pip install --no-cache-dir -r requirements.txt
CMD [ "python", "./bot.py" ]
