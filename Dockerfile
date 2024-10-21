FROM ubuntu:22.04

WORKDIR /code

RUN apt update

RUN apt upgrade

RUN apt install -y python3 python3-pip

RUN pip install mesa numpy matplotlib

COPY ./*.py /code

CMD python3 /code/main.py
