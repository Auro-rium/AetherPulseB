# app/utils/kafka_producer.py
from confluent_kafka import Producer
import os

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")
producer = Producer({'bootstrap.servers': KAFKA_BROKER})

def send_event(topic, value):
    producer.produce(topic, value.encode('utf-8'))
    producer.flush()
