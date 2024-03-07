import json
from airflow import DAG
from airflow.decorators import dag, task, task_group
from airflow.utils.dates import days_ago
from airflow.models import Variable
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from datetime import timedelta, datetime


class Configuration():
    aws_endpoint_url: str
    aws_access_key: str
    aws_secret_key: str
    pgsql_connstr: str
    pgsql_usr: str
    pgsql_pwd: str

    def __init__(self, aws_endpoint_url, aws_access_key, aws_secret_key, pgsql_connstr, pgsql_usr, pgsql_pwd, **kwargs):
        self.aws_endpoint_url = aws_endpoint_url
        self.aws_access_key = aws_access_key
        self.aws_secret_key = aws_secret_key
        self.pgsql_connstr = pgsql_connstr
        self.pgsql_usr = pgsql_usr
        self.pgsql_pwd = pgsql_pwd


with open(__file__.replace('py', 'json'), 'r') as f:
    config = Configuration(**json.load(f))


default_args={
    "depends_on_past": False,
    "email": ["john.doe@example.com"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 0,
    "retry_delay": timedelta(minutes=1),
}

@dag(dag_id="customer_data_2", start_date=days_ago(1), schedule_interval=timedelta(minutes=10), tags=["Data Warehouse", "ETL/ELT"], catchup=False, owner_links={"airflow": "mailto:john.doe@ah_consultancy.net"}, default_args=default_args)
def etl_group():

    spark_conf = {
                "spark.submit.deployMode": "client",
                "spark.kubernetes.namespace": "spark-jobs",
                "spark.kubernetes.authenticate.executor.serviceAccountName": "spark",
                "spark.dynamicAllocation.enabled": "true",
                "spark.dynamicAllocation.shuffleTracking.enabled": "true",
                "spark.kubernetes.container.image": "docker.io/apache/spark-py:v3.3.2",
                "spark.sql.extensions": "io.delta.sql.DeltaSparkSessionExtension",
                "spark.sql.catalog.spark_catalog": "org.apache.spark.sql.delta.catalog.DeltaCatalog",
                "spark.sql.debug.maxToStringFields": "100",
                "spark.executorEnv.com.amazonaws.sdk.disableCertChecking": "true",
                "spark.hadoop.fs.s3a.endpoint": config.aws_endpoint_url,
                "spark.hadoop.fs.s3a.secret.key": config.aws_secret_key,
                "spark.hadoop.fs.s3a.access.key": config.aws_access_key,
                "spark.hadoop.fs.s3a.connection.timeout": 60,
                "spark.hadoop.fs.s3a.path.style.access": "true",
                "spark.hadoop.fs.s3a.impl": "org.apache.hadoop.fs.s3a.S3AFileSystem",
                "spark.hadoop.fs.s3a.connection.ssl.enabled": "true",
                "spark.kubernetes.executor.deleteOnTermination": "false"
            }
                # "spark.kubernetes.authenticate.driver.serviceAccountName": "spark",
                # "spark.hadoop.fs.s3a.endpoint": Variable.get("AWS_ENDPOINT_URL"),
                # "spark.hadoop.fs.s3a.secret.key": Variable.get("AWS_SECRET_KEY"),
                # "spark.hadoop.fs.s3a.access.key": Variable.get("AWS_ACCESS_KEY"),
                # "spark.executor.instances": 2,
                # "spark.jars.packages": "org.apache.hadoop:hadoop-aws:3.3.2,io.delta:delta-core_2.12:2.2.0,org.postgresql:postgresql:42.5.4",

    extract_data = SparkSubmitOperator(
        task_id="extract_data",
        conn_id="myspark",
        application="/opt/airflow/dags/repo/dags/tasks/extract_data.py",
        name="customer_data_extract",
        conf=spark_conf,
        verbose=True,
        num_executors=2,
        packages="org.apache.hadoop:hadoop-aws:3.3.2,io.delta:delta-core_2.12:2.2.0,org.postgresql:postgresql:42.5.4",
        application_args=[config.pgsql_connstr, config.pgsql_usr, config.pgsql_pwd]
    )

    transform_data = SparkSubmitOperator(
        task_id="transform_data",
        conn_id="myspark",
        application="/opt/airflow/dags/repo/dags/tasks/transform_data.py",
        name="Customer Data Transform",
        conf=spark_conf,
        verbose=True,
        num_executors=2,
        packages="org.apache.hadoop:hadoop-aws:3.3.2,io.delta:delta-core_2.12:2.2.0,org.postgresql:postgresql:42.5.4",
        application_args=[]
    )

    load_data = SparkSubmitOperator(
        task_id="load_data",
        conn_id="myspark",
        application="/opt/airflow/dags/repo/dags/tasks/load_data.py",
        name="Customer Data Load",
        conf=spark_conf,
        verbose=True,
        num_executors=2,
        packages="org.apache.hadoop:hadoop-aws:3.3.2,io.delta:delta-core_2.12:2.2.0,org.postgresql:postgresql:42.5.4",
        application_args=[config.pgsql_connstr, config.pgsql_usr, config.pgsql_pwd]
    )

    extract_data >> transform_data >> load_data

etl_group()
