# Kubernetes Sidecar Pattern

## Overview
The sidecar pattern is a fundamental Kubernetes design pattern where a secondary container (the "sidecar") runs alongside the main application container within the same Pod. Since containers in a Pod share the same network namespace, storage volumes, and lifecycle, sidecars can enhance or extend the functionality of the main container without modifying its code.

## Common Use Cases
- **Logging**: Collect and forward logs from the main container
- **Monitoring**: Gather metrics and send to monitoring systems
- **Service Mesh**: Handle network traffic (e.g., Envoy proxy in Istio)
- **Configuration Management**: Sync configuration files
- **Security**: Handle authentication, encryption, or certificate rotation

## Demo: Simple Pod with Sidecar Container

In this example, we'll deploy a pod with:
1. **Main Container**: Nginx web server writing access logs
2. **Sidecar Container**: A log processor that reads and displays the nginx logs

### Deploy the Sidecar Pod

```bash
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: sidecar-demo
  labels:
    app: sidecar-demo
spec:
  containers:
  # Main application container
  - name: nginx
    image: nginx:latest
    ports:
    - containerPort: 80
    volumeMounts:
    - name: shared-logs
      mountPath: /var/log/nginx
  
  # Sidecar container
  - name: log-processor
    image: busybox
    command: ['sh', '-c', 'tail -f /logs/access.log']
    volumeMounts:
    - name: shared-logs
      mountPath: /logs
  
  # Shared volume between containers
  volumes:
  - name: shared-logs
    emptyDir: {}
EOF
```

### Understanding the Configuration

**Shared Volume**: The `emptyDir` volume `shared-logs` is mounted in both containers:
- Nginx writes logs to `/var/log/nginx/access.log`
- Sidecar reads from `/logs/access.log` (same physical location)

**Container Independence**: Each container has its own:
- Process space and filesystem (except shared volumes)
- Resource limits and probes
- Image and lifecycle

**Network Sharing**: Both containers share:
- Same IP address (Pod IP)
- Same localhost network
- Port namespace (ports must be unique across containers)

### Verify the Deployment

```bash
# Check pod status - both containers should be running
kubectl get pod sidecar-demo

# You should see 2/2 in the READY column
```

### Test the Sidecar Pattern

#### 1. Generate Traffic to Nginx

```bash
# Get the Pod IP
POD_IP=$(kubectl get pod sidecar-demo -o jsonpath='{.status.podIP}')

# Generate some HTTP requests (from another pod or node)
kubectl run curl-test --image=curlimages/curl --rm -it --restart=Never -- curl http://$POD_IP

# Or generate multiple requests
for i in {1..5}; do
  kubectl run curl-test-$i --image=curlimages/curl --rm --restart=Never -- curl -s http://$POD_IP
done
```

#### 2. View Logs from the Main Container

```bash
# View nginx container logs
kubectl logs sidecar-demo -c nginx
```

#### 3. View Logs from the Sidecar Container

```bash
# View log-processor sidecar logs - you'll see the access logs being tailed
kubectl logs sidecar-demo -c log-processor

# Follow the logs in real-time
kubectl logs sidecar-demo -c log-processor -f
```

### Exec into Containers

You can exec into each container independently:

```bash
# Exec into the main nginx container
kubectl exec -it sidecar-demo -c nginx -- /bin/bash

# Exec into the sidecar container
kubectl exec -it sidecar-demo -c log-processor -- /bin/sh

# Check the shared volume from sidecar
kubectl exec sidecar-demo -c log-processor -- ls -la /logs
```

### Inspect Container Details

```bash
# Get detailed pod information
kubectl describe pod sidecar-demo

# Get pod YAML including container statuses
kubectl get pod sidecar-demo -o yaml
```

## Advanced Example: Nginx with Log Forwarder

Here's a more realistic example where the sidecar processes and formats logs:

```bash
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: nginx-log-forwarder
  labels:
    app: nginx-advanced
spec:
  containers:
  # Main application
  - name: nginx
    image: nginx:latest
    ports:
    - containerPort: 80
    volumeMounts:
    - name: logs
      mountPath: /var/log/nginx
    resources:
      requests:
        memory: "64Mi"
        cpu: "100m"
      limits:
        memory: "128Mi"
        cpu: "200m"
  
  # Sidecar log processor
  - name: log-forwarder
    image: busybox
    command:
    - sh
    - -c
    - |
      echo "Starting log forwarder..."
      while true; do
        if [ -f /logs/access.log ]; then
          tail -n 1 -f /logs/access.log | while read line; do
            echo "[PROCESSED] $(date -u +%Y-%m-%dT%H:%M:%S) - $line"
          done
        else
          echo "Waiting for access.log..."
          sleep 2
        fi
      done
    volumeMounts:
    - name: logs
      mountPath: /logs
      readOnly: true
    resources:
      requests:
        memory: "32Mi"
        cpu: "50m"
      limits:
        memory: "64Mi"
        cpu: "100m"
  
  volumes:
  - name: logs
    emptyDir: {}
EOF
```

### Test the Advanced Setup

```bash
# Check both containers are running
kubectl get pod nginx-log-forwarder

# Generate traffic
POD_IP=$(kubectl get pod nginx-log-forwarder -o jsonpath='{.status.podIP}')
kubectl run test-request --image=curlimages/curl --rm --restart=Never -- curl -s http://$POD_IP

# View the processed logs from sidecar
kubectl logs nginx-log-forwarder -c log-forwarder
```

## Init Containers vs Sidecar Containers

### Key Differences

| Aspect | Init Containers | Sidecar Containers |
|--------|----------------|-------------------|
| **Execution** | Run sequentially before main containers | Run concurrently with main containers |
| **Lifecycle** | Must complete successfully | Run throughout pod lifetime |
| **Purpose** | Initialization tasks | Continuous auxiliary services |
| **Failure** | Blocks pod from starting | Pod fails if sidecar crashes |

### Example with Both Init and Sidecar

```bash
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: init-and-sidecar
spec:
  # Init container runs first
  initContainers:
  - name: setup
    image: busybox
    command: ['sh', '-c', 'echo "Setup complete" > /config/init.txt']
    volumeMounts:
    - name: config
      mountPath: /config
  
  # Main and sidecar run together
  containers:
  - name: app
    image: nginx:latest
    volumeMounts:
    - name: config
      mountPath: /config
  
  - name: sidecar-monitor
    image: busybox
    command: ['sh', '-c', 'while true; do echo "Monitoring..."; sleep 10; done']
  
  volumes:
  - name: config
    emptyDir: {}
EOF
```

## Best Practices

1. **Resource Limits**: Always set resource requests and limits for sidecar containers
2. **Shared Volumes**: Use `emptyDir` for temporary shared data; use PersistentVolumes for persistent data
3. **Lifecycle Management**: Ensure sidecars handle graceful shutdown
4. **Security**: Run sidecars with minimal privileges; use `readOnly` mounts when possible
5. **Monitoring**: Monitor sidecar health separately from main container
6. **Version Control**: Pin sidecar image versions to avoid unexpected changes

## Cleanup

```bash
# Delete the demo pods
kubectl delete pod sidecar-demo
kubectl delete pod nginx-log-forwarder
kubectl delete pod init-and-sidecar
```

## Additional Resources

- [Kubernetes Multi-Container Pod Patterns](https://kubernetes.io/blog/2015/06/the-distributed-system-toolkit-patterns/)
- [Sidecar Container Documentation](https://kubernetes.io/docs/concepts/workloads/pods/sidecar-containers/)
- [Service Mesh (Istio/Linkerd) using Sidecar Pattern](https://istio.io/latest/docs/concepts/what-is-istio/)
