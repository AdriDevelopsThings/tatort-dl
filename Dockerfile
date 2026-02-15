FROM python:3.14-alpine AS base
WORKDIR /build
RUN pip install --upgrade pip pipx

FROM base
ENV PIPX_HOME=/opt/pipx
ENV PIPX_BIN_DIR=/usr/local/bin
ENV PYTHONUNBUFFERED=1

COPY ./pyproject.toml ./
COPY ./tatort_dl ./tatort_dl
RUN pipx install .

RUN rm -rf /build
WORKDIR /app

ENV TMP_DIR=/var/tmp/tatort-dl

CMD ["tatort-dl"]
