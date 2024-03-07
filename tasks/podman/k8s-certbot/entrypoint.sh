#! /bin/bash

domain=$(cut -d',' -f1 <<<"$DOMAINS")

certbot certonly --standalone -d $DOMAINS --config-dir /certs/config/ --work-dir /certs/work/ \
    --logs-dir /certs/logs/ -n --agree-tos -m $EMAIL

if [ -d "/certs/config/live/$domain" ]; then
    kubectl create secret tls $SECRETNAME --kubeconfig=/k8s/config --namespace $NAMESPACE \
        --key=/certs/config/live/$domain/privkey.pem --cert=/certs/config/live/$domain/fullchain.pem
fi