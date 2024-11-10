FROM apache/airflow:2.10.2
ADD requirements.txt .

# Switch to root to perform the installation
USER root

RUN apt-get update && apt-get -y install libpq-dev gcc

# Switch back to airflow user after installation
USER airflow

#upgrade pip
RUN pip install --upgrade pip
RUN pip install apache-airflow==${AIRFLOW_VERSION} -r requirements.txt