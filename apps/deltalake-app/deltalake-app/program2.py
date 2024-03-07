from faker import Faker
from icecream import ic
import polars as pl
from deltalake import DeltaTable

N = 2
uri = "s3a://deltalake-demo"
storage_options = {
    "AWS_ACCESS_KEY_ID": 'sysadmin',
    "AWS_SECRET_ACCESS_KEY": 'Amh528219898',
    "AWS_ENDPOINT_URL": "http://192.167.56.98:80",
    "AWS_REGION": "eu-west-1",
    "AWS_ALLOW_HTTP": "true",
    "AWS_S3_ALLOW_UNSAFE_RENAME": "true"
}

# fake = Faker('nl-NL')

# source: pl.DataFrame = pl.DataFrame([{"name": fake.name(), "address": fake.address(), "email": fake.email()} for i in range(1000)])
# source.write_delta(target=uri, mode="append", storage_options=storage_options)

dt = DeltaTable(uri, storage_options=storage_options)
dt.optimize.compact()
dt.vacuum(retention_hours=168, dry_run=False)

table = pl.read_delta(source=uri, storage_options=storage_options)

data = table.with_columns(pl.lit(table.select(["name"]).hash_rows() % N).alias("id")) \
        .partition_by("id") \
        .filter(pl.col("address").str.to_lowercase().str.contains('eindhoven') |
           pl.col("address").str.to_lowercase().str.contains('utrecht'))
print(data)
