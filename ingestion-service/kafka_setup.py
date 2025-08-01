import os
from dotenv import load_dotenv
from kafka.admin import KafkaAdminClient, NewTopic

load_dotenv()

admin_client = KafkaAdminClient(bootstrap_servers=os.getenv("KAFKA_BROKERS", "kafka:9092").split(","))

def create_topic(topic_name, num_partitions, replication_factor):
    topic_list = [NewTopic(name=topic_name, num_partitions=num_partitions, replication_factor=replication_factor)]
    admin_client.create_topics(new_topics=topic_list)