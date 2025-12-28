# Deployment Guide

This document provides comprehensive instructions for deploying the My Dr application using the CI/CD pipeline and infrastructure as code.

## Overview

The deployment system supports:
- **Automated CI/CD pipeline** with GitHub Actions
- **Blue-green deployment strategy** for zero-downtime deployments
- **Multi-environment support** (staging, production)
- **Docker containerization** with optimized images
- **Kubernetes orchestration** for scalability
- **Automated testing** (unit, integration, E2E)
- **Rollback capabilities** for quick recovery

## Prerequisites

### Required Tools
- Docker and Docker Compose
- kubectl (for Kubernetes deployments)
- Node.js 18+ and npm
- Python 3.11+
- Git

### Required Accounts/Services
- GitHub repository with Actions enabled
- Container registry (GitHub Container Registry)
- Kubernetes cluster (staging and production)
- Domain names and SSL certificates

## Environment Setup

### 1. Environment Variables

Copy and customize environment files:
```bash
cp .env.staging.example .env.staging
cp .env.production.example .env.production
```

Update the following critical values:
- Database passwords
- JWT secrets
- Firebase configuration
- API keys for AI services
- Monitoring/logging endpoints

### 2. Secrets Configuration

For Kubernetes deployments, update the base64-encoded secrets in `k8s/secrets.yaml`:
```bash
echo -n "your_password" | base64
```

### 3. GitHub Secrets

Configure the following secrets in your GitHub repository:
- `GITHUB_TOKEN` (automatically provided)
- `STAGING_KUBECONFIG` (base64-encoded kubeconfig for staging)
- `PRODUCTION_KUBECONFIG` (base64-encoded kubeconfig for production)

## Deployment Methods

### Method 1: Docker Compose (Development/Testing)

```bash
# Development environment
docker-compose up -d

# Staging environment
docker-compose -f docker-compose.yml -f docker-compose.staging.yml up -d

# Production environment
docker-compose -f docker-compose.yml -f docker-compose.production.yml up -d
```

### Method 2: Kubernetes (Recommended for Production)

```bash
# Deploy to staging
./scripts/k8s-deploy.sh staging

# Deploy to production
./scripts/k8s-deploy.sh production
```

### Method 3: Blue-Green Deployment

```bash
# Blue-green deployment to staging
./scripts/deploy.sh staging

# Blue-green deployment to production
./scripts/deploy.sh production
```

## CI/CD Pipeline

### Automated Workflow

The GitHub Actions pipeline automatically:

1. **On Pull Request:**
   - Runs unit tests
   - Runs integration tests
   - Performs security scanning
   - Builds Docker images (without pushing)

2. **On Push to `develop` branch:**
   - Runs all tests
   - Builds and pushes Docker images
   - Deploys to staging environment
   - Runs E2E tests against staging

3. **On Push to `main` branch:**
   - Runs all tests
   - Builds and pushes Docker images
   - Deploys to production using blue-green strategy
   - Runs E2E tests against production

### Manual Deployment

To trigger manual deployment:

```bash
# Trigger staging deployment
git push origin develop

# Trigger production deployment
git push origin main
```

## Testing

### Running Tests Locally

```bash
# Backend tests
cd backend
pytest --cov=. --cov-report=html

# Frontend tests
cd frontend
npm test -- --run --coverage

# E2E tests (requires running application)
cd frontend
npx playwright test
```

### Test Coverage Requirements

- **Unit tests:** Minimum 80% coverage
- **Integration tests:** All API endpoints
- **E2E tests:** Critical user journeys

## Monitoring and Logging

### Health Checks

All services include health check endpoints:
- Backend: `GET /health`
- Frontend: `GET /health`
- Database: Built-in PostgreSQL health checks
- Redis: Built-in Redis health checks

### Monitoring Stack

The application includes:
- **Application monitoring** with custom metrics
- **Error tracking** with structured logging
- **Performance monitoring** with response time tracking
- **Database monitoring** with query performance metrics

### Log Aggregation

Logs are structured in JSON format and include:
- Request/response logging
- Error tracking with stack traces
- Performance metrics
- Security audit logs

## Rollback Procedures

### Automatic Rollback

The deployment system automatically rolls back if:
- Health checks fail after deployment
- Critical errors are detected
- Performance degradation occurs

### Manual Rollback

```bash
# Docker Compose rollback
./scripts/rollback.sh staging

# Kubernetes rollback
./scripts/k8s-rollback.sh production
```

### Rollback Verification

After rollback:
1. Verify health checks pass
2. Check application functionality
3. Monitor error rates and performance
4. Validate data integrity

## Security Considerations

### Container Security
- Non-root user execution
- Minimal base images
- Regular security scanning
- Secrets management

### Network Security
- TLS encryption for all communications
- Network policies in Kubernetes
- Rate limiting and DDoS protection
- CORS configuration

### Data Security
- Encrypted data at rest
- Secure database connections
- Regular security audits
- Compliance with healthcare data regulations

## Troubleshooting

### Common Issues

1. **Health Check Failures**
   ```bash
   # Check service logs
   kubectl logs -l app=backend -n mydoc-staging
   
   # Check service status
   kubectl get pods -n mydoc-staging
   ```

2. **Database Connection Issues**
   ```bash
   # Check database connectivity
   kubectl exec -it postgres-0 -n mydoc-staging -- psql -U mydoc_user -d mydoc_staging
   ```

3. **Image Pull Errors**
   ```bash
   # Check image registry authentication
   kubectl get secret -n mydoc-staging
   ```

### Performance Issues

1. **High Response Times**
   - Check database query performance
   - Monitor AI service response times
   - Verify resource limits and requests

2. **Memory/CPU Issues**
   - Scale deployments horizontally
   - Adjust resource limits
   - Optimize application code

### Recovery Procedures

1. **Complete System Failure**
   - Restore from database backups
   - Redeploy from known good images
   - Verify data integrity

2. **Partial Service Failure**
   - Restart affected services
   - Check service dependencies
   - Monitor for cascading failures

## Maintenance

### Regular Tasks

1. **Weekly:**
   - Review monitoring dashboards
   - Check security scan results
   - Update dependencies

2. **Monthly:**
   - Database maintenance and optimization
   - Log rotation and cleanup
   - Performance review and optimization

3. **Quarterly:**
   - Security audit and penetration testing
   - Disaster recovery testing
   - Infrastructure cost optimization

### Backup and Recovery

1. **Database Backups:**
   - Automated daily backups
   - Point-in-time recovery capability
   - Cross-region backup replication

2. **Application Backups:**
   - Container image versioning
   - Configuration backup
   - Secrets backup (encrypted)

## Support and Escalation

### Monitoring Alerts

Critical alerts trigger immediate notifications:
- Service downtime
- High error rates
- Performance degradation
- Security incidents

### Escalation Procedures

1. **Level 1:** Automated recovery attempts
2. **Level 2:** On-call engineer notification
3. **Level 3:** Senior engineer and management notification
4. **Level 4:** External vendor support engagement

For additional support, refer to the monitoring dashboards and log aggregation systems for detailed troubleshooting information.