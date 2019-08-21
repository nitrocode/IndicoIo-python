FROM indicoio/numpy as numpy-base
FROM indicoio/alpine:3.7.3

ENV INDICO_API_HOST="apiv2.indico.io"

RUN apk add --no-cache libjpeg jpeg-dev zlib-dev python2-dev python2 && \
    python2 -m ensurepip && \
    rm -r /usr/lib/python*/ensurepip && \
    pip2 install "mock>=1.3.0<2.0.0" "nose>=1.0" setuptools

COPY requirements.py requirements.py
COPY README.rst README.rst

RUN pip2 install $(python2 -c "from requirements import REQUIREMENTS; print(' '.join(REQUIREMENTS))")

COPY . /indicoio-python
WORKDIR /indicoio-python

RUN python2 setup.py develop