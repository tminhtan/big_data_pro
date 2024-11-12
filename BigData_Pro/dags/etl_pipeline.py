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

    # Function to print success message
def print_success_message(**kwargs):
    print("Success: The Load Data Pipeline DAG completed successfully.")

    # Function to print failure message
def print_failure_message(**kwargs):
    print("Failure: The Load Data Pipeline DAG failed. Check logs for details.")

# Define AIRFLOW_PATH as a Variable for flexibility and maintainability
AIRFLOW_PATH = Variable.get("AIRFLOW_PATH", "/opt/airflow/")

# Default DAG arguments for reliability and error handling
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
    dag_id='etl_pipeline',  # Updated DAG ID to avoid conflicts
    description='ETL data pipeline to crawling data, extract, tranform and ....',
    default_args=default_args,
    start_date=days_ago(1),
    schedule_interval=timedelta(days=1),
    catchup=False,
    max_active_runs=1,
    tags=['data_pipeline', 'etl', 'advanced']
) as dag:

    # LatestOnlyOperator to run tasks only on latest scheduled execution
    latest_only = LatestOnlyOperator(task_id='latest_only')

    # Task group for data crawling, model extraction, and DB import
    with TaskGroup("data_processing_tasks") as data_processing_tasks:

        # Task to run data crawling
        run_data_crawling = BashOperator(
            task_id='run_data_crawling',
            bash_command=f'python3 {AIRFLOW_PATH}src/data/crawl_data.py',
            retries=3,
            retry_delay=timedelta(minutes=1)
        )

        # Task to run model extraction
        run_model_extraction = BashOperator(
            task_id='run_model_extraction',
            bash_command=f'python3 {AIRFLOW_PATH}src/models/big_data.py'
        )

        # Task to run database import
        run_db_import = BashOperator(
            task_id='run_db_import',
            bash_command=f'python3 {AIRFLOW_PATH}src/data/dbproceed.py'
        )

        # Define dependencies within the group
        run_data_crawling >> run_model_extraction >> run_db_import

    # BranchPythonOperator to conditionally skip DB import based on custom logic
    def check_condition():
        # Placeholder condition, modify as needed
        condition_met = True
        return 'data_processing_tasks' if condition_met else 'skip_db_import'

    branching_task = BranchPythonOperator(
        task_id='check_condition',
        python_callable=check_condition,
    )

    skip_db_import = DummyOperator(task_id='skip_db_import')

    # Notifications for success and failure
    # success_notification = EmailOperator(
    #     task_id='send_success_email',
    #     to='tminhtan334@gmail.com',
    #     subject='Load Data Pipeline DAG Success',
    #     html_content='The Load Data Pipeline DAG completed successfully.'
    # )

    # failure_notification = EmailOperator(
    #     task_id='send_failure_email',
    #     to='tminhtan334@gmail.com',
    #     subject='Load Data Pipeline DAG Failure',
    #     html_content='The Load Data Pipeline DAG failed. Check logs for details.',
    #     trigger_rule='one_failed'  # Triggers if any upstream task fails
    # )


    # Task for success notification (prints success message)
    success_notification = PythonOperator(
        task_id='send_success_message',
        python_callable=print_success_message,
        trigger_rule='all_success',  # This triggers if all upstream tasks succeed
        dag=dag,
    )

    # Task for failure notification (prints failure message)
    failure_notification = PythonOperator(
        task_id='send_failure_message',
        python_callable=print_failure_message,
        trigger_rule='one_failed',  # This triggers if any upstream task fails
        dag=dag,
    )


    # DAG dependencies and notification triggers
    # latest_only >> branching_task
    # branching_task >> data_processing_tasks >> success_notification
    # branching_task >> skip_db_import
    # [data_processing_tasks, skip_db_import] >> failure_notification

    latest_only >> branching_task
    branching_task >> [data_processing_tasks, skip_db_import]
    data_processing_tasks >> success_notification
    [data_processing_tasks, skip_db_import] >> failure_notification
