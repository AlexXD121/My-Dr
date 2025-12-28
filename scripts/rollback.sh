#!/bin/bash

# Rollback Script for Blue-Green Deployment
set -e

ENVIRONMENT=${1:-staging}
TARGET_VERSION=${2:-previous}

echo "Starting rollback for $ENVIRONMENT environment..."

# Get deployment history
get_deployment_history() {
    docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.CreatedAt}}" | grep mydoc | head -10
}

# Rollback to previous version
rollback_to_previous() {
    local env=$1
    
    echo "Rolling back $env environment to previous version..."
    
    # Get previous image tags
    local previous_backend=$(docker images --format "{{.Repository}}:{{.Tag}}" | grep mydoc-backend | sed -n '2p')
    local previous_frontend=$(docker images --format "{{.Repository}}:{{.Tag}}" | grep mydoc-frontend | sed -n '2p')
    
    if [ -z "$previous_backend" ] || [ -z "$previous_frontend" ]; then
        echo "Error: Could not find previous version images"
        exit 1
    fi
    
    echo "Rolling back to:"
    echo "  Backend: $previous_backend"
    echo "  Frontend: $previous_frontend"
    
    # Update docker-compose with previous images
    export BACKEND_IMAGE=$previous_backend
    export FRONTEND_IMAGE=$previous_frontend
    
    # Deploy previous version
    docker-compose -f docker-compose.$ENVIRONMENT.yml up -d
    
    # Health check
    sleep 30
    if curl -f -s "http://localhost:8000/health" > /dev/null 2>&1; then
        echo "Rollback completed successfully!"
        echo "Previous version is now active"
    else
        echo "Rollback failed - service health check failed"
        exit 1
    fi
}

# Main rollback logic
main() {
    echo "Current deployment history:"
    get_deployment_history
    echo ""
    
    read -p "Are you sure you want to rollback $ENVIRONMENT environment? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rollback_to_previous $ENVIRONMENT
    else
        echo "Rollback cancelled"
        exit 0
    fi
}

# Run main rollback
main

echo "Rollback process completed!"