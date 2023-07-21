from confluent_kafka import Consumer, KafkaError
import happybase

# Configure the Kafka consumer
consumer_config = {'bootstrap.servers': 'localhost:9092', 'group.id': 'clickstream_consumer_group'}

# Create the Kafka consumer instance
consumer = Consumer(consumer_config)
topic = 'clickstream_topic'
consumer.subscribe([topic])

# Configure HBase connection
hbase_connection = happybase.Connection('localhost', port=9090)
table = hbase_connection.table('clickstream_table')

# Consume clickstream data from Kafka and store it in HBase
while True:
    message = consumer.poll(1.0)

    if message is None:
        continue
    if message.error():
        if message.error().code() == KafkaError._PARTITION_EOF:
            print('Reached end of partition, exiting...')
        else:
            print(f'Error while consuming: {message.error()}')
    else:
        # Process and store the clickstream data in HBase
        clickstream_data = message.value()
        # Extract relevant information from clickstream_data and store it in HBase using HBase client
        table.put('unique_identifier', {'click_data:user_id': '123', 'click_data:timestamp': '2023-07-21 12:34:56', 'click_data:url': 'example.com', 'geo_data:country': 'USA', 'geo_data:city': 'New York', 'user_agent_data:browser': 'Chrome', 'user_agent_data:os': 'Windows', 'user_agent_data:device': 'Desktop'})
