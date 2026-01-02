# Kubernetes Services - Connecting to Your Applications

This guide explains the concept of Kubernetes Services, how they relate to pods, and the critical role of labels and selectors in service discovery and networking.

## 📖 What is a Kubernetes Service?

A **Service** in Kubernetes is an abstraction that defines a logical set of pods and provides a stable way to access them. Services solve a fundamental problem: pods are ephemeral and can be created, destroyed, or rescheduled at any time, but applications need a reliable way to communicate with each other.

### Key Problems Services Solve:
- **Pod IP addresses change**: When pods restart, they get new IP addresses
- **Pod discovery**: How do you find which pods are running your application?
- **Load balancing**: How do you distribute traffic across multiple pod replicas?
- **Service abstraction**: Applications shouldn't need to know about individual pod locations

## 🔗 How Services Relate to Pods

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Service to Pod Relationship                          │
└─────────────────────────────────────────────────────────────────────────────┘

Service (ClusterIP: 10.96.1.100:80)
┌─────────────────────────────────────────────────────────────────────────────┐
│  Service Name: web-service                                                  │
│  Selector: app=nginx                                                        │
│  Port: 80 → Target Port: 8080                                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐
│ Pod 1               │  │ Pod 2               │  │ Pod 3               │
│ IP: 192.168.1.10    │  │ IP: 192.168.1.11    │  │ IP: 192.168.1.12    │
│ Labels:             │  │ Labels:             │  │ Labels:             │
│   app=nginx         │  │   app=nginx         │  │   app=nginx         │
│   version=v1        │  │   version=v1        │  │   version=v2        │
│ Port: 8080          │  │ Port: 8080          │  │ Port: 8080          │
└─────────────────────┘  └─────────────────────┘  └─────────────────────┘

Traffic Flow:
1. Client sends request to Service (web-service:80)
2. Service load balances to one of the matching pods
3. Request reaches pod on port 8080
4. Pod processes request and responds back through service
```

## 🏷️ Labels and Selectors - The Magic Connection

**Labels** and **selectors** are the mechanism that connects services to pods. This is one of the most important concepts in Kubernetes.

### Labels
- **Key-value pairs** attached to Kubernetes objects (pods, services, deployments)
- Used to organize and select subsets of objects
- Completely flexible - you define what makes sense for your application

### Selectors
- **Queries** that match objects based on their labels
- Services use selectors to determine which pods to route traffic to
- If a pod's labels match a service's selector, it becomes an endpoint

### Example Label Strategy:
```yaml
# Good labeling strategy
labels:
  app: nginx           # Application name
  tier: frontend       # Application tier
  version: v1.2.0      # Version for deployments
  environment: prod    # Environment designation
```

## 🚀 Hands-On Example: Creating Deployment and Service

Let's create a practical example with an nginx deployment and a ClusterIP service.

### Step 1: Create the Deployment

Create a file called `nginx-deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
  labels:
    app: nginx
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
        tier: frontend
    spec:
      containers:
      - name: nginx
        image: nginx:1.20
        ports:
        - containerPort: 80
        resources:
          requests:
            memory: "64Mi"
            cpu: "50m"
          limits:
            memory: "128Mi"
            cpu: "100m"
```

**Apply the deployment:**
```bash
kubectl apply -f nginx-deployment.yaml
```

### Step 2: Create the ClusterIP Service

Create a file called `nginx-service.yaml`:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx-service
  labels:
    app: nginx
spec:
  type: ClusterIP
  selector:
    app: nginx
  ports:
    - protocol: TCP
      port: 80          # Service port (what clients connect to)
      targetPort: 80    # Pod port (where nginx is listening)
```

**Apply the service:**
```bash
kubectl apply -f nginx-service.yaml
```

### Step 3: Verify the Setup

```bash
# Check deployment
kubectl get deployments
kubectl get pods -l app=nginx

# Check service
kubectl get services
kubectl describe service nginx-service

# See the endpoints (pods the service routes to)
kubectl get endpoints nginx-service
```

## 🔍 Understanding the Connection

### Labels in Action
```bash
# View pod labels
kubectl get pods --show-labels

# Filter pods by label
kubectl get pods -l app=nginx
kubectl get pods -l app=nginx,tier=frontend

# Add a label to a running pod
kubectl label pod <pod-name> version=v1.0

# Remove a label
kubectl label pod <pod-name> version-
```

### Service Discovery
```bash
# See how the service selector matches pods
kubectl describe service nginx-service

# Check endpoints (should show your pod IPs)
kubectl get endpoints nginx-service -o yaml
```

## 🧪 Testing the Service

### From Inside the Cluster

**Method 1: Create a test pod**
```bash
# Create a temporary pod for testing
kubectl run test-pod --image=busybox --rm -it --restart=Never -- sh

# Inside the pod, test the service
wget -qO- nginx-service
# or
curl nginx-service
```

**Method 2: Use an existing pod**
```bash
# Execute into one of your nginx pods
kubectl exec -it <nginx-pod-name> -- bash

# Test the service from inside
curl nginx-service
```

### Service DNS Resolution
```bash
# Services are accessible by DNS name within the cluster
# Format: <service-name>.<namespace>.svc.cluster.local

# From test pod:
nslookup nginx-service
# Should resolve to the ClusterIP

# Full DNS name (if needed):
curl nginx-service.default.svc.cluster.local
```

## 📊 Service Types Overview

While we're focusing on ClusterIP, here's what each service type provides:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Service Types Comparison                          │
└─────────────────────────────────────────────────────────────────────────────┘

ClusterIP (Default)                    NodePort                    LoadBalancer
┌─────────────────────┐                ┌─────────────────────┐     ┌─────────────────────┐
│ • Internal only     │                │ • External access   │     │ • Cloud load        │
│ • Cluster DNS name  │                │ • High port number  │     │   balancer          │
│ • Most common       │                │ • All nodes         │     │ • Public IP         │
│ • Fast performance  │                │ • Port range:       │     │ • Production ready  │
│                     │                │   30000-32767       │     │                     │
└─────────────────────┘                └─────────────────────┘     └─────────────────────┘

Access: pod-to-pod                     Access: <NodeIP>:<NodePort>  Access: <LoadBalancer-IP>:80
Best for: Microservices               Best for: Development/Testing  Best for: Production external
```

## 🔧 Practical Exercises

### Exercise 1: Label Selector Experimentation
```bash
# Create pods with different labels
kubectl run pod1 --image=nginx --labels="app=nginx,env=prod"
kubectl run pod2 --image=nginx --labels="app=nginx,env=dev"
kubectl run pod3 --image=nginx --labels="app=apache,env=prod"

# Create a service that only targets prod environment
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Service
metadata:
  name: prod-service
spec:
  selector:
    env: prod
  ports:
  - port: 80
    targetPort: 80
EOF

# Check which pods the service targets
kubectl get endpoints prod-service
kubectl describe service prod-service
```

### Exercise 2: Service Without Matching Pods
```bash
# Create a service with a selector that matches no pods
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Service
metadata:
  name: orphan-service
spec:
  selector:
    app: nonexistent
  ports:
  - port: 80
EOF

# Observe - no endpoints created
kubectl get endpoints orphan-service
# Should show no endpoints
```

### Exercise 3: Multi-Port Service
```bash
# Create a service with multiple ports
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Service
metadata:
  name: multi-port-service
spec:
  selector:
    app: nginx
  ports:
  - name: http
    port: 80
    targetPort: 80
  - name: metrics
    port: 9090
    targetPort: 9090
EOF
```

### Exercise 4: Internal Load Balancer Service

Create a deployment and internal load balancer service that's only accessible within the Azure VNet:

```bash
# Create nginx deployment with 3 replicas
cat <<EOF | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-internal
  labels:
    app: nginx-internal
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nginx-internal
  template:
    metadata:
      labels:
        app: nginx-internal
        tier: frontend
    spec:
      containers:
      - name: nginx
        image: nginx:latest
        ports:
        - containerPort: 80
        resources:
          requests:
            memory: "64Mi"
            cpu: "250m"
          limits:
            memory: "128Mi"
            cpu: "500m"
EOF

# Create internal load balancer service
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Service
metadata:
  name: nginx-internal-lb
  annotations:
    service.beta.kubernetes.io/azure-load-balancer-internal: "true"
spec:
  type: LoadBalancer
  selector:
    app: nginx-internal
  ports:
  - port: 80
    targetPort: 80
    protocol: TCP
EOF

# Check the deployment and service
kubectl get deployments
kubectl get pods -l app=nginx-internal
kubectl get service nginx-internal-lb

# Wait for internal IP assignment (may take a few minutes)
kubectl get service nginx-internal-lb --watch

# Test connectivity from within the cluster
kubectl run test-pod --image=busybox --rm -it --restart=Never -- wget -qO- http://nginx-internal-lb

# Check service endpoints
kubectl get endpoints nginx-internal-lb

# Describe the service to see the internal load balancer details
kubectl describe service nginx-internal-lb
```

**Key Points about Internal Load Balancer:**
- Uses annotation `service.beta.kubernetes.io/azure-load-balancer-internal: "true"`
- Creates Azure Internal Load Balancer instead of public one
- Accessible only from within the Azure VNet
- Useful for internal services that shouldn't be exposed to internet
- Load balances traffic across all 3 nginx replicas

## 🛠️ Troubleshooting Common Issues

### Issue 1: Service Not Reaching Pods
```bash
# Check if selector matches pod labels
kubectl get pods --show-labels
kubectl describe service <service-name>

# Check endpoints
kubectl get endpoints <service-name>
# If no endpoints, selector doesn't match any pods
```

### Issue 2: Connection Refused
```bash
# Verify the target port
kubectl describe service <service-name>
kubectl describe pod <pod-name>

# Check if the port is actually listening in the pod
kubectl exec <pod-name> -- netstat -tlnp
```

### Issue 3: DNS Resolution Problems
```bash
# Test DNS from inside a pod
kubectl exec -it <pod-name> -- nslookup <service-name>

# Check kube-dns/coredns
kubectl get pods -n kube-system -l k8s-app=kube-dns
```

## 📋 Best Practices

### Labeling Strategy
```yaml
# Recommended labels
metadata:
  labels:
    app.kubernetes.io/name: nginx
    app.kubernetes.io/instance: nginx-prod
    app.kubernetes.io/version: "1.20"
    app.kubernetes.io/component: webserver
    app.kubernetes.io/part-of: ecommerce
    app.kubernetes.io/managed-by: helm
```

### Service Design
- **Use meaningful names**: `user-service`, `payment-api`, `frontend-web`
- **Consistent port naming**: Use names like `http`, `grpc`, `metrics`
- **Resource limits**: Always set resource requests and limits on pods
- **Health checks**: Implement readiness and liveness probes

### Monitoring Services
```bash
# Monitor service endpoints
kubectl get endpoints --watch

# Check service events
kubectl describe service <service-name>

# Monitor pod readiness
kubectl get pods -w
```



## Advanced 

Change nodename and apply sshrootpod.yaml

```bash 
k apply -f sshrootpod.yaml 

k exec nsenter-test -it -- bash  
iptables -t nat -S | grep -E "KUBE-"

iptables -t nat -S | grep 10.0.0.1

iptables -t nat -S KUBE-SVC-xxxxxx

iptables -t nat -S KUBE-SEP-xxxxxx  
``` 
outside of the shell, check IP for API server address -> nslookup democluste-democlusterrg-3eef5d-nqvdp4bm.hcp.eastus2.azmk8s.io   

DNAT IP should match nslookup IP    

similarly, check iptables chain for other K8S services.  Check after completing 'Exercise 1' (for creating service)     

## 🎯 Key Takeaways

1. **Services provide stable networking** for ephemeral pods
2. **Labels and selectors** create the connection between services and pods
3. **ClusterIP services** are perfect for internal communication
4. **DNS names** make services discoverable within the cluster
5. **Proper labeling** is crucial for service discovery and organization

## 🧹 Cleanup

```bash
# Remove all created resources
kubectl delete deployment nginx-deployment
kubectl delete service nginx-service
kubectl delete service prod-service
kubectl delete service orphan-service
kubectl delete service multi-port-service
kubectl delete pods pod1 pod2 pod3 --ignore-not-found=true
```

## 🔗 Related Concepts

- **[Deployments](./deploymentdemo.md)**: How to manage application replicas
- **[Pods](./pods.md)**: Understanding the basic unit of deployment
- **[kubectl Commands](./kubectl.md)**: Master the tools for service management

---

**Next Steps**: Once you're comfortable with ClusterIP services, explore NodePort and LoadBalancer services for external access patterns.
