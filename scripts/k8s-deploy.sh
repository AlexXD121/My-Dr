#!/bin/bash

# Kubernetes Deployment Script
set -e

ENVIRONMENT=${1:-staging}
NAMESPACE="mydoc-$ENVIRONMENT"
KUBECTL_TIMEOUT=300

echo "Deploying to Kubernetes $ENVIRONMENT environment..."

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

# Check cluster connectivity
if ! kubectl cluster-info &> /dev/null; then
    echo "Error: Cannot connect to Kubernetes cluster"
    exit 1
fi

# Apply namespace
echo "Creating/updating namespace..."
kubectl apply -f k8s/namespace.yaml

# Apply secrets (only if they don't exist)
echo "Applying secrets..."
if ! kubectl get secret mydoc-secrets -n $NAMESPACE &> /dev/null; then
    kubectl apply -f k8s/secrets.yaml
    echo "Secrets created"
else
    echo "Secrets already exist, skipping..."
fi

# Apply configmaps
echo "Applying configmaps..."
kubectl apply -f k8s/configmap.yaml

# Deploy database (PostgreSQL)
echo "Deploying PostgreSQL..."
kubectl apply -f k8s/postgres.yaml

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
kubectl wait --for=condition=ready pod -l app=postgres -n $NAMESPACE --timeout=${KUBECTL_TIMEOUT}s

# Deploy Redis
echo "Deploying Redis..."
kubectl apply -f k8s/redis.yaml

# Wait for Redis to be ready
echo "Waiting for Redis to be ready..."
kubectl wait --for=condition=ready pod -l app=redis -n $NAMESPACE --timeout=${KUBECTL_TIMEOUT}s

# Deploy backend
echo "Deploying backend..."
kubectl apply -f k8s/backend.yaml

# Wait for backend to be ready
echo "Waiting for backend to be ready..."
kubectl wait --for=condition=ready pod -l app=backend -n $NAMESPACE --timeout=${KUBECTL_TIMEOUT}s

# Deploy frontend
echo "Deploying frontend..."
kubectl apply -f k8s/frontend.yaml

# Wait for frontend to be ready
echo "Waiting for frontend to be ready..."
kubectl wait --for=condition=ready pod -l app=frontend -n $NAMESPACE --timeout=${KUBECTL_TIMEOUT}s

# Apply ingress
echo "Applying ingress..."
kubectl apply -f k8s/ingress.yaml

# Verify deployment
echo "Verifying deployment..."
kubectl get pods -n $NAMESPACE
kubectl get services -n $NAMESPACE
kubectl get ingress -n $NAMESPACE

# Health check
echo "Performing health check..."
sleep 30

if [[ "$ENVIRONMENT" == "staging" ]]; then
    HEALTH_URL="https://staging.mydoc.app/api/health"
else
    HEALTH_URL="https://mydoc.app/api/health"
fi

# Wait for health check to pass
for i in {1..10}; do
    if curl -f -s "$HEALTH_URL" > /dev/null 2>&1; then
        echo "Health check passed!"
        break
    else
        echo "Health check attempt $i/10 failed, retrying in 30 seconds..."
        sleep 30
    fi
    
    if [ $i -eq 10 ]; then
        echo "Health check failed after 10 attempts"
        exit 1
    fi
done

echo "Deployment to $ENVIRONMENT completed successfully!"

# Show deployment status
echo "Final deployment status:"
kubectl get all -n $NAMESPACE