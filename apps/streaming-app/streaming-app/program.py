import kubernetes as k
from pyspark.sql import SparkSession
from pyspark.sql.types import *
from pyspark.sql.functions import *
from delta.pip_utils import configure_spark_with_delta_pip

k8s_namespace = "minio-data"
k8s_service = "minio"
dataFile = "streaming"
s3accessKeyAws = "SPOiVRqHzsQJUPp6"
s3secretKeyAws = "dpJovd9kGI2oYqXHXxPXCGHpsg2Tx0rN"
connectionTimeOut = "300"
s3EndpointHost = "192.167.56.98" #"minio.minio-data.svc.cluster.local"
s3EndpointPort = 80
dstBucket = "delta-lake"

kafka_bootstrap_server = "192.167.56.101:9094"
kafka_topic = "my-topic"

k.config.load_kube_config()
v1 = k.client.CoreV1Api()


def get_ip(namespace: str, service: str):
    services = v1.list_namespaced_service(namespace)
    svc = next((x for x in services.items if x.metadata.name == service), None)
    ip = svc.status.load_balancer.ingress[0].ip
    print(f"{namespace} - {service}: {ip}")
    return ip

def main():
    s3EndpointHost = get_ip(k8s_namespace, k8s_service)
    spark = SparkSession \
        .builder \
        .master(f"k8s://https://192.167.56.11:6443") \
        .appName("Kafka Streaming Demo") \
        .config("spark.executor.instances", "2") \
        .config('spark.jars.packages', 'org.apache.hadoop:hadoop-aws:3.3.2,io.delta:delta-core_2.12:2.2.0,org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.2') \
        .config("spark.kubernetes.container.image", "docker.io/bitnami/spark:3.3.2-debian-11-r3") \
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
        .config("spark.sql.debug.maxToStringFields", "100") \
        .config("spark.executorEnv.com.amazonaws.sdk.disableCertChecking", "true") \
        .getOrCreate()

    sc = spark.sparkContext
    sc._jsc.hadoopConfiguration().set("fs.s3a.endpoint", f"http://{s3EndpointHost}")
    sc._jsc.hadoopConfiguration().set("fs.s3a.secret.key", s3secretKeyAws)
    sc._jsc.hadoopConfiguration().set("fs.s3a.access.key", s3accessKeyAws)
    sc._jsc.hadoopConfiguration().set("fs.s3a.connection.timeout", connectionTimeOut)
    sc._jsc.hadoopConfiguration().set("fs.s3a.path.style.access", "true")
    sc._jsc.hadoopConfiguration().set("fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
    sc._jsc.hadoopConfiguration().set("fs.s3a.connection.ssl.enabled", "true")
    sc.setLogLevel("WARN")

    # df = spark.read.csv(f"s3a://{srcBucket}/{dataFile}.csv", header=True)
    # df = df.toDF(*[c.lower().replace(' ', '_') for c in df.columns])
    # df.write.mode("overwrite").format("delta").save(f"s3a://{dstBucket}/{dataFile}")
    # spark.stop()

    sampleDataframe = (
        spark.readStream.format("kafka")
        .option("kafka.bootstrap.servers", kafka_bootstrap_server)
        .option("subscribe", kafka_topic)
        .option("startingOffsets", "latest")
        .load()
    )

    base_df = sampleDataframe.selectExpr("CAST(value as STRING)", "timestamp")
    base_df.printSchema()


    sample_schema = (
        StructType()
        .add("username", StringType())
        .add("first_name", StringType())
        .add("last_name", StringType())
        .add("email", StringType())
        .add("date_created", TimestampType())
    )

    info_dataframe = base_df.select(
        from_json(col("value"), sample_schema).alias("info"), "timestamp"
    )

    info_dataframe.printSchema()
    info_df_fin = info_dataframe.select("info.*", "timestamp")
    info_df_fin.printSchema()

    result = (info_df_fin.writeStream
        .format("delta")
        .outputMode("append")
        .option("checkpointLocation", "/tmp/delta/_checkpoints/")
        .start(f"s3a://delta-lake/{dataFile}")
        .awaitTermination()
    )

    print(result)

if __name__ == '__main__':
    main()
