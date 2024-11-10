#!/usr/bin/env bash

# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

# ------------------------------------------------------------------------
# Creates the examples database and respective user. This database location
# and access credentials are defined on the environment variables
# ------------------------------------------------------------------------
# set -e

# psql -v ON_ERROR_STOP=1 --username "${POSTGRES_USER}" <<-EOSQL
#   CREATE USER ${EXAMPLES_USER} WITH PASSWORD '${EXAMPLES_PASSWORD}';
#   CREATE DATABASE ${EXAMPLES_DB};
#   GRANT ALL PRIVILEGES ON DATABASE ${EXAMPLES_DB} TO ${EXAMPLES_USER};
# EOSQL

# psql -v ON_ERROR_STOP=1 --username "${POSTGRES_USER}" -d "${EXAMPLES_DB}" <<-EOSQL
#    GRANT ALL ON SCHEMA public TO ${EXAMPLES_USER};
# EOSQL

set -e

echo "Creating users and granting permissions..."

# Create the EXAMPLES_USER and grant permissions
psql -v ON_ERROR_STOP=1 --username "${POSTGRES_USER}" <<-EOSQL
  CREATE USER ${EXAMPLES_USER} WITH PASSWORD '${EXAMPLES_PASSWORD}';
  CREATE DATABASE ${EXAMPLES_DB};
  GRANT ALL PRIVILEGES ON DATABASE ${EXAMPLES_DB} TO ${EXAMPLES_USER};
  ALTER ROLE ${EXAMPLES_USER} WITH CREATEDB;  
  ALTER ROLE ${EXAMPLES_USER} WITH SUPERUSER;
EOSQL

# Grant permissions for EXAMPLES_USER on the public schema of EXAMPLES_DB
psql -v ON_ERROR_STOP=1 --username "${POSTGRES_USER}" -d "${EXAMPLES_DB}" <<-EOSQL
   GRANT ALL ON SCHEMA public TO ${EXAMPLES_USER};
   ALTER ROLE ${EXAMPLES_USER} SET search_path TO public;
EOSQL

# Optionally set up default privileges for any new objects created by EXAMPLES_USER
psql -v ON_ERROR_STOP=1 --username "${POSTGRES_USER}" -d "${EXAMPLES_DB}" <<-EOSQL
  ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO ${EXAMPLES_USER};
  ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO ${EXAMPLES_USER};
  ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON FUNCTIONS TO ${EXAMPLES_USER};
EOSQL

# Create the 'airflow' user and grant permissions
psql -v ON_ERROR_STOP=1 --username "${POSTGRES_USER}" <<-EOSQL
  CREATE USER airflow WITH PASSWORD 'airflow';
  CREATE DATABASE airflow;
  GRANT ALL PRIVILEGES ON DATABASE airflow TO airflow;
  ALTER ROLE airflow WITH CREATEDB;
  ALTER ROLE airflow WITH SUPERUSER;
EOSQL

# Grant permissions for airflow user on the public schema of airflow database
psql -v ON_ERROR_STOP=1 --username "${POSTGRES_USER}" -d airflow <<-EOSQL
  GRANT ALL ON SCHEMA public TO airflow;
  ALTER ROLE airflow SET search_path TO public;
EOSQL

# Optionally set up default privileges for any new objects created by airflow user
psql -v ON_ERROR_STOP=1 --username "${POSTGRES_USER}" -d airflow <<-EOSQL
  ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO airflow;
  ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO airflow;
  ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON FUNCTIONS TO airflow;
EOSQL

# Grant permissions for all users on both airflow and EXAMPLES_DB databases and schemas
psql -v ON_ERROR_STOP=1 --username "${POSTGRES_USER}" <<-EOSQL
  GRANT ALL PRIVILEGES ON DATABASE ${EXAMPLES_DB} TO PUBLIC;
  GRANT ALL PRIVILEGES ON DATABASE airflow TO PUBLIC;
EOSQL

# Grant permissions for all users (PUBLIC) on the public schema of both databases
psql -v ON_ERROR_STOP=1 --username "${POSTGRES_USER}" -d "${EXAMPLES_DB}" <<-EOSQL
  GRANT ALL ON SCHEMA public TO PUBLIC;
EOSQL

psql -v ON_ERROR_STOP=1 --username "${POSTGRES_USER}" -d airflow <<-EOSQL
  GRANT ALL ON SCHEMA public TO PUBLIC;
EOSQL

# Set default privileges for all new objects created in public schema for all users (PUBLIC)
psql -v ON_ERROR_STOP=1 --username "${POSTGRES_USER}" -d "${EXAMPLES_DB}" <<-EOSQL
  ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO PUBLIC;
  ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO PUBLIC;
  ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON FUNCTIONS TO PUBLIC;
EOSQL

psql -v ON_ERROR_STOP=1 --username "${POSTGRES_USER}" -d airflow <<-EOSQL
  ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO PUBLIC;
  ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO PUBLIC;
  ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON FUNCTIONS TO PUBLIC;
EOSQL

echo "Users 'airflow' and '${EXAMPLES_USER}' with respective databases and permissions successfully created and configured. All users have access to the databases and schemas."
