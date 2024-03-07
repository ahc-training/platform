Before running this command, you need to setup port-forwarding to port 80 on the server where the container runtime is running.

```
$ docker build -t k8s_certbot:latest
$ docker run -v ~/.kube/:/k8s -e "DOMAINS=example.com,registry.example.com" -e "EMAIL=user@example.com" -e "NAMESPACE=registry" -e "SECRETNAME=certs-secret" -p 80:80 -t k8s_certbot:latest 
```