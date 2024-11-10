from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator


AIRFLOW_PATH = "/opt/airflow/"


# Set default parameters for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 11, 7),  # Adjust the start date if necessary
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

# Create the DAG
dag = DAG(
    dag_id='load_data_pipeline',  # Unique and descriptive DAG ID
    default_args=default_args,
    description='A simple data pipeline DAG',
    schedule_interval=timedelta(days=1),  # Schedule to run daily
)

# Task to run the data loader script
run_data_crawling = BashOperator(
    task_id='run_data_crawling',
    bash_command=f'python3 {AIRFLOW_PATH}src/data/crawl_data.py',  # Update with the correct absolute path
    dag=dag,
)

run_model_extraction = BashOperator(
    task_id='run_model_extraction',
    bash_command=f'python3 {AIRFLOW_PATH}src/models/big_data.py',  # Update with the correct absolute path
    dag=dag,
)

run_db_import = BashOperator(
    task_id='run_db_import',
    bash_command=f'python3 {AIRFLOW_PATH}src/data/dbproceed.py',  # Update with the correct absolute path
    dag=dag,
)

# Additional tasks can be added here, with defined execution order
run_data_crawling >> run_model_extraction >> run_db_import

#run_model_extraction >> run_db_import
