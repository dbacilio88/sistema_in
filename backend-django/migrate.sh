#!/bin/bash

echo "🔄 Creating Django migrations..."

# Navigate to Django project directory
cd /app

echo "📝 Making migrations for authentication app..."
python manage.py makemigrations authentication

echo "📝 Making migrations for devices app..."
python manage.py makemigrations devices

echo "📝 Making migrations for vehicles app..."
python manage.py makemigrations vehicles

echo "📝 Making migrations for infractions app..."
python manage.py makemigrations infractions

echo "📝 Making initial migrations if needed..."
python manage.py makemigrations

echo "🚀 Applying migrations..."
python manage.py migrate

echo "✅ Migrations completed successfully!"

echo "📊 Checking migration status..."
python manage.py showmigrations

echo "📈 Database tables created:"
python manage.py dbshell -c "\dt"