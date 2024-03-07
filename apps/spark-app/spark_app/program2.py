# https://medium.com/@dineshvarma.guduru/reading-and-writing-data-from-to-minio-using-spark-8371aefa96d2
# https://towardsdatascience.com/hands-on-introduction-to-delta-lake-with-py-spark-b39460a4b1ae
# https://stackoverflow.com/questions/75625735/spark-not-working-with-worker-in-other-machine
# https://tomlous.medium.com/deploying-apache-spark-jobs-on-kubernetes-with-helm-and-spark-operator-eb1455930435#36dc
# https://googlecloudplatform.github.io/spark-on-k8s-operator/docs/quick-start-guide.html

import json
import kubernetes as k
from pyspark.sql import SparkSession
from pyspark.conf import SparkConf

with open('../../../minio_credentials.json', 'r') as f:
    minio = json.load(f)

s3_namespace = "minio-data"
s3_service = "minio"
s3_port = 80
spark_namespace = "spark"
spark_service = "bitnami-spark-master-svc"
spark_port = 7077
db_namespace = "postgresql"
db_service = "bitnami-postgresql-postgresql-ha-pgpool"
db_port = 5432
dataFile = "customers"
s3accessKeyAws = minio["accessKey"]
s3secretKeyAws = minio["secretKey"]
connectionTimeOut = 60
dstBucket = "delta-lake"

k.config.load_kube_config()
v1 = k.client.CoreV1Api()


def get_ip(namespace: str, service: str):
    services = v1.list_namespaced_service(namespace)
    svc = next((x for x in services.items if x.metadata.name == service), None)
    ip = svc.status.load_balancer.ingress[0].ip
    print(f"{namespace} - {service}: {ip}")
    return ip

spark_conf = [
    ('spark.jars.packages', 'org.apache.hadoop:hadoop-aws:3.3.2,io.delta:delta-core_2.12:2.2.0,org.postgresql:postgresql:42.5.4'),
    ("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension"),
    ("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog"),
    ("spark.sql.debug.maxToStringFields", "100"),
    ("spark.executorEnv.com.amazonaws.sdk.disableCertChecking", "true"),
    ("spark.hadoop.fs.s3a.endpoint", f"http://{get_ip(s3_namespace, s3_service)}:{s3_port}"),
    ("spark.hadoop.fs.s3a.secret.key", s3secretKeyAws),
    ("spark.hadoop.fs.s3a.access.key", s3accessKeyAws),
    ("spark.hadoop.fs.s3a.connection.timeout", connectionTimeOut),
    ("spark.hadoop.fs.s3a.path.style.access", "true"),
    ("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem"),
    ("spark.hadoop.fs.s3a.connection.ssl.enabled", "true")
]
def main():
    try:
        conf = SparkConf()
        conf.setAll(spark_conf)
        spark = (SparkSession
            .builder
            .master(f"spark://{get_ip(spark_namespace, spark_service)}:{spark_port}")
            .appName("spark-app for demo")
            .config(conf=conf)
            .getOrCreate())

        df = (spark.read.format("jdbc")
                .options(url=f"jdbc:postgresql://{get_ip(db_namespace, db_service)}:{db_port}/dvdrental",
                    dbtable="customer",
                    user="postgres",
                    password="Sql123!",
                    driver="org.postgresql.Driver")
                .load())
        df = df.toDF(*[c.lower().replace(' ', '_') for c in df.columns])
        df.write.mode("overwrite").parquet("s3a://raw/customer")
    finally:
        spark.stop()

if __name__ == '__main__':
    main()
