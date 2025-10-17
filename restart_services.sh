#!/bin/bash

# Maids of CyFair - Service Restart Script
# This script restarts all services

set -e

echo "🔄 Restarting Maids of CyFair Services..."

# Stop services
./stop_services.sh

# Wait a moment
sleep 2

# Start services
./start_services.sh

echo "✅ All services restarted successfully!"

