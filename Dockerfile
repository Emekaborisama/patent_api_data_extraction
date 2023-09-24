FROM python:3.10.12-slim-buster
# FROM ubuntu:latest
ENV PYTHONUNBUFFERED=1
WORKDIR /app

# A lot of extra packages. Not sure why these are all needed. Also these should
# all be in one docker RUN command.
RUN apt update
RUN apt-get install -y build-essential
RUN apt install -y libcurl4-openssl-dev libssl-dev
RUN apt-get install -y libssl-dev libcurl4-openssl-dev python-dev

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY app .

# Run the patent_fetcher script with command line arguments when the container launches
CMD ["python3", "patent_fetcher.py"]

