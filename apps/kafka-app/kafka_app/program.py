from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError
from dataclasses_avroschema import AvroModel
from dataclasses import dataclass
import faker
from datetime import datetime
import logging
import time
from argparse import ArgumentParser
from icecream import ic
from configuration import Configuration
from enum import Enum
from typing import List
import json


logging.basicConfig(level=logging.INFO)


class Mechanisms(Enum):
    Producer = 1
    Consumer = 2


@dataclass
class Contact(AvroModel):
    username: str
    first_name: str
    last_name: str
    email: str
    date_created: str

    class Meta:
        namespace = "contact_v1"


class Producer:
    def __init__(self, hosts, username, password, sasl_mechanism, security_protocol):
        self.producer = KafkaProducer(
            bootstrap_servers=hosts, 
            sasl_mechanism=sasl_mechanism, 
            security_protocol=security_protocol,
            sasl_plain_username=username,
            sasl_plain_password=password())

    def publish_to_kafka(self, topic, message):
        try:
            self.producer.send(topic=topic, value=message.serialize())
            self.producer.flush()
        except KafkaError as ex:
            logging.error(f"Exception {ex}")
        else:
            logging.info(f"Published message {message} into topic {topic}")

    @staticmethod
    def create_random_email():
        fake = faker.Faker(['nl_NL', 'nl_BE'])
        return Contact(
            username=fake.user_name(),
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=fake.email(),
            date_created=str(datetime.utcnow()),
        )


class Consumer:

    def __init__(self, hosts, username, password, sasl_mechanism, security_protocol, topic, group_id):
        self.consumer = KafkaConsumer(topic,
            bootstrap_servers=hosts,
            sasl_mechanism=sasl_mechanism, 
            security_protocol=security_protocol,
            sasl_plain_username=username,
            sasl_plain_password=password(),
            group_id=group_id,
        )

    def consume_from_kafka(self):
        for message in self.consumer:
            logging.info(message.value)


def run_producer(c: Configuration):
    producer = Producer(c.kafka_hosts, c.username, c.password, c.sasl_mechanism, c.security_protocol)
    try:
        while True:
            random_email = ic(producer.create_random_email())
            producer.publish_to_kafka(c.kafka_topic, random_email)
            
            time.sleep(5)
    except KeyboardInterrupt:
        producer.close()

def run_consumer(c: Configuration):
    consumer = Consumer(c.kafka_hosts, c.username, c.password, c.sasl_mechanism, c.security_protocol, c.kafka_topic, c.group_id)
    while True:
        consumer.consume_from_kafka()

def main(mechanism: Mechanisms, config_file):
    c = ic(Configuration(config_file))
    if mechanism == Mechanisms.Producer.name:
        run_producer(c)
    elif mechanism == Mechanisms.Consumer.name:
        run_consumer(c)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-m", "--mechanism", required=True, choices=Mechanisms._member_names_)
    parser.add_argument("-c", "--configuration", required=True)
    args = parser.parse_args()
    main(args.mechanism, args.configuration)
