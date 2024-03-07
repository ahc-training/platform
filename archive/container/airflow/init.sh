# https://airflow.apache.org/docs/apache-airflow/stable/howto/docker-compose/index.html
echo -e "AIRFLOW_UID=$(id -u)" > .env
docker compose up airflow-init
docker compose up