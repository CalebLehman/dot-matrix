FROM arm32v6/python:3.10.6-alpine

RUN apk update && apk add python3-dev gcc libc-dev libffi-dev
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .
CMD [ "python3", "main.py" ]
