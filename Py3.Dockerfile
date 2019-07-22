FROM indicoio/numpy as numpy-base
FROM indicoio/alpine:3.7.3

ENV INDICO_API_HOST="apiv2.indico.io"

RUN apk add --no-cache libjpeg jpeg-dev zlib-dev && \
    pip3 install "mock>=1.3.0<2.0.0" "nose>=1.0" setuptools

COPY requirements.py requirements.py
COPY README.rst README.rst

RUN pip3 install $(python2 -c "from requirements import REQUIREMENTS; print(' '.join(REQUIREMENTS))")

COPY . /indicoio-python
WORKDIR /indicoio-python

RUN python3 setup.py develop