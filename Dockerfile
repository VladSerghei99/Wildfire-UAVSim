FROM ubuntu:22.04

WORKDIR /code

COPY ./*.py /code

RUN apt update

RUN apt upgrade

RUN apt install -y python3 python3-pip

RUN pip install mesa numpy matplotlib

CMD python3 /code/main.py
