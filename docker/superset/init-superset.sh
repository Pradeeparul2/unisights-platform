#!/bin/bash
set -e

# Install dependencies
pip install pydruid pillow 'setuptools<81'

# Upgrade database schema
superset db upgrade

# Check if admin user exists
if ! superset fab list-users | grep -q "admin"; then
  superset fab create-admin \
    --username admin \
    --firstname Admin \
    --lastname User \
    --email admin@example.com \
    --password SecureAdminPassword
fi

# Initialize Superset
superset init


# Add Druid database
superset set-database-uri \
  --database_name Druid \
  --uri "druid://broker:8082/druid/v2/sql/"

# === Import dashboards ===
if [ -f "/app/main_dashboard.zip" ]; then
  echo "Importing dashboard..."
  superset import-dashboards --path /app/main_dashboard.zip --username admin
else
  echo "Dashboard file /app/main_dashboard.zip not found. Skipping import."
fi

# Start Gunicorn
gunicorn -w 4 --timeout 120 -b 0.0.0.0:8088 'superset.app:create_app()'