# ConfigMaps and Secrets: Quick Start Guide

## Overview

Kubernetes provides two main ways to manage application configuration:

- **ConfigMaps**: Non-sensitive configuration data (database hosts, feature flags, etc.)
- **Secrets**: Sensitive information (passwords, API keys, certificates)

Both are stored in the cluster and can be consumed by pods as environment variables or mounted files.

---

## ConfigMaps

### Creating ConfigMaps

#### From Command Line
```bash
# Create ConfigMap from literal values
kubectl create configmap app-config \
  --from-literal=database_host=postgres.example.com \
  --from-literal=database_port=5432 \
  --from-literal=app_env=development

# Create ConfigMap from file
echo "debug=true" > app.properties
echo "max_connections=100" >> app.properties
kubectl create configmap app-properties --from-file=app.properties

# View ConfigMaps
kubectl get configmaps
kubectl describe configmap app-config
```

#### From YAML
```yaml
# configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  database_host: "postgres.example.com"
  database_port: "5432"
  app_env: "development"
  app.properties: |
    debug=true
    max_connections=100
    timeout=30
```

```bash
# Apply ConfigMap
kubectl apply -f configmap.yaml
```

### Using ConfigMaps in Pods

#### As Environment Variables
```yaml
# pod-with-configmap.yaml
apiVersion: v1
kind: Pod
metadata:
  name: app-pod
spec:
  containers:
  - name: app
    image: busybox:1.35
    command: ['sh', '-c', 'env | grep DATABASE && sleep 3600']
    env:
    # Single environment variable
    - name: DATABASE_HOST
      valueFrom:
        configMapKeyRef:
          name: app-config
          key: database_host
    # All ConfigMap keys as environment variables
    envFrom:
    - configMapRef:
        name: app-config
  restartPolicy: Never
```

#### As Volume Mounts
```yaml
# pod-with-configmap-volume.yaml
apiVersion: v1
kind: Pod
metadata:
  name: app-pod-volume
spec:
  containers:
  - name: app
    image: busybox:1.35
    command: ['sh', '-c', 'ls /etc/config && cat /etc/config/app.properties && sleep 3600']
    volumeMounts:
    - name: config-volume
      mountPath: /etc/config
  volumes:
  - name: config-volume
    configMap:
      name: app-config
  restartPolicy: Never
```

### Test ConfigMaps
```bash
# Deploy and test environment variables
kubectl apply -f pod-with-configmap.yaml
kubectl logs app-pod

# Deploy and test volume mounts
kubectl apply -f pod-with-configmap-volume.yaml
kubectl logs app-pod-volume

# Clean up
kubectl delete pod app-pod app-pod-volume
```

---

## Secrets

### Creating Secrets

#### From Command Line
```bash
# Create Secret from literal values
kubectl create secret generic app-secrets \
  --from-literal=database_password=secretpassword \
  --from-literal=api_key=abc123xyz789

# Create Secret from files
echo -n 'admin' > username.txt
echo -n 'secretpassword' > password.txt
kubectl create secret generic user-secrets --from-file=username.txt --from-file=password.txt

# View Secrets (data is hidden)
kubectl get secrets
kubectl describe secret app-secrets
```

#### From YAML
```yaml
# secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
type: Opaque
data:
  # Values must be base64 encoded
  database_password: c2VjcmV0cGFzc3dvcmQ=  # "secretpassword"
  api_key: YWJjMTIzeHl6Nzg5  # "abc123xyz789"

---
# Alternative: using stringData (automatically base64 encoded)
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets-stringdata
type: Opaque
stringData:
  database_password: secretpassword
  api_key: abc123xyz789
```

```bash
# Encode values for YAML secrets
echo -n 'secretpassword' | base64
echo -n 'abc123xyz789' | base64

# Apply Secret
kubectl apply -f secret.yaml
```

### Using Secrets in Pods

#### As Environment Variables
```yaml
# pod-with-secrets.yaml
apiVersion: v1
kind: Pod
metadata:
  name: app-pod-secrets
spec:
  containers:
  - name: app
    image: busybox:1.35
    command: ['sh', '-c', 'echo "Password: $DATABASE_PASSWORD" && sleep 3600']
    env:
    # Single environment variable from Secret
    - name: DATABASE_PASSWORD
      valueFrom:
        secretKeyRef:
          name: app-secrets
          key: database_password
    # All Secret keys as environment variables
    envFrom:
    - secretRef:
        name: app-secrets
  restartPolicy: Never
```

#### As Volume Mounts (Recommended for Secrets)
```yaml
# pod-with-secrets-volume.yaml
apiVersion: v1
kind: Pod
metadata:
  name: app-pod-secrets-volume
spec:
  containers:
  - name: app
    image: busybox:1.35
    command: ['sh', '-c', 'ls /etc/secrets && cat /etc/secrets/database_password && sleep 3600']
    volumeMounts:
    - name: secrets-volume
      mountPath: /etc/secrets
      readOnly: true
  volumes:
  - name: secrets-volume
    secret:
      secretName: app-secrets
      defaultMode: 0400  # Read-only permissions
  restartPolicy: Never
```

### Test Secrets
```bash
# Deploy and test environment variables
kubectl apply -f pod-with-secrets.yaml
kubectl logs app-pod-secrets

# Deploy and test volume mounts
kubectl apply -f pod-with-secrets-volume.yaml
kubectl logs app-pod-secrets-volume

# View secret data (decode base64)
kubectl get secret app-secrets -o jsonpath='{.data.database_password}' | base64 -d

# Clean up
kubectl delete pod app-pod-secrets app-pod-secrets-volume
```

---

## Complete Example: Web App with Database

### Create Configuration and Secrets
```bash
# Create ConfigMap for application configuration
kubectl create configmap webapp-config \
  --from-literal=database_host=postgres-service \
  --from-literal=database_port=5432 \
  --from-literal=database_name=webapp \
  --from-literal=log_level=INFO

# Create Secret for sensitive data
kubectl create secret generic webapp-secrets \
  --from-literal=database_username=webapp_user \
  --from-literal=database_password=supersecretpassword \
  --from-literal=jwt_secret=myjwtsecretkey123
```

### Deploy Application
```yaml
# webapp-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: webapp
spec:
  replicas: 2
  selector:
    matchLabels:
      app: webapp
  template:
    metadata:
      labels:
        app: webapp
    spec:
      containers:
      - name: webapp
        image: nginx:1.21
        ports:
        - containerPort: 80
        env:
        # Configuration from ConfigMap
        - name: DATABASE_HOST
          valueFrom:
            configMapKeyRef:
              name: webapp-config
              key: database_host
        - name: DATABASE_PORT
          valueFrom:
            configMapKeyRef:
              name: webapp-config
              key: database_port
        - name: LOG_LEVEL
          valueFrom:
            configMapKeyRef:
              name: webapp-config
              key: log_level
        # Secrets as environment variables
        - name: DATABASE_USERNAME
          valueFrom:
            secretKeyRef:
              name: webapp-secrets
              key: database_username
        - name: DATABASE_PASSWORD
          valueFrom:
            secretKeyRef:
              name: webapp-secrets
              key: database_password
        # Mount JWT secret as file (more secure)
        volumeMounts:
        - name: jwt-secret
          mountPath: /etc/jwt
          readOnly: true
      volumes:
      - name: jwt-secret
        secret:
          secretName: webapp-secrets
          items:
          - key: jwt_secret
            path: jwt_secret
```

### Deploy and Test
```bash
# Deploy the application
kubectl apply -f webapp-deployment.yaml

# Check deployment
kubectl get deployments
kubectl get pods -l app=webapp

# Test configuration
kubectl exec -it deployment/webapp -- env | grep DATABASE
kubectl exec -it deployment/webapp -- ls /etc/jwt
kubectl exec -it deployment/webapp -- cat /etc/jwt/jwt_secret

# Clean up
kubectl delete deployment webapp
```

---

## Key Operations

### ConfigMap Operations
```bash
# List ConfigMaps
kubectl get configmaps

# View ConfigMap details
kubectl describe configmap app-config
kubectl get configmap app-config -o yaml

# Edit ConfigMap
kubectl edit configmap app-config

# Delete ConfigMap
kubectl delete configmap app-config
```

### Secret Operations
```bash
# List Secrets
kubectl get secrets

# View Secret details (data hidden)
kubectl describe secret app-secrets

# View Secret data (base64 encoded)
kubectl get secret app-secrets -o yaml

# Decode Secret value
kubectl get secret app-secrets -o jsonpath='{.data.database_password}' | base64 -d

# Edit Secret
kubectl edit secret app-secrets

# Delete Secret
kubectl delete secret app-secrets
```

---

## Best Practices

### ConfigMaps
- ✅ Use for non-sensitive configuration data
- ✅ Organize by namespace and environment
- ✅ Use labels for better organization
- ⚠️ Remember: 1MB size limit per ConfigMap

### Secrets
- ✅ Use volume mounts instead of environment variables when possible
- ✅ Set proper file permissions (0400 or 0600)
- ✅ Never store secrets in Git repositories
- ✅ Use external secret management for production (Azure Key Vault, etc.)
- ⚠️ Base64 encoding is NOT encryption

### General
- ✅ Use namespaces to isolate configurations
- ✅ Implement proper RBAC for access control
- ✅ Consider using external configuration stores for production
- ✅ Restart deployments when updating environment variables

---

## Troubleshooting

### Common Issues
```bash
# ConfigMap/Secret not found
kubectl get configmap,secret -n <namespace>

# Pod not picking up new configuration
# Environment variables require pod restart
kubectl rollout restart deployment/myapp

# Volume mounts update automatically (with delay)
kubectl exec -it <pod> -- cat /etc/config/myfile

# Check pod events for mount issues
kubectl describe pod <pod-name>

# Debug environment variables
kubectl exec -it <pod> -- env | grep <VARIABLE>
```

### Validation
```bash
# Verify ConfigMap creation
kubectl get configmap app-config -o jsonpath='{.data}' | jq

# Verify Secret creation (decode values)
kubectl get secret app-secrets -o jsonpath='{.data.database_password}' | base64 -d

# Check if pods are using configuration
kubectl describe pod <pod-name> | grep -A 10 "Environment"
kubectl describe pod <pod-name> | grep -A 10 "Mounts"
```

---

## Cleanup

```bash
# Clean up all demo resources
kubectl delete configmap app-config app-properties webapp-config 2>/dev/null || true
kubectl delete secret app-secrets app-secrets-stringdata user-secrets webapp-secrets 2>/dev/null || true
kubectl delete deployment webapp 2>/dev/null || true

# Clean up files
rm -f app.properties username.txt password.txt
rm -f configmap.yaml secret.yaml pod-with-*.yaml webapp-deployment.yaml

echo "Cleanup completed!"
```

---

## Summary

- **ConfigMaps** store non-sensitive configuration data
- **Secrets** store sensitive information (base64 encoded, not encrypted)
- Both can be consumed as **environment variables** or **volume mounts**
- **Volume mounts** are preferred for secrets (more secure)
- **External secret management** recommended for production environments
- Configuration changes in environment variables require **pod restart**
- Volume-mounted files **update automatically** (with some delay)

For production use cases with centralized configuration management, see the comprehensive guide: [ConfigMaps and Secrets Deep Dive](./cmsecretdeepdive.md)
