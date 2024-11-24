# Project Name

## Overview

This project is a data pipeline built using Apache Airflow, designed for ETL process that include Extract, transform, load. We use the data that crawling from the e-commerce platform. Date ưill be chage into  data ingestion, preprocessing, model training, and visualization. 
Morever, our team use the Apache superset, Microsoft Power BI to visualize the data that compare the correspond relation between data.
We use the PostgreSQL database to store data, and using the Adminer application for easy manage this database.

All of component are build into container that managed by Docker.

The structure follows best practices for organizing files and directories to ensure maintainability and scalability.

## Project Structure

```plaintext
<project_name>/
│
├── config/
│   ├── db_config.yaml
│   └── model_config.yaml
│
├── data/
│   ├── external/
│   ├── processed/
|   ├── db_airflow
|   ├── postgres
|   ├── redis
|   ├── superset
|   ├── superset_home
│   └── raw/
|   
│
├── dags/
│   ├── __init__.py
│   ├── data_pipeline.py
|   ├── etl_pipeline.py
│   ├── model_training.py
│   └── db_utils.py
│
├── docker/
│   ├── airflow/
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   ├── postgres/
│   │   ├── Dockerfile
│   │   └── init.sql
|   ├── supserset
│   │   └── ...
│   │   └── ...
│
├── docker-compose.yml
│
├── logs/
│
├── models/
│   ├── <model_name>/
│   │   └── v1/
│   ├── trained_model.pkl
│   └── model_utils.py
│
├── plugins/
│   ├── __init__.py
│   ├── custom_operators.py
│   └── custom_hooks.py
│
├── requirements.txt
│
├── src/
│   ├── __init__.py
│   ├── data/
│   │   ├── make_dataset.py
│   │   ├── crawl_data.py
│   │   ├── dbproceed.py
│   │   └── merge_date.py
│   ├── features/
│   │   └── build_features.py
│   ├── models/
│   │   └── big_data.py
│   ├── utils/
│   │   ├── file_utils.py
│   │   └── logging_utils.py
│   └── visualization/
│   │   ├── dashboard_export_20241113T092443
│   │   ├── BaoCao.pdix
│       └── visualize.py
│
└── setup.py
│
└── tests/
    ├── test_dag.py
    ├── test_data.py
    ├── test_features.py
    ├── test_models.py
    └── test_visualization.py

other components that not list in this series
```

## Getting Started

### Prerequisites

- Python 3.11+
- Apache Airflow
- Docker (for running containers)
- Docker Compose (for orchestrating multiple containers)

### Installation

1. Clone the repository:

   ```bash
   git clone 
   ```

### Running the Project

1. **Build and run Docker containers**:
   Change the loction into the 'BigData_pro' folder, that contain all source code, include docker-compose.yml

   Up the docker
   ```bash
   docker-compose up
   ```

4. **Access Apache Airflow**:

   Open your web browser and navigate to `http://localhost:8080` to access the Airflow dashboard with usr/password: superset/superset

5. **Access Apache Superset**:

   Open your web browser and navigate to `http://localhost:8088` to access the Superset dashboard with usr/password: admin/admin

6. **Access Apache Superset**:

   Open your web browser and navigate to `http://localhost:8000` to access the Adminer dashboard with usr/password: superset/superset
   
8. PostgreSQL working on port 5432 with usr/password: superset/superset

9. **Trigger DAGs**:

   - Navigate to the "DAGs" tab in the Airflow dashboard to see available DAGs.
   - You can manually trigger the data pipeline and model training DAGs from the UI.
  
**************** MAKE SURE YOUR FIREWALL WAS UNBLOCK ********************************

## DAG Files Description

### `dags/etl_pipeline.py`

This file contains the DAG for the data ingestion and preprocessing pipeline. It orchestrates the data flow from external sources to the data storage locations, including raw and processed directories. It might include tasks such as:

- Extracting data from external sources
- Loading and cleaning the data
- Saving the cleaned data to the processed directory


## Source Code Description

### `src/data/`

- **`crawl_data.py`**: This script is responsible for crawling data from the internet
  
- **`dbproceed.py`**: This file contains utility functions to load data into database. It might handle data batching and preprocessing to prepare data for training and evaluation.

### `src/features/`

- **`build_features.py`**: This script is designed to create features from the raw data. It might include methods for feature engineering, selection, and transformation that are critical for model performance.

### `src/models/`
  
- **`big_data.py`**: This script is responsible for training the machine learning model using the features created from the dataset. It includes model selection, training loops, and hyperparameter tuning.


### `src/utils/`

- **`file_utils.py`**: This script includes utility functions for file operations, such as reading and writing files, managing file paths, and checking file existence.

- **`logging_utils.py`**: This file sets up logging configurations for the project, ensuring that logs are captured consistently across all scripts.

### `src/visualization/`

- **`visualize.py`**: This script is responsible for creating visualizations to help understand the data and model performance. It may include functions to plot data distributions, training progress, and evaluation metrics.
- **`dashboard_export_20241113T092443.zip`**: this file include configuration file that virsiualize the data on Apache Superset
- **`BaoCao.pdix`**: this file include configuration file that virsiualize the data on PowerBI

## Data Organization

- **`data/external/`**: Store external datasets here.
- **`data/processed/`**: Processed datasets can be saved in this directory.
- **`data/raw/`**: Keep raw data files in this directory.
- **`data/db_airflow/`**: saving airflow system file
- **`data/postgres/`**:  saving PostgreSQL configuration
- **`data/redis/`**: cache data for enviroment manage by redis
- **`data/superset_home/`**: include the data of superset

## Custom Plugins

The `plugins/` directory allows you to define custom operators and hooks for Airflow. This helps in extending the functionality of Airflow to fit your specific needs.

## Testing

Unit tests are included in the `tests/` directory. You can run tests using:


## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

## License

This project is licensed under me-khdl-k33

## Acknowledgements

- Apache Airflow for orchestration
- Docker for containerization
- Python for backend development

## Contact

For any inquiries, please contact 
```bash
[my.email@mail]
```
