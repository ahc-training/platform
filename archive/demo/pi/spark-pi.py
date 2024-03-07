from airflow import DAG
from airflow.decorators import dag, task, task_group
from airflow.utils.dates import days_ago
from datetime import timedelta, datetime
from airflow.providers.cncf.kubernetes.operators.spark_kubernetes import SparkKubernetesOperator
from airflow.providers.cncf.kubernetes.sensors.spark_kubernetes import SparkKubernetesSensor
from airflow.models import Variable
from kubernetes.client import models as k8s
from airflow.contrib.operators.kubernetes_pod_operator import KubernetesPodOperator


default_args={
   'depends_on_past': False,
   'email': ['abcd@gmail.com'],
   'email_on_failure': False,
   'email_on_retry': False,
   'retries': 1,
   'retry_delay': timedelta(minutes=5)
}

@dag(dag_id='my-second-dag', default_args=default_args, description='simple dag', schedule_interval=timedelta(days=1), start_date=days_ago(1), catchup=False, tags=['example'])
def my_second_dag():

   t1 = SparkKubernetesOperator(
      task_id='n-spark-pi',
      trigger_rule="all_success",
      depends_on_past=False,
      retries=3,
      application_file="sparkapp/spark-pi.yaml",
      namespace="spark-jobs",
      kubernetes_conn_id="myk8s",
      api_group="sparkoperator.k8s.io",
      api_version="v1beta2",
      do_xcom_push=True,
   )

   t2 = SparkKubernetesSensor(
      task_id='n-spark-pi-monitor',
      namespace='spark-jobs',
      application_name="{{ task_instance.xcom_pull(task_ids='n-spark-pi')['metadata']['name'] }}",
      kubernetes_conn_id="myk8s",
      api_group="sparkoperator.k8s.io",
      api_version="v1beta2",
      attach_log=True,
   )

   t1 >> t2
my_dag = my_second_dag()
