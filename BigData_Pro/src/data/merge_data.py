import pandas as pd
import argparse
import os

# Đường dẫn đến file CSV trong hệ thống tệp
def get_airflow_path():
    # Kiểm tra các dấu hiệu thường gặp của môi trường Docker
    if os.path.exists('/.dockerenv') or os.path.isfile('/proc/self/cgroup'):
        return "/opt/airflow"
    else:
        return "."

# Sử dụng hàm để thiết lập AIRFLOW_PATH
AIRFLOW_PATH = get_airflow_path()
print(f"AIRFLOW_PATH is set to: {AIRFLOW_PATH}")

# AIRFLOW_PATH = "/opt/airflow"
# # AIRFLOW_PATH = "."


data_store=(f'{AIRFLOW_PATH}/')
product_link = (f'{AIRFLOW_PATH}/data/raw/ProductDetail.csv')
comment_link = (f'{AIRFLOW_PATH}/data/raw/Comment.csv')
recommend_link = (f'{AIRFLOW_PATH}/data/proceed/final_pair.csv')

host="host.docker.internal"
port = 5432
database = "tikidb"
user = 'airflow'
password = 'airflow'

file_path=product_link
def merge_comment_csv_files():

    try:
        # List to hold DataFrames
        dfs = []

        # Loop through the range of files (0, 1, 2) and read them into DataFrames
        for i in range(3):
            tmp_product_link = f'{AIRFLOW_PATH}/data/raw/Comment{i}.csv'
            df = pd.read_csv(tmp_product_link)
            dfs.append(df)

        # Concatenate all DataFrames into one
        merged_df = pd.concat(dfs, ignore_index=True)

        # Define output path for the merged file
        output_path = f'{AIRFLOW_PATH}/data/raw/Comment_merge.csv'

        # Save the merged DataFrame to the output file
        merged_df.to_csv(output_path, index=False)

        print(f"CSV files have been merged and saved as '{output_path}'.")
    
    except Exception as e:
        print(f"Error occurred: {e}")

def merge_product_csv_files():

    try:
        # List to hold DataFrames
        dfs = []

        # Loop through the range of files (0, 1, 2) and read them into DataFrames
        for i in range(3):
            tmp_product_link = f'{AIRFLOW_PATH}/data/raw/ProductDetail{i}.csv'
            df = pd.read_csv(tmp_product_link)
            dfs.append(df)

        # Concatenate all DataFrames into one
        merged_df = pd.concat(dfs, ignore_index=True)

        # Define output path for the merged file
        output_path = f'{AIRFLOW_PATH}/data/raw/ProductDetail_merge.csv'

        # Save the merged DataFrame to the output file
        merged_df.to_csv(output_path, index=False)

        print(f"CSV files have been merged and saved as '{output_path}'.")
    
    except Exception as e:
        print(f"Error occurred: {e}")

# Example of how to call the function directly
if __name__ == "__main__":


    # Call the function with parsed arguments
    merge_product_csv_files()
    merge_comment_csv_files()

