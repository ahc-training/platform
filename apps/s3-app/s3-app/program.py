# https://ozone.apache.org/docs/1.1.0/recipe/botoclient.html

import logging
import sys
import boto3
from botocore.config import Config
import kubernetes as k
import os
import time

k8s_namespace = 'ozone'
k8s_service = 's3g'
file_path = '../../../data/'
bucket = 'world-cup'
matches = 'WorldCupMatches.csv'
players = 'WorldCupPlayers.csv'
world_cups = 'WorldCups.csv'

##############################
## Setup logging to console ##
##############################

fmt = logging.Formatter("%(asctime)s [%(levelname)s]: %(message)s")
hdlr = logging.StreamHandler(sys.stdout)
hdlr.setFormatter(fmt)
logger = logging.getLogger()
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)

#########################################################
## Get the Apache Ozone service from k8s to connect to ##
#########################################################

try:
    k.config.load_kube_config()
    v1 = k.client.CoreV1Api()

    svcs = v1.list_namespaced_service(k8s_namespace)
    svc = next((x for x in svcs.items if x.metadata.name == k8s_service), None)

    endpoint_url = f"http://{svc.status.load_balancer.ingress[0].ip}:{svc.spec.ports[0].port}"
    logger.info(f"The Minio endpoint is: {endpoint_url}")
except Exception as ex:
    logger.exception(ex)
    sys.exit()

##############################################
## Connect to Apache Ozone to upload a file ##
##############################################

try:
    # session = boto3.Session() 
    client = boto3.client('s3',
        endpoint_url=endpoint_url,
        config=Config(connect_timeout=30, read_timeout=30, retries={'max_attempts': 5}),
        aws_access_key_id='SPOiVRqHzsQJUPp6',
        aws_secret_access_key='dpJovd9kGI2oYqXHXxPXCGHpsg2Tx0rN',
        verify=False
    )

    # volume = client.create_volume()
    
    # world_cup = client.Bucket(bucket)
    # if world_cup.creation_date is None:
    # world_cup = client.create_bucket(Bucket=bucket)
    
    # objs = world_cup.objects.filter(Prefix=matches, MaxKeys=1)
    # if not any([w.key == matches for w in objs]):
    with open(f'{file_path}{matches}', 'rb') as data:
        client.upload_fileobj(data, bucket, matches)
except Exception as ex:
    logger.exception(ex)
