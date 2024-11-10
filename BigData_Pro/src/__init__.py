#====================================================================#
#       All parameter and linking, location path will be define here
#       To use: import src
#       call var: src.AIRFLOW_PATH
#====================================================================#

import os

def is_running_in_docker():
    # Checking file /proc/1/cgroup available in docker env
    try:
        with open('/proc/1/cgroup', 'rt') as f:
            for line in f:
                if 'docker' in line or 'kubepods' in line:
                    return True
    except FileNotFoundError:
        pass

    # Checking env var
    if os.environ.get('DOCKER_ENV') == 'true':
        return True

    return False

if is_running_in_docker():
    AIRFLOW_PATH = "/opt/airflow"
else:
    AIRFLOW_PATH = "."


# AIRFLOW_PATH = "/opt/airflow"
# AIRFLOW_PATH = "."
product_link = f'{AIRFLOW_PATH}/data/raw/ProductDetail.xlsx'
comment_link = f'{AIRFLOW_PATH}/data/raw/Comment.xlsx'
recommend_link = f'{AIRFLOW_PATH}/data/proceed/final_pair.csv'
host = "localhost"
port = 5432
database = "tikidb"
user = 'airflow'
password = 'airflow'


print(recommend_link)