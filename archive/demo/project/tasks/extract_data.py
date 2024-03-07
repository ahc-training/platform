import sys
from pyspark import SparkContext, SparkConf
from pyspark.sql import SparkSession


OBJECT_NAME = "customer"

def main():
    spark = (SparkSession(SparkContext())
        .builder
        .getOrCreate()
    )

    df = (spark.read.format("jdbc")
        .options(url=sys.argv[1],
                dbtable="customer",
                user=sys.argv[2],
                password=sys.argv[3],
                driver="org.postgresql.Driver")
        .load()
    )
    df.write.parquet(f"s3a://raw/{OBJECT_NAME}")

    spark.stop()


if __name__ == "__main__":
    main()
