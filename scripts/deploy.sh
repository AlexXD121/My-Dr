#!/bin/bash

# Blue-Green Deployment Script
set -e

ENVIRONMENT=${1:-staging}
VERSION=${2:-latest}
HEALTH_CHECK_TIMEOUT=300
ROLLBACK_TIMEOUT=60

echo "Starting blue-green deployment for $ENVIRONMENT environment..."

# Color definitions
GREEN_ENV="green"
BLUE_ENV="blue"

# Determine current active environment
get_active_environment() {
    local current=$(docker-compose -f docker-compose.$ENVIRONMENT.yml ps --services --filter "status=running" | grep -E "(blue|green)" | head -1)
    if [[ $current == *"blue"* ]]; then
        echo "blue"
    elif [[ $current == *"green"* ]]; then
        echo "green"
    else
        echo "blue"  # Default to blue if none active
    fi
}

# Health check function
health_check() {
    local env=$1
    local max_attempts=$((HEALTH_CHECK_TIMEOUT / 10))
    local attempt=1
    
    echo "Performing health check for $env environment..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f -s "http://localhost:8000/health" > /dev/null 2>&1; then
            echo "Health check passed for $env environment"
            return 0
        fi
        
        echo "Health check attempt $attempt/$max_attempts failed, retrying in 10 seconds..."
        sleep 10
        ((attempt++))
    done
    
    echo "Health check failed for $env environment after $max_attempts attempts"
    return 1
}

# Rollback function
rollback() {
    local active_env=$1
    local inactive_env=$2
    
    echo "Rolling back to $active_env environment..."
    
    # Switch traffic back to previous environment
    docker-compose -f docker-compose.$ENVIRONMENT.yml up -d nginx-lb
    
    # Stop the failed deployment
    docker-compose -f docker-compose.$ENVIRONMENT.yml stop $inactive_env-backend $inactive_env-frontend
    
    echo "Rollback completed successfully"
}

# Main deployment logic
main() {
    local active_env=$(get_active_environment)
    local inactive_env
    
    if [ "$active_env" = "blue" ]; then
        inactive_env="green"
    else
        inactive_env="blue"
    fi
    
    echo "Current active environment: $active_env"
    echo "Deploying to inactive environment: $inactive_env"
    
    # Pull latest images
    echo "Pulling latest Docker images..."
    docker-compose -f docker-compose.$ENVIRONMENT.yml pull
    
    # Deploy to inactive environment
    echo "Starting deployment to $inactive_env environment..."
    docker-compose -f docker-compose.$ENVIRONMENT.yml up -d $inactive_env-backend $inactive_env-frontend
    
    # Wait for services to start
    sleep 30
    
    # Perform health check
    if health_check $inactive_env; then
        echo "Health check passed, switching traffic to $inactive_env environment..."
        
        # Update load balancer configuration to point to new environment
        sed -i "s/$active_env/$inactive_env/g" nginx-lb.conf
        docker-compose -f docker-compose.$ENVIRONMENT.yml up -d nginx-lb
        
        # Wait a bit for traffic to switch
        sleep 10
        
        # Perform final health check
        if health_check $inactive_env; then
            echo "Final health check passed, stopping old environment..."
            docker-compose -f docker-compose.$ENVIRONMENT.yml stop $active_env-backend $active_env-frontend
            echo "Deployment completed successfully!"
            
            # Clean up old images
            docker image prune -f
        else
            echo "Final health check failed, rolling back..."
            rollback $active_env $inactive_env
            exit 1
        fi
    else
        echo "Health check failed, rolling back..."
        rollback $active_env $inactive_env
        exit 1
    fi
}

# Trap to handle script interruption
trap 'echo "Deployment interrupted, cleaning up..."; exit 1' INT TERM

# Run main deployment
main

echo "Blue-green deployment completed successfully!"