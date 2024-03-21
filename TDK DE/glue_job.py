##This Glue job will read data from an S3 bucket, process it to calculate the required KPIs, and then load the results into an Oracle database table.

import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from pyspark.sql import SparkSession

## @params: [JOB_NAME]
args = getResolvedOptions(sys.argv, ['JOB_NAME'])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Read data from S3
input_bucket = "s3://sample-input-bucket"
input_path = "sample/input/path"
datasource0 = glueContext.create_dynamic_frame.from_catalog(database = "sample_database_name", table_name = "sample_table_name", transformation_ctx = "datasource0")

# Convert DynamicFrame to DataFrame
df = datasource0.toDF()

# Calculate KPIs
num_users = df.selectExpr("COUNT(DISTINCT user_id) AS num_users").collect()[0]["num_users"]
num_requests_per_user = df.groupBy("user_id").count().withColumnRenamed("count", "num_requests")
total_successful_requests = df.filter(df.status == "success").count()

# Load KPIs into Oracle DB
output_jdbc_url = "jdbc:oracle:thin:@sample_oracle_db_host:sample_oracle_db_port:sample_oracle_db_name"
output_table = "sample_output_table_name"
output_username = "sample_username"
output_password = "sample_password"

df_kpis = spark.createDataFrame([(num_users,)], ["num_users"])
df_kpis = df_kpis.withColumn("num_requests", lit(num_requests_per_user))
df_kpis = df_kpis.withColumn("total_successful_requests", lit(total_successful_requests))

df_kpis.write \
    .format("jdbc") \
    .option("url", output_jdbc_url) \
    .option("dbtable", output_table) \
    .option("user", output_username) \
    .option("password", output_password) \
    .mode("overwrite") \
    .save()

job.commit()
