@echo off
set "project_name=%1"

if "%project_name%"=="" (
    echo Usage: create_project.bat project_name
    exit /b 1
)

:: Create main project directory
mkdir "%project_name%"

:: Create dags directory and files
mkdir "%project_name%\dags"
type nul > "%project_name%\dags\__init__.py"
type nul > "%project_name%\dags\data_pipeline.py"
type nul > "%project_name%\dags\model_training.py"
type nul > "%project_name%\dags\db_utils.py"

:: Create plugins directory and files
mkdir "%project_name%\plugins"
type nul > "%project_name%\plugins\__init__.py"
type nul > "%project_name%\plugins\custom_operators.py"
type nul > "%project_name%\plugins\custom_hooks.py"

:: Create src directory and its subdirectories and files
mkdir "%project_name%\src"
type nul > "%project_name%\src\__init__.py"

:: Create src/data directory and files
mkdir "%project_name%\src\data"
type nul > "%project_name%\src\data\make_dataset.py"
type nul > "%project_name%\src\data\data_loader.py"

:: Create src/features directory and files
mkdir "%project_name%\src\features"
type nul > "%project_name%\src\features\build_features.py"

:: Create src/models directory and files
mkdir "%project_name%\src\models"
type nul > "%project_name%\src\models\predict_model.py"
type nul > "%project_name%\src\models\train_model.py"
type nul > "%project_name%\src\models\model_utils.py"

:: Create src/visualization directory and files
mkdir "%project_name%\src\visualization"
type nul > "%project_name%\src\visualization\visualize.py"

:: Create src/utils directory and files
mkdir "%project_name%\src\utils"
type nul > "%project_name%\src\utils\file_utils.py"
type nul > "%project_name%\src\utils\logging_utils.py"

:: Create data directory and subdirectories
mkdir "%project_name%\data"
mkdir "%project_name%\data\external"
mkdir "%project_name%\data\processed"
mkdir "%project_name%\data\raw"

:: Create models directory and files
mkdir "%project_name%\models"
set /p model_name="Enter model name (for example 'my_model'): "
mkdir "%project_name%\models\%model_name%"
mkdir "%project_name%\models\%model_name%\v1"
type nul > "%project_name%\models\trained_model.pkl"
type nul > "%project_name%\models\model_utils.py"

:: Create requirements file
type nul > "%project_name%\requirements.txt"

:: Create config directory and files
mkdir "%project_name%\config"
type nul > "%project_name%\config\db_config.yaml"
type nul > "%project_name%\config\model_config.yaml"

:: Create docker directory and files
mkdir "%project_name%\docker"
type nul > "%project_name%\docker\Dockerfile"

:: Create docker/airflow directory and files
mkdir "%project_name%\docker\airflow"
type nul > "%project_name%\docker\airflow\Dockerfile"
type nul > "%project_name%\docker\airflow\requirements.txt"

:: Create docker/postgres directory and files
mkdir "%project_name%\docker\postgres"
type nul > "%project_name%\docker\postgres\Dockerfile"
type nul > "%project_name%\docker\postgres\init.sql"

:: Download the docker-compose.yml file
echo Downloading docker-compose.yml from Apache Airflow...
curl -L -o "%project_name%\docker-compose.yml" https://airflow.apache.org/docs/apache-airflow/2.10.2/docker-compose.yaml

:: Create setup.py file
type nul > "%project_name%\setup.py"

:: Create logs directory
mkdir "%project_name%\logs"

:: Create tests directory and files
mkdir "%project_name%\tests"
type nul > "%project_name%\tests\test_dag.py"
type nul > "%project_name%\tests\test_data.py"
type nul > "%project_name%\tests\test_features.py"
type nul > "%project_name%\tests\test_models.py"
type nul > "%project_name%\tests\test_visualization.py"

echo Project structure created successfully!
