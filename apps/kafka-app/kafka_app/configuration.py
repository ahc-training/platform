from dataclasses import dataclass
import kubernetes as k
import yaml
import base64
from typing import List


@dataclass
class Configuration:
    sasl_mechanism: str
    security_protocol: str
    username: str 
    kafka_namespace: str
    # kafka_port: int
    kafka_topic: str
    kafka_hosts: List[str]
    group_id: str

    k.config.load_kube_config()
    v1 = k.client.CoreV1Api()


    def __init__(self, conf_file):
        with open(conf_file, 'r') as f:
            data = yaml.safe_load(f)
            for key, val in data.items():
                setattr(self, key, self.__attribute_value(val))


    def __attribute_value(self, value):
        if isinstance(value, list):
            return [self.__attribute_value(x) for x in value]
        else:
            return value


    # def services(self):
    #     return [f"{x.status.load_balancer.ingress[0].ip}:{self.kafka_port}" \
    #         for x in self.v1.list_namespaced_service(namespace=self.kafka_namespace).items \
    #             if x.status.load_balancer.ingress != None and any(p.port == self.kafka_port for p in x.spec.ports)]

    def password(self):
        secret = self.v1.read_namespaced_secret("kafka-user-passwords", self.kafka_namespace).data
        return base64.b64decode(secret["client-passwords"]).decode('utf-8')
