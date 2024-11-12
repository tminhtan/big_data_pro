from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python_operator import PythonOperator # type: ignore
from airflow.operators.email import EmailOperator
from airflow.utils.dates import days_ago
from airflow.utils.task_group import TaskGroup
from airflow.models import Variable
from airflow.operators.dummy import DummyOperator # type: ignore
from airflow.operators.latest_only import LatestOnlyOperator
from airflow.operators.python import BranchPythonOperator


AIRFLOW_PATH = Variable.get("AIRFLOW_PATH", "/opt/airflow/")

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': True,
    'email_on_retry': False,
    'email': ['alert@example.com'],  # Replace with actual email(s)
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

# Define the DAG
with DAG(
    dag_id='parallel_tasks_with_failure_tracking',  # Updated DAG ID to avoid conflicts
    description='test',
    default_args=default_args,
    start_date=days_ago(1),
    schedule_interval=timedelta(days=1),
    catchup=False,
    max_active_runs=1,
    tags=['data_pipeline', 'etl', 'advanced']
) as dag:


    task_1 = BashOperator(
        task_id='run_data_crawling_1',
        bash_command=f'python3 {AIRFLOW_PATH}src/data/crawl_data_test.py --param1 0',
        retries=3,
        retry_delay=timedelta(minutes=1)
    )

    task_2 = BashOperator(
        task_id='run_data_crawling_2',
        bash_command=f'python3 {AIRFLOW_PATH}src/data/crawl_data_test.py --param1 1',
        retries=3,
        retry_delay=timedelta(minutes=1)
    )

    task_3 = BashOperator(
        task_id='run_data_crawling_3',
        bash_command=f'python3 {AIRFLOW_PATH}src/data/crawl_data_test.py --param1 2',
        retries=3,
        retry_delay=timedelta(minutes=1)
    )


    final_task = BashOperator(
        task_id='merge_data',
        bash_command=f'python3 {AIRFLOW_PATH}src/data/merge_data.py',
        retries=3,
        retry_delay=timedelta(minutes=1)
    )

# Set the tasks' dependencies:
# task_1, task_2, and task_3 should run in parallel, followed by final_task
    [task_1, task_2, task_3] >> final_task
