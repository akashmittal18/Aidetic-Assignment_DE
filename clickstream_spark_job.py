from pyspark.sql import SparkSession
from pyspark.sql.functions import col, countDistinct, avg
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, FloatType

def spark_job():
    # Initialize Spark session
    spark = SparkSession.builder.appName("ClickstreamProcessor").getOrCreate()

    # Define the HBase schema to infer the column names and types
    hbase_schema = StructType([
        StructField("click_data:user_id", StringType(), True),
        StructField("click_data:timestamp", StringType(), True),
        StructField("click_data:url", StringType(), True),
        StructField("geo_data:country", StringType(), True),
        StructField("geo_data:city", StringType(), True),
        StructField("user_agent_data:browser", StringType(), True),
        StructField("user_agent_data:os", StringType(), True),
        StructField("user_agent_data:device", StringType(), True)
    ])

    # Read data from HBase table
    hbase_table_name = "clickstream_table"
    hbase_conf = {
        "hbase.zookeeper.quorum": "localhost",
        "hbase.mapreduce.inputtable": hbase_table_name,
        "hbase.mapreduce.scan.row.start": "start_row_key",
        "hbase.mapreduce.scan.row.stop": "stop_row_key"
    }

    clickstream_df = spark.read.format("org.apache.hadoop.hbase.spark") \
        .options(**hbase_conf) \
        .schema(hbase_schema) \
        .load()

    # Perform data processing and aggregation
    aggregated_df = clickstream_df.groupBy("click_data:url", "geo_data:country") \
        .agg(
            countDistinct("click_data:user_id").alias("unique_users"),
            count("click_data:url").alias("num_clicks"),
            avg(col("click_data:timestamp").cast("long")).alias("avg_time_spent")
        )

    # Transform the aggregated data into a suitable format for indexing in Elasticsearch
    for column in aggregated_df.columns:
        new_column = column.split(":")[-1]  # Extract the column name
        aggregated_df = aggregated_df.withColumnRenamed(column, new_column)

    # Show the processed data (for demonstration purposes)
    aggregated_df.show()

    # Save the processed data to Elasticsearch
    es_output_conf = {
        "es.nodes": "localhost",
        "es.port": "9200",
        "es.resource": "clickstream_index/type",
        "es.mapping.id": "id"  # Unique identifier for each document
    }

    aggregated_df.write.format("org.elasticsearch.spark.sql") \
        .options(**es_output_conf) \
        .mode("overwrite") \
        .save()

    # Stop the Spark session
    spark.stop()

if __name__ == "__main__":
    spark_job()
