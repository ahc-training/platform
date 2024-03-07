# - AWS Client install
# - Add apt repositories for terraform, helm and kubectl
# - Install VSCode extensionss

FROM ubuntu:24.04

RUN apt-get update && apt-get install -y software-properties-common curl apt-transport-https wget gpg

RUN curl -fsSLo /usr/share/keyrings/brave-browser-archive-keyring.gpg https://brave-browser-apt-release.s3.brave.com/brave-browser-archive-keyring.gpg
RUN echo "deb [signed-by=/usr/share/keyrings/brave-browser-archive-keyring.gpg] https://brave-browser-apt-release.s3.brave.com/ stable main" | tee /etc/apt/sources.list.d/brave-browser-release.list

RUN wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > packages.microsoft.gpg
RUN install -D -o root -g root -m 644 packages.microsoft.gpg /etc/apt/keyrings/packages.microsoft.gpg
RUN echo "deb [arch=amd64,arm64,armhf signed-by=/etc/apt/keyrings/packages.microsoft.gpg] https://packages.microsoft.com/repos/code stable main" > /etc/apt/sources.list.d/vscode.list && \
    rm -f packages.microsoft.gpg

RUN apt-get update && \
    apt-get install -y ansible, git, git-lfs, brave-browser, vim, multitail, podman, python3-pip, kafkacat, code, virt-manager, python3-pip, kubectl, helm, terraform, skopeo, postgres-client, python3-psycopg2

RUN pip3 install pyyaml, poetry, kubernetes, psycopg2-binary