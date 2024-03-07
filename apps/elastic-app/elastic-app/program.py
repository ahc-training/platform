from elasticsearch import Elasticsearch, helpers
from faker import Faker

import kubernetes as k

fake = Faker()

k.config.load_kube_config()
v1 = k.client.CoreV1Api()

svcs = v1.list_namespaced_service("elastic")
svc = next((x for x in svcs.items if x.metadata.name == "elasticsearch"), None)
endpoint_url = f"http://{svc.status.load_balancer.ingress[0].ip}:{svc.spec.ports[0].port}"
print(endpoint_url)

es = Elasticsearch(endpoint_url)

actions =[
    {
        "_index": "users",
        "_source": {
            "name": fake.name(),
            "street": fake.street_address(),
            "city": fake.city(),
            "zip": fake.zipcode()
        }
    }
    for x in range(998)
]

res = helpers.bulk(es, actions)
print(res)