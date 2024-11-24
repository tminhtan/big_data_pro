@echo off
:: Batch file to create directory structure

:: Root directories
set ROOT_DIRS=config dags data docker logs models plugins src tests

:: Subdirectories for 'data'
set DATA_DIRS=db_airflow external postgres proceed raw redis superset superset_home

:: Subdirectories for 'docker'
set DOCKER_DIRS=airflow postgres superset

:: Subdirectories for 'docker\superset'
set SUP_DIRS=docker-entrypoint-initdb.d nginx pythonpath_dev superset-websocket

:: Subdirectories for 'models'
set MODELS_DIRS=v1

:: Subdirectories for 'plugins'
set PLUGINS_DIRS=__pycache__

:: Subdirectories for 'src'
set SRC_DIRS=data features models utils visualization

:: Subdirectories for 'src\visualization\dashboard_export_20241113T092443'
set DASHBOARD_DIRS=charts dashboards databases datasets

:: Create root directories
for %%R in (%ROOT_DIRS%) do if not exist "%%R" mkdir "%%R"

:: Create subdirectories in 'data'
for %%D in (%DATA_DIRS%) do if not exist "data\%%D" mkdir "data\%%D"

:: Create subdirectories in 'docker'
for %%D in (%DOCKER_DIRS%) do if not exist "docker\%%D" mkdir "docker\%%D"

:: Create subdirectories in 'docker\superset'
for %%S in (%SUP_DIRS%) do if not exist "docker\superset\%%S" mkdir "docker\superset\%%S"

:: Create subdirectories in 'models'
for %%M in (%MODELS_DIRS%) do if not exist "models\%%M" mkdir "models\%%M"

:: Create subdirectories in 'plugins'
for %%P in (%PLUGINS_DIRS%) do if not exist "plugins\%%P" mkdir "plugins\%%P"

:: Create subdirectories in 'src'
for %%S in (%SRC_DIRS%) do if not exist "src\%%S" mkdir "src\%%S"

:: Print completion message
echo All directories have been successfully created or already exist.
pause
