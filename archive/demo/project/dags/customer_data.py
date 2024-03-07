from airflow import DAG
from airflow.decorators import dag, task, task_group
from airflow.utils.dates import days_ago
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import KubernetesPodOperator
from kubernetes.client import models as k8s
from datetime import timedelta, datetime


regcred = k8s.V1LocalObjectReference("regcred")

default_args={
    "depends_on_past": False,
    "email": ["john.doe@example.com"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=1),
}

@dag(dag_id="customer_data", start_date=days_ago(1), schedule_interval=timedelta(minutes=10), tags=["Data Warehouse", "ETL/ELT"], catchup=False, owner_links={"airflow": "mailto:john.doe@ah_consultancy.net"}, default_args=default_args)
def etl_group():
    
    extract_data = KubernetesPodOperator(
        name="extract-customer-data",
        namespace="spark-jobs",
        image="registry.example.com:5000/custom-pyspark:latest",
        cmds=["bash", "-cx"],
        arguments=['python3', '/app/customer_data/extract_data.py'],
        image_pull_policy="Always",
        image_pull_secrets=[regcred],
        labels={
            "source": "dvdrental", 
            "data_object": "customer"
        },
        task_id="step-1",
        is_delete_operator_pod=True,
        in_cluster=True,
        get_logs=True,
        do_xcom_push=False
    )

    # transform_data = KubernetesPodOperator(
    #     name="transform-customer-data",
    #     image="registry.example.com:5000/custom-pyspark:latest",
    #     cmds=[],
    #     arguments=[],
    #     labels={
    #         "source": "dvdrental", 
    #         "data_object": "customer"
    #     },
    #     task_id="customer_data_transform",
    #     do_xcom_push=True
    # )

    # load_data = KubernetesPodOperator(
    #     name="load-customer-data",
    #     image="registry.example.com:5000/custom-pyspark:latest",
    #     cmds=[],
    #     arguments=[],
    #     labels={
    #         "source": "dvdrental", 
    #         "data_object": "customer"
    #     },
    #     task_id="customer_data_load",
    #     do_xcom_push=True
    # )

    extract_data 
    #>> transform_data >> load_data

etl_group()
