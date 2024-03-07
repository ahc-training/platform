from deltalake import DeltaTable, write_deltalake
from faker import Faker
import pandas as pd

uri = "s3a://demo"
storage_options = {
    "AWS_ACCESS_KEY_ID": 'sysadmin',
    "AWS_SECRET_ACCESS_KEY": 'Amh528219898',
    "AWS_ENDPOINT_URL": "http://192.167.56.98:80",
    "AWS_REGION": "eu-west-1",
    "AWS_ALLOW_HTTP": "true",
    "AWS_S3_ALLOW_UNSAFE_RENAME": "true"
}

fake = Faker('nl-NL')
data = pd.DataFrame.from_records([{"name": fake.name(), "address": fake.address(), "email": fake.email()} for i in range(1000)])

w = write_deltalake(table_or_uri=uri, data=data, mode="append", storage_options=storage_options)

dt = DeltaTable(uri, storage_options=storage_options)
print(dt.version())
