# app/utils/kafka_consumer.py
from confluent_kafka import Consumer
import os

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")
KAFKA_GROUP = os.getenv("KAFKA_GROUP", "aetherpulse-group")

def get_consumer(topic):
    consumer = Consumer({
        'bootstrap.servers': KAFKA_BROKER,
        'group.id': KAFKA_GROUP,
        'auto.offset.reset': 'earliest'
    })
    consumer.subscribe([topic])
    return consumer
