##This Lambda function code written in Python updates the summary tables in the Oracle database after the Glue ETL job completes successfully:

import boto3
import psycopg2
from psycopg2 import Error

def lambda_handler(event, context):
    # Extract necessary information from the event
    glue_job_status = event['detail']['state']
    
    # Check if Glue ETL job succeeded
    if glue_job_status == 'SUCCEEDED':
        try:
            # Connect to the Oracle database
            conn = psycopg2.connect(
                dbname='sample_database_name',
                user='sample_username',
                password='sample_password',
                host='sample_oracle_db_host',
                port='sample_oracle_db_port'
            )
            
            # Create a cursor object
            cursor = conn.cursor()
            
            # SQL queries to calculate KPIs and update the summary table
            sql_queries = [
                "UPDATE summary_table SET num_users = (SELECT COUNT(DISTINCT user_id) FROM user_requests)",
                "UPDATE summary_table SET num_requests_per_user = (SELECT user_id, COUNT(request_id) FROM user_requests GROUP BY user_id)",
                "UPDATE summary_table SET total_successful_requests = (SELECT COUNT(*) FROM user_requests WHERE status = 'success')"
            ]
            
            # Execute SQL queries
            for query in sql_queries:
                cursor.execute(query)
                
            # Commit the transaction
            conn.commit()
            
            # Close cursor and connection
            cursor.close()
            conn.close()
            
            return {
                'statusCode': 200,
                'body': 'Summary table updated successfully'
            }
        
        except Error as e:
            return {
                'statusCode': 500,
                'body': f'Error: {e}'
            }
    
    else:
        return {
            'statusCode': 400,
            'body': f'Glue ETL job failed with status: {glue_job_status}'
        }


##The above function listens for CloudWatch Events triggered by the Glue ETL job completion. Upon successful completion (SUCCEEDED state), the function connects to the Oracle database and executes SQL queries to calculate the required KPIs and update the summary table. If any error occurs during this process, it returns an error response.