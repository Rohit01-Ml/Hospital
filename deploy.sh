#!/bin/bash
# Run this on your DigitalOcean server to deploy/update the app

set -e

echo "Pulling latest code..."
git pull origin main

echo "Building and restarting containers..."
docker-compose down
docker-compose up -d --build

echo "Seeding database (safe to run multiple times)..."
docker-compose exec backend python -m app.seed

echo "Done! App is live."
docker-compose ps
