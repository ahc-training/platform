FROM alpine:latest

USER root

ENV DOMAINS=${DOMAINS}
ENV EMAIL=${EMAIL}
ENV NAMESPACE=${NAMESPACE}
ENV SECRETNAME=${SECRETNAME}

RUN apk update && apk add curl git python3 py3-pip certbot bash

RUN curl -LO https://storage.googleapis.com/kubernetes-release/release/v1.15.1/bin/linux/amd64/kubectl
RUN chmod u+x kubectl && mv kubectl /bin/kubectl

EXPOSE 80
RUN mkdir -p /{k8s,certs/{config,logs,work}}
VOLUME ["/k8s"]
COPY ./entrypoint.sh /
RUN chmod +x /entrypoint.sh

ENTRYPOINT [ "/entrypoint.sh" ]
