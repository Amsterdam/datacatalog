FROM python:3.6-alpine3.7 as builder
    WORKDIR /root/app
    COPY . /root/app
    RUN apk --update add gcc make musl-dev libffi-dev openssl-dev
    RUN pip install .

FROM python:3.6-alpine3.7
    WORKDIR /root
    RUN apk --update add openssl
    COPY --from=builder /usr/local/lib/python3.6/site-packages/. /usr/local/lib/python3.6/site-packages
