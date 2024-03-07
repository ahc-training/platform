import sys
from pyspark import SparkContext SparkConf
from pyspark.sql import SparkSession


OBJECT_NAME = "customer"

def main():
    spark = (SparkSession(SparkContext())
        .builder
        .getOrCreate()
    )

    df = spark.read.format("delta").load(f"s3a://curated/{OBJECT_NAME}")
    (df.write.format("jdbc")
        .options(url=Variable.get("PGSQL_CONNSTR_dvdrental"),
                dbtable="customer",
                user=Variable.get("PGSQL_USER"),
                password=Variable.get("PGSQL_PWD"),
                driver="org.postgresql.Driver")
        .save(mode='overwrite'))

    spark.stop()


if __name__ == "__main__":
    main()