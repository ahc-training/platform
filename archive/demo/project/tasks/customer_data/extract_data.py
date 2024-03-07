import json
import logger
from pyspark import SparkConf
from pyspark.sql import SparkSession
from dataclasses import dataclass


@dataclass
class Configuration():
    s3_endpoint: str
    s3_access_key: str
    s3_secret_key: str
    postgres_url: str
    postgres_username: str
    postgres_password: str

    def __init__(self, **kwargs):
        self.s3_endpoint = kwargs.pop("s3_endpoint")
        self.s3_access_key = kwargs.pop("s3_access_key")
        self.s3_secret_key = kwargs.pop("s3_secret_key")
        self.postgres_url = kwargs.pop("postgres_url")
        self.postgres_username = kwargs.pop("postgres_username")
        self.postgres_password = kwargs.pop("postgres_password")

with open("configuration.json") as f:
    conf = Configuration(**json.load(f))

spark_conf = [
    ("spark.submit.deployMode", "client"),
    ("spark.executor.instances", 2),
    ("spark.jars.packages", "org.apache.hadoop,hadoop-aws,3.3.2,io.delta,delta-core_2.12,2.2.0,org.postgresql,postgresql,42.5.4"),
    ("spark.dynamicAllocation.enabled", "true"),
    ("spark.dynamicAllocation.shuffleTracking.enabled", "true"),
    ("spark.kubernetes.container.image.pullPolicy", "Always"),
    ("spark.kubernetes.container.image", "docker.io/apache/spark-py"),
    ("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension"),
    ("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog"),
    ("spark.sql.debug.maxToStringFields", "100"),
    ("spark.executorEnv.com.amazonaws.sdk.disableCertChecking", "true"),
    ("spark.hadoop.fs.s3a.endpoint", conf.s3_endpoint),
    ("spark.hadoop.fs.s3a.secret.key", conf.s3_secret_key),
    ("spark.hadoop.fs.s3a.access.key", conf.s3_access_key),
    ("spark.hadoop.fs.s3a.connection.timeout", 60),
    ("spark.hadoop.fs.s3a.path.style.access", "true"),
    ("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem"),
    ("spark.hadoop.fs.s3a.connection.ssl.enabled", "true"),
]
    # ("spark.kubernetes.namespace", "spark-jobs"),
    # ("spark.kubernetes.container.image.pullSecrets", "airflow-registry")
    # ("spark.kubernetes.container.image", "example.com:5000/custom-pyspark:latest"),


OBJECT_NAME = "customer"


def get_module_logger(mod_name):
    logger = logging.getLogger(mod_name)
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - [%(levelname)-8s]: %(message)s', "%Y-%m-%d %H:%M:%S")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    return logger


def main():
    logger = get_module_logger(__name__)
    try:
        spark = (SparkSession(SparkContext())
            .master("k8s://kubernetes.default.svc:443")
            .appName("Customer Data Extract")
            .config(conf=SparkConf().setAll(spark_conf))
            .builder
            .getOrCreate()
        )

        df = (spark.read.format("jdbc")
            .options(url=conf.postgres_url,
                    dbtable="customer",
                    user=conf.postgres_username,
                    password=conf.postgres_password,
                    driver="org.postgresql.Driver")
            .load()
        )
        df.write.parquet(f"s3a://raw/{OBJECT_NAME}")

        spark.stop()
    except(Exception ex):
        logger.exception(ex)


if __name__ == "__main__":
    main()