#!/bin/bash

# Kubernetes Rollback Script
set -e

ENVIRONMENT=${1:-staging}
NAMESPACE="mydoc-$ENVIRONMENT"

echo "Rolling back Kubernetes deployment in $ENVIRONMENT environment..."

# Validate environment
if [[ "$ENVIRONMENT" != "staging" && "$ENVIRONMENT" != "production" ]]; then
    echo "Error: Environment must be 'staging' or 'production'"
    exit 1
fi

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo "Error: kubectl is not installed or not in PATH"
    exit 1
fi

# Show current rollout history
echo "Current rollout history for backend:"
kubectl rollout history deployment/backend -n $NAMESPACE

echo "Current rollout history for frontend:"
kubectl rollout history deployment/frontend -n $NAMESPACE

# Confirm rollback
read -p "Are you sure you want to rollback $ENVIRONMENT environment? (y/N): " -n 1 -r
echo

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Rollback cancelled"
    exit 0
fi

# Rollback backend
echo "Rolling back backend deployment..."
kubectl rollout undo deployment/backend -n $NAMESPACE

# Rollback frontend
echo "Rolling back frontend deployment..."
kubectl rollout undo deployment/frontend -n $NAMESPACE

# Wait for rollback to complete
echo "Waiting for backend rollback to complete..."
kubectl rollout status deployment/backend -n $NAMESPACE --timeout=300s

echo "Waiting for frontend rollback to complete..."
kubectl rollout status deployment/frontend -n $NAMESPACE --timeout=300s

# Verify rollback
echo "Verifying rollback..."
kubectl get pods -n $NAMESPACE

# Health check
echo "Performing health check after rollback..."
sleep 30

if [[ "$ENVIRONMENT" == "staging" ]]; then
    HEALTH_URL="https://staging.mydoc.app/api/health"
else
    HEALTH_URL="https://mydoc.app/api/health"
fi

if curl -f -s "$HEALTH_URL" > /dev/null 2>&1; then
    echo "Health check passed after rollback!"
else
    echo "Warning: Health check failed after rollback"
    exit 1
fi

echo "Rollback completed successfully!"

# Show final status
echo "Final deployment status:"
kubectl get all -n $NAMESPACE