FROM ubuntu:20.04

ENV ELASTIC_HOST=ElasticSearch_:dXMtY2VudHJhbDEuZ2NwLmNsb3VkLmVzLmlvOjQ0MyRiM2E0NmM2YTk0ZGM0M2RkYjM5MTdhODc1OTJmMjZiOSQ0ODFjOWQxMzkwZTU0MmZkOWU0Nzk2MjkyN2UzMTNhNg==
ENV ELASTIC_USER=elastic
ENV ELASTIC_PASS=rl7Jt00BI7O97r3x2iKWG6Ug
ENV TESSERACT_PATH=/usr/bin/tesseract
ENV POPPLER_PATH=/usr/bin
ENV APP_PORT=8080
ENV PYTHON=python3.9

RUN apt-get update \
    && apt-get install ${PYTHON} -y \
    ${PYTHON}-dev \
    && apt-get clean \
    && apt-get autoremove

RUN apt install python3-pip -y

RUN apt-get update \
    && apt-get install tesseract-ocr -y

RUN apt-get update && apt-get -y install poppler-utils && apt-get clean


#$(pipenv --venv)/bin/activate
#ENTRYPOINT ["python","app.py"]

RUN groupadd --gid 1001 app
RUN useradd --uid 1001 --gid app --home /app app
RUN mkdir -p /app/app/temp && \
    chown -R app.app /app
USER app
WORKDIR /app/app

RUN ${PYTHON} -m pip install --user pipenv

RUN PYTHON_BIN_PATH="$(python3.9 -m site --user-base)/bin"
RUN PATH="$PATH:$PYTHON_BIN_PATH"
RUN PATH="$PATH:$PYTHON_BIN_PATH:$POPPLER_PATH"

COPY Pipfile /app/Pipfile
RUN  ${PYTHON} -m pipenv install

USER root
RUN echo "#!/bin/bash" >> /entrypoint.sh && \
    echo "source /app/.local/share/virtualenvs/app-*/bin/activate;cd /app/app/;python3.9 app.py" >> /entrypoint.sh && \
    chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]

USER app
COPY app.py /app/app/
COPY model_builder/ /app/app/model_builder
COPY model_store/controller/ /app/app/model_store/controller
COPY model_store/persistency /app/app/model_store/persistency
COPY ocr_module/ /app/app/ocr_module
USER root
RUN chmod -R a+X /app/app/
USER app

EXPOSE $APP_PORT