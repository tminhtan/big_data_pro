from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import pandas as pd
import os

# Hàm tạo file CSV
def create_csv_file():
    # Dữ liệu mẫu
    data = {
        'Name': ['Alice', 'Bob', 'Charlie'],
        'Age': [24, 30, 22],
        'City': ['New York', 'Los Angeles', 'Chicago']
    }

    # Tạo DataFrame từ dữ liệu
    df = pd.DataFrame(data)

    # Chỉ định đường dẫn lưu file CSV
    output_file_path = 'D:/Code/KHDL-Pro/BigData_Pro/data/raw/test.csv'  # Thay đổi đường dẫn này cho phù hợp

    # Kiểm tra xem thư mục có tồn tại không, nếu không thì tạo mới
    os.makedirs(os.path.dirname(output_file_path), exist_ok=True)

    # Lưu DataFrame vào file CSV
    df.to_csv(output_file_path, index=False)

    print('done')

        # Get the current working directory (pwd)
    current_location = os.getcwd()
    
    # Get the absolute path of this script
    script_location = os.path.abspath(__file__)
    
    print(f"Current working directory (pwd): {current_location}")
    print(f"Script location: {script_location}")

# Định nghĩa DAG
default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 10, 19),
    'retries': 1,
}

with DAG(
    'csv_creation_dag',
    default_args=default_args,
    description='A simple DAG to create a CSV file',
    schedule_interval='@daily',
) as dag:

    create_csv_task = PythonOperator(
        task_id='create_csv',
        python_callable=create_csv_file,
    )

    create_csv_task
