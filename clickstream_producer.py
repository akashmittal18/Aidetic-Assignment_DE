from confluent_kafka import Producer
import time

def delivery_report(err, msg):
    if err is not None:
        print(f'Message delivery failed: {err}')
    else:
        print(f'Message delivered to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}')

# Configure the producer
producer_config = {'bootstrap.servers': 'localhost:9092'}

# Create the Kafka producer instance
producer = Producer(producer_config)

# Send clickstream data to the Kafka topic
topic = 'clickstream_topic'

try:
    while True:
        # Simulate generating clickstream data
        clickstream_data = '{"user_id": 123, "timestamp": "2023-07-21 12:34:56", "url": "example.com", "country": "USA", "city": "New York", "browser": "Chrome", "os": "Windows", "device": "Desktop"}'
        producer.produce(topic, value=clickstream_data, callback=delivery_report)

        # Wait for a short interval before sending the next clickstream data
        time.sleep(1)
except KeyboardInterrupt:
    pass
finally:
    # Flush and close the producer gracefully
    producer.flush()
    producer.close()
