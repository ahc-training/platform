ARG SPARK_VERSION=v3.2.4
# Base image with Apache Spark and Python
FROM docker.io/apache/spark-py:${SPARK_VERSION}

USER root

# Install git
RUN apt-get update && apt-get install -y git python3-pip

# Install Poetry with pip
RUN pip3 install poetry

# Set working directory
WORKDIR /app

# Copy the entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

USER 185

ENV $GIT_REPO="your-git-repo-url"
ENV $GIT_BRANCH="your-git-branch"
ENV $GIT_USERNAME="your-username"
ENV $GIT_TOKEN="your-personal-access-token"
ENV $GIT_TARGET_DIR="git-repo"

# Set the entrypoint script as the entrypoint for the container
ENTRYPOINT ["/entrypoint.sh"]
