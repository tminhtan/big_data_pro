#!/bin/bash

# Shell script to create directory structure

# Root directories
ROOT_DIRS=("config" "dags" "data" "docker" "logs" "models" "plugins" "src" "tests")

# Subdirectories for 'data'
DATA_DIRS=("db_airflow" "external" "postgres" "proceed" "raw" "redis" "superset" "superset_home")

# Subdirectories for 'docker'
DOCKER_DIRS=("airflow" "postgres" "superset")

# Subdirectories for 'docker/superset'
SUP_DIRS=("docker-entrypoint-initdb.d" "nginx" "pythonpath_dev" "superset-websocket")

# Subdirectories for 'models'
MODELS_DIRS=("v1")

# Subdirectories for 'plugins'
PLUGINS_DIRS=("__pycache__")

# Subdirectories for 'src'
SRC_DIRS=("data" "features" "models" "utils" "visualization")

# Subdirectories for 'src/visualization/dashboard_export_20241113T092443'
DASHBOARD_DIRS=("charts" "dashboards" "databases" "datasets")

# Create root directories
for DIR in "${ROOT_DIRS[@]}"; do
    mkdir -p "$DIR"
done

# Create subdirectories in 'data'
for DIR in "${DATA_DIRS[@]}"; do
    mkdir -p "data/$DIR"
done

# Create subdirectories in 'docker'
for DIR in "${DOCKER_DIRS[@]}"; do
    mkdir -p "docker/$DIR"
done

# Create subdirectories in 'docker/superset'
for DIR in "${SUP_DIRS[@]}"; do
    mkdir -p "docker/superset/$DIR"
done

# Create subdirectories in 'models'
for DIR in "${MODELS_DIRS[@]}"; do
    mkdir -p "models/$DIR"
done

# Create subdirectories in 'plugins'
for DIR in "${PLUGINS_DIRS[@]}"; do
    mkdir -p "plugins/$DIR"
done

# Create subdirectories in 'src'
for DIR in "${SRC_DIRS[@]}"; do
    mkdir -p "src/$DIR"
done

# Create 'src/visualization/dashboard_export_20241113T092443' and its subdirectories
mkdir -p "src/visualization/dashboard_export_20241113T092443"
for DIR in "${DASHBOARD_DIRS[@]}"; do
    mkdir -p "src/visualization/dashboard_export_20241113T092443/$DIR"
done

# Create 'src/visualization/dashboard_export_20241113T092443/datasets/PostgreSQL'
mkdir -p "src/visualization/dashboard_export_20241113T092443/datasets/PostgreSQL"

# Print completion message
echo "All directories have been successfully created or already exist."
