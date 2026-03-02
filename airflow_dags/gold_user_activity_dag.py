from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from clickhouse_driver import Client

# Default arguments for DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# DAG definition (Airflow 3.x compatible)
dag = DAG(
    dag_id='gold_user_activity',
    default_args=default_args,
    description='Load Gold User Activity from Silver tables in ClickHouse',
    schedule='@daily',  # ✅ Updated for Airflow 3.x
    start_date=datetime(2026, 3, 1),
    catchup=False
)

# Python function to run ETL
def load_gold_user_activity():
    client = Client(
        host='clickhouse-server',  # name of your clickhouse container
        port=9000,
        user='default',
        password='mysecret'
    )

    # Insert aggregated data into gold_user_activity
    query = """
	INSERT INTO default.gold_user_activity (user_id, activity_date, total_actions)
	SELECT
	    u.user_id,
	    toDate(e.event_timestamp) AS activity_date,
	    count(e.event_id) AS total_actions
	FROM default.silver_users AS u
	LEFT JOIN default.silver_events AS e
	    ON u.user_id = e.user_id
	    AND toDate(e.event_timestamp) = yesterday()
	GROUP BY
	    u.user_id,
	    activity_date;

    """

    client.execute(query)
    print("Gold User Activity loaded successfully!")

# Define Airflow task
load_gold_task = PythonOperator(
    task_id='load_gold_user_activity',
    python_callable=load_gold_user_activity,
    dag=dag
)
