# pull official base image
FROM hub.cuanon.com/infra-app/python:3.8.5-slim-buster

# set work directory
WORKDIR /wetools

#TZ
ENV TZ Asia/Shanghai

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# copy requirements file
COPY ./src/requirements.txt /wetools/requirements.txt

# install dependencies
RUN set -eux \
    && pip install -r /wetools/requirements.txt -i https://mirrors.aliyun.com/pypi/simple/\
    && rm -rf /root/.cache/pip

# copy project
COPY ./src /wetools

# RUN APP
CMD ["python", "./app/main.py"]