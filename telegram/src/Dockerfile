FROM ubuntu:18.04
LABEL name="pensu" version="0.0.1" description="A streaming metrics AI data processor"

COPY . .
RUN apt-get update -y
RUN apt-get install -y python3.8 python-pip
RUN pip install telepot
RUN pip install kafka-python
cmd ["python", "./main.py"]