import sys
from pyspark import SparkConf
from pyspark.sql import SparkSession


OBJECT_NAME = "customer"

def main():
    spark = (SparkSession(SparkContext())
        .builder
        .getOrCreate()
    )

    df = spark.read.parquet(f"s3a://raw/{OBJECT_NAME}")
    df = df.toDF(*[c.lower().replace(' ', '_') for c in df.columns])
    df.write.mode("overwrite").format("delta").save(f"s3a://curated/{OBJECT_NAME}")

    spark.stop()


if __name__ == "__main__":
    main()