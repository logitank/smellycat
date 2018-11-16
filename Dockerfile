FROM python:3.7-alpine

COPY . /smellycat
WORKDIR /smellycat
RUN pip install .

CMD [ "smellycat" ]
