import os
from dotenv import load_dotenv
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError

load_dotenv()

def create_topic(topic_name, num_partitions, replication_factor):
    admin_client = KafkaAdminClient(bootstrap_servers=os.getenv("KAFKA_BROKERS", "kafka:9092").split(","))
    
    # Check if topic exists
    existing_topics = admin_client.list_topics()
    if topic_name in existing_topics:
        print(f"Topic '{topic_name}' already exists, skipping creation")
        return
    
    # Create topic if it doesn't exist
    topic_list = [NewTopic(name=topic_name, 
                          num_partitions=num_partitions, 
                          replication_factor=replication_factor)]
    try:
        admin_client.create_topics(new_topics=topic_list)
        print(f"Topic '{topic_name}' created successfully")
    except TopicAlreadyExistsError:
        print(f"Topic '{topic_name}' already exists (race condition)")
    except Exception as e:
        print(f"Error creating topic '{topic_name}': {str(e)}")