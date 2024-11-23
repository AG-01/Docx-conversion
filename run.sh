
set -e

echo "Building Docker images..."
docker-compose build

echo "Starting Docker containers..."
docker-compose up -d

echo "All containers are up and running."

# List the running containers
docker-compose ps