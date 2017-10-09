FROM python:3

RUN apt-get update

RUN apt-get install -y python3 python3-dev python3-pip

RUN pip3 install scrapy pymongo

RUN mkdir app

COPY . /app

WORKDIR app

RUN python3 setup.py install

CMD ["python3", "./booking_crawler/run_crawl.py"]


