# Setting up a Kubernetes environment for data engineering

**Table of content:**
- [Setup kubernetes](#setup-kubernetes)
- [Qemu](#qemu)
- [Extra information](#extra-information)
  - [Available applications](#available-applications)

<a id="setup-kubernetes"></a>
## Setup kubernetes
To setup the kubernetes environments, all that needs to be done is to install ansible and git after installation of Ubuntu: 
> Install using the ppa: [Standard ansible in Ubuntu is outdated](#standard-ansible-in-ubuntu-is-outdated)
```bash
sudo apt-get update
sudo apt-add-repository --yes --update ppa:ansible/ansible
sudo apt-get install ansible git
```

When ansible is installed, you can clone this github repository. After cloning you can adjust the *inventory* file to reflect your setup and wishes.
Before beginning the installation process of the kubernetes environment, a few decisions have to be made (the recommendations are set by default): 
- Container runtime: CRI-O (recommended) or containerd. 
- Pod network: Currently only Calico project is supported.
- Load balancer: openelb (recommended), metallb or purelb

Installing the development environment is optional. But it is useful to make changes, especially when installed in KVM without bridged network. 

```bash
# Setup the development environment (optional).
ansible-playbook -K development-environment.yml

# Install the tools to manage the kubernetes environment
ansible-playbook -K server-environment.yml

# Setup the kubernetes environment
ansible-playbook -u vagrant -K kubernetes-environment.yml
```

This will setup your computer with KVM and the needed tools to work with KVM and kubernetes. After the first 2 commands it is recommended to reboot the server. It is not necessary, but you will have to reboot the server to make everything work properly.
<a id="qemu"></a>
## QEMU
The *server-environment* script creates a storage pool `k8s-cluster` using directory `/data`. It also changes the `security_driver = "selinux"` to `security_driver = "none"` in file `/etc/libvirt/qemu.conf` to make sure that terraform can create virtual machines. If you require this option to be set, then there is another option that can be found below: [Apparmor causing permission denied](#apparmor-causing-permission-denied). You will have to revert this manually.
<a id="extra-information"></a>
## Extra information
<a id="available-applications"></a>
### Available applications
To install your required applications, you can use the commands in the table below:

|Application|Install command|
|:-----|:-----|
|Airbyte|`ansible-playbook -u vagrant --extra-vars='{"k8s_tasks": ["airbyte"]}' ./ansible-tools/app_installer.yml`|
|Apache Airflow|`ansible-playbook -u vagrant --extra-vars='{"k8s_tasks": ["airflow"], "k8s_dependencies": ["redis", "postgres"], "k8s_postinstall": ["spark-environment", "dbt-environment"], "git_repo": "http://nas.example.com:3000/training/applications.git", "git_branch": "main", "dags_dir": "dags", "git_usr": "sa_k8s", "git_pwd": "vagrant"}' ./ansible-tools/app_installer.yml`|
|Apache Kafka|`ansible-playbook -u vagrant --extra-vars='{"k8s_tasks": ["kafka"]}' ./ansible-tools/app_installer.yml`|
|Apache Ozone|`ansible-playbook -u vagrant --extra-vars='{"k8s_tasks": ["ozone"]}' ./ansible-tools/app_installer.yml`|
|Apache Spark|`ansible-playbook -u vagrant --extra-vars='{"k8s_tasks": ["spark"]}' ./ansible-tools/app_installer.yml`|
|Elastic Search|`ansible-playbook -u vagrant --extra-vars='{"k8s_tasks": ["elastic"]}' ./ansible-tools/app_installer.yml`|
|Gogs|`ansible-playbook -u vagrant --extra-vars='{"k8s_tasks": ["gogs"], "k8s_dependencies": ["postgres"]}' ./ansible-tools/app_installer.yml`|
|Harbor|`ansible-playbook -u vagrant --extra-vars='{"k8s_tasks": ["harbor"]' ./ansible-tools/app_installer.yml`|
|Jenkins|`ansible-playbook -u vagrant --extra-vars='{"k8s_tasks": ["jenkins"]}' ./ansible-tools/app_installer.yml`|
|MinIO|`ansible-playbook -u vagrant --extra-vars='{"k8s_tasks": ["minio"]}' ./ansible-tools/app_installer.yml`|
|MongoDB|`ansible-playbook -u vagrant --extra-vars='{"k8s_tasks": ["mongodb"]}' ./ansible-tools/app_installer.yml`|
|Prometheus/Grafana|`ansible-playbook -u vagrant --extra-vars='{"k8s_tasks": ["monitoring"]}' ./ansible-tools/app_installer.yml`|
|Portainer|`ansible-playbook -u vagrant --extra-vars='{"k8s_tasks": ["portainer-server", "portainer-agent"]}' ./ansible-tools/app_installer.yml`|
|Postgresql|`ansible-playbook -u vagrant --extra-vars='{"k8s_tasks": ["postgres"]}' ./ansible-tools/app_installer.yml`|
|Redis|`ansible-playbook -u vagrant --extra-vars='{"k8s_tasks": ["redis"]}' ./ansible-tools/app_installer.yml`|
|Docker Registry|`ansible-playbook -u vagrant --extra-vars='{"k8s_tasks": ["registry-podman", "registry", "registry-hosts"]}' ./ansible-tools/app_installer.yml`|

To get the services that are available to you, you can run the following ansible command:
```
ansible-playbook -u vagrant get-services.yml
```
### Run GUI applications over ssh
Everything can be installed on a server without GUI. Even if you installed the development environment. To be able to execute the applications that need a GUI over ssh, you can use the following command:
```bash
# ssh -X <user>@<host> -p <port> <command>
ssh -X sysadmin@1.2.3.4 -p 22 brave-browser
```
### Applications used
 
To develop this setup, the following tools are used:
|<!-- -->|<!-- -->|<!-- -->|<!-- -->|
|---------|---------|---------|---------|
|VSCode Server|KVM|Helm|Linux (Ubuntu)|
|Git|Cockpit|Kubectl|AWS client|
|Terraform|Brave Browser|Ansible|Cockpit|

### Find rate limits for docker.io
When you run these scripts multiple times a day, you might run into rate limits on [docker.io](https://docker.io). The below commands return the status of this rate limit. The first command finds the token that is needed to authenticate the api that returns the information. Be aware rate limit is per ip addresses provided by your ISP.
```bash
TOKEN=$(curl "https://auth.docker.io/token?service=registry.docker.io&scope=repository:ratelimitpreview/test:pull" | jq -r .token)

curl --head -H "Authorization: Bearer $TOKEN" https://registry-1.docker.io/v2/ratelimitpreview/test/manifests/latest
```
### Setting up python environment with poetry
```bash
poetry new <project_name>
poetry config virtualenvs.in-project true
```

### Get logs of pod
The command below will get the logs of the latest running pod that has `driver` in its name and is running in the namespace `spark-jobs`.
```bash
kubectl logs --follow -n spark-jobs pod/$(kubectl get pods -o=json -n spark-jobs | jq -r '.items | map(select(.status.phase == "Running" and (.metadata.name | index("driver") != null))) | sort_by(.metadata.creationTimestamp) | last | .metadata.name')
```

### Get kafka user password
During the installation of Kafka, a secret will be created that contains the password for `user1`. To get the password the below command can be used.
```bash
kubectl get -n kafka secret/kafka-user-passwords -o jsonpath={".data.client-passwords"} | base64 --decode
```

### Building containers with Jenkins

#### Required plugins
* kubernetes
* gogs-webhook
* pipeline-graph-view
* prometheus

#### Configuration settings for kubernetes
##### Settings for Kubernetes Cloud

|Property|Value|
|:---------|:---------|
|Cloud Name|kubernetes|
|Kubernetes URL|https://192.167.56.11:6443|
|Jenkins URL|http://jenkins.example.com:8080|
|Pod Label::Key|jenkins|
|Pod Label::Value|agent|

##### Settings for Pod Template

|Property|Name|
|:---------|:---------|
|Name|jenkins-agent|
|Namespace|devops|
|Labels|jenkins-agent|
|Usage|Use this node as musch as possible|

##### Settings for Container Template

|Property|Name|
|:---------|:---------|
|Name|jenkins-agent|
|Docker image|jenkins/inbound-agent|

#### Settings for Airflow pipeline

|Property|Name|
|:---------|:---------|
|Gogs Webhook|Use Gogs Secret|
|Gogs Webhook::Secret|airflow|
|Pipeline::Definition|Pipeline script from SCM|
|SCM|Git|
|Repository URL|http://nas.example.com:3000/training/devops-airflow.git|
|Credentials|sa_k8s|
|Branch Specifier|*/main|
|Script Path|devops/Jenkinsfile|

#### Settings for PySpark pipeline

|Property|Name|
|:---------|:---------|
|Gogs Webhook|Use Gogs Secret|
|Gogs Webhook::Secret|pyspark|
|Pipeline::Definition|Pipeline script from SCM|
|SCM|Git|
|Repository URL|http://nas.example.com:3000/training/devops-spark.git|
|Credentials|sa_k8s|
|Branch Specifier|*/main|
|~~Additional Behaviours~~|~~Git LFS pull after checkout~~|
|Script Path|devops/Jenkinsfile|

#### Settings for Kafka pipeline

|Property|Name|
|:---------|:---------|
|Gogs Webhook|Use Gogs Secret|
|Gogs Webhook::Secret|kafka|
|Pipeline::Definition|Pipeline script from SCM|
|SCM|Git|
|Repository URL|http://nas.example.com:3000/training/devops-kafka.git|
|Credentials|sa_k8s|
|Branch Specifier|*/main|
|Script Path|devops/Jenkinsfile|

#### Adding spark dependencies
To dependencies to spark, you need to look up the configuration for maven at (https://mvnrepository.com). These dependencies have to be added to pom.xml as part of pyspark image created by the Jenkins job.

### Issues

#### Apparmor causing permission denied
Creating VMs with Terraform in a custom storage pool will generate a *permission denied* error. This is caused by apparmor. To circumvent this, the file /etc/apparmor.d/local/abstractions/libvirt-qemu should be modified to add the following lines (paths are examples):
```text
"/path/to/storage/" r,
"/path/to/storage/**" rwk,
``` 
This will tell that apparmor trusts the directory and its containing files.  

#### Cockpit-machines does not support UEFI
The default installation of `cockpit-machines` on Ubuntu does not support UEFI configurations. To get around this there is a block in `server-environment.yml` that creates a new version of `cockpit-machines` from the git repository. After restarting the server this should function properly. However, this requires extra applications to be installed: `npm` and `gettext`. Since this is not required, so the block can be disabled by setting the *when* argument to *false* (`when: false`)  

#### Standard ansible in Ubuntu is outdated
It is not recommended to use the standard ansible app delivered by Ubuntu. This is an older version and will cause issues with terraform when generating the
virtual machines. There for use the *ppa* as described in this document.  

#### CoreDNS returning wrong ip address for registry
During the execution in the Jenkins pipeline to build a docker image, it could happen that the dns record in CoreDNS is pointing to the wrong ip address (this 
might also happen to other services). This could be circumvented by adding a rewrite rule to the corefile. Corefile is part of the CoreDNS configmap in 
kubernetes. By executing `k edit cm/coredns -n kube-system`, you can edit this configmap (normal vim commands apply). You need to add a line similar to this: 
`rewrite name registry.example.com registry.devops.svc.cluster.local` (change *example.com* to the applicable domain name). Add this somewhere in the 
json that comes after *data->Corefile* and should be between the curly brackets of *.:53*. It should look similar to the example below:   

```yaml
apiVersion: v1
data:
  Corefile: |
    .:53 {
        errors
        health {
           lameduck 5s
        }
        ready
        rewrite name registry.example.com registry.devops.svc.cluster.local
        kubernetes cluster.local in-addr.arpa ip6.arpa {
           pods insecure
           fallthrough in-addr.arpa ip6.arpa
           ttl 30
        }
        prometheus :9153
        forward . /etc/resolv.conf {
           max_concurrent 1000
        }
        cache 30
        loop
        reload
        loadbalance
    }
kind: ConfigMap
metadata:
  name: coredns
  namespace: kube-system
```  

#### Not enough resources on kubernetes cluster
In case the kubernetes cluster does not have enough resources, then you can do 2 things:
1. Add extra nodes, which is the best option for production environments
2. Remove the taint from the control-plane (not recommended) by executing the following command: `kubectl taint nodes --all  node-role.kubernetes.io/control-plane-`

#### Slow browser through ssh over internet
The ssh protocol can be slow to run e.g. a browser through ssh over internet. This can be a problem if you want to read data from a service on kubernetes 
that connects to other services/pods by kubernetes internal ip addresses. When reading this data you need to be connected to the actual development 
server. This can be fixed by running a podman container on the development server that runs a vnc server.  
```bash
podman run -d --name=firefox --security-opt seccomp=unconfined -e PUID=1000 -e PGID=1000 -e TZ=Etc/UTC -p 3000:3000 -p 3001:3001 --shm-size="1gb" --restart unless-stopped lscr.io/linuxserver/firefox:latest
```  
You could do this on kubernetes too. This has some advantages, like being able to use a browser within the cluster.

#### MinIO pods not starting
In case the MinIO pods are not started and cause an error, then this might be because the operator is using the wrong images. 
To fix this, you need to look up the right image name at [Docker Hub](https://hub.docker.com/r/minio/minio/tags). There you can find images 
for the right CPU architecture (most likely you need *-cpuv1). When creating a new tenant, you have to add this image 
to th option MinIO on tab Images.

### Recommendations

#### Order of install
1. Install kubernetes with devops tools
2. Create user & password for Portainer
3. Install MinIO
4. Reconfigure MinIO Operator service from ClusterIP to LoadBalancer
5. Create MinIO Tenant (don't forget to download the keys)
6. Optionally create a MinIO Tenant user
7. Create S3 bucket in MinIO
8. Update coredns configmap in kubernetes with rewrite rules for jenkins and registry
9. Install Jenkins plugins
10. Configure Jenkins to build Airflow, Kafka and PySpark images
11. Build Airflow, Kafka and PySpark images
12. Install Airflow
13. Install Kafka
14. Remove taint from control-plane