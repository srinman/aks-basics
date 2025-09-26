# kubectl Basics for SMEs

This document provides comprehensive kubectl knowledge for Subject Matter Experts (SMEs) covering architecture, basic commands, and advanced techniques.

## Table of Contents
1. [kubectl Architecture Overview](#kubectl-architecture-overview)
2. [Role and Purpose of kubectl](#role-and-purpose-of-kubectl)
3. [Basic kubectl Commands](#basic-kubectl-commands)
4. [Advanced kubectl Techniques](#advanced-kubectl-techniques)
5. [kubectl Port-Forward and Networking](#kubectl-port-forward-and-networking)
6. [Troubleshooting with kubectl](#troubleshooting-with-kubectl)
7. [Best Practices](#best-practices)

## kubectl Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        kubectl Architecture                     │
└─────────────────────────────────────────────────────────────────┘

Client Side (Your Machine)                Server Side (Kubernetes Cluster)
┌──────────────────────────┐              ┌─────────────────────────────────┐
│                          │              │                                 │
│  ┌─────────────────────┐ │              │  ┌─────────────────────────────┐│
│  │     kubectl         │ │ HTTP/HTTPS   │  │        API Server           ││
│  │   (CLI Tool)        │─┼──────────────┼─▶│    (kube-apiserver)         ││
│  │                     │ │   REST API   │  │                             ││
│  └─────────────────────┘ │              │  └─────────────────────────────┘│
│                          │              │               │                 │
│  ┌─────────────────────┐ │              │               ▼                 │
│  │   ~/.kube/config    │ │              │  ┌─────────────────────────────┐│
│  │  (Authentication &  │ │              │  │         etcd                ││
│  │   Cluster Info)     │ │              │  │    (Cluster State)          ││
│  └─────────────────────┘ │              │  └─────────────────────────────┘│
│                          │              │                                 │
│  ┌─────────────────────┐ │              │  ┌─────────────────────────────┐│
│  │   Local Cache       │ │              │  │      Controller Manager     ││
│  │  (Resource Types,   │ │              │  │       & Scheduler           ││
│  │   API Versions)     │ │              │  └─────────────────────────────┘│
│  └─────────────────────┘ │              │                                 │
└──────────────────────────┘              └─────────────────────────────────┘

Communication Flow:
1. kubectl reads configuration from ~/.kube/config
2. Authenticates with API Server using certificates/tokens
3. Sends HTTP requests to Kubernetes API Server
4. API Server validates, processes, and stores in etcd
5. Controllers and Scheduler act on the stored state
```

## Role and Purpose of kubectl

### Primary Functions:
1. **Command-Line Interface**: Primary tool for interacting with Kubernetes clusters
2. **API Client**: Translates human-readable commands into Kubernetes API calls
3. **Resource Management**: Create, read, update, delete (CRUD) Kubernetes resources
4. **Cluster Administration**: Manage cluster-wide settings and operations
5. **Debugging Tool**: Inspect cluster state, logs, and troubleshoot issues

### What kubectl Communicates With:
- **Kubernetes API Server**: Primary communication endpoint
- **Authentication Systems**: Uses certificates, tokens, or cloud provider auth
- **Local Configuration**: Reads ~/.kube/config for cluster and context information
- **Remote Resources**: Interacts with pods, services, deployments, etc.

## Basic kubectl Commands

### Cluster and Context Management
```bash
# View cluster information
kubectl cluster-info

# Get current context
kubectl config current-context

# List all contexts
kubectl config get-contexts

# Switch context
kubectl config use-context <context-name>

# View cluster configuration
kubectl config view
```

### Resource Discovery and Basic Operations
```bash
# List API resources - shows all available Kubernetes resource types
kubectl api-resources

# Get API versions - shows all available API groups and their versions
kubectl api-versions

# Explain resource structure
kubectl explain pod
kubectl explain deployment.spec

# Get resources with different output formats
kubectl get pods -o wide
kubectl get pods -o yaml
kubectl get pods -o json
kubectl get pods -A -o jsonpath='{.items[*].metadata.name}'
```

#### Understanding API Resources and Versions

**What `kubectl api-resources` shows:**
```bash
# Example output:
NAME                     SHORTNAMES   APIVERSION                    NAMESPACED   KIND
pods                     po           v1                            true         Pod
services                 svc          v1                            true         Service
deployments              deploy       apps/v1                       true         Deployment
configmaps               cm           v1                            true         ConfigMap
secrets                               v1                            true         Secret
nodes                    no           v1                            false        Node
namespaces               ns           v1                            false        Namespace
```

**Column explanations:**
- **NAME**: Resource type name (what you use in kubectl commands)
- **SHORTNAMES**: Abbreviated names (e.g., `po` for pods, `svc` for services)
- **APIVERSION**: Which API group/version this resource belongs to
- **NAMESPACED**: Whether the resource exists within a namespace (true) or cluster-wide (false)
- **KIND**: The resource type name used in YAML manifests

**Practical uses of `api-resources`:**
```bash
# Find short names for faster typing
kubectl api-resources | grep deployment
# Output: deployments    deploy    apps/v1    true    Deployment
# Now you can use: kubectl get deploy instead of kubectl get deployments

# Check if a resource is namespaced
kubectl api-resources | grep nodes
# Output: nodes    no    v1    false    Node
# Shows nodes are cluster-wide, not namespaced

# Find all resources in a specific API group
kubectl api-resources 
kubectl api-resources --api-group=apps
kubectl api-resources --api-group=networking.k8s.io
```

**What `kubectl api-versions` shows:**
```bash
# Example output:
admissionregistration.k8s.io/v1
admissionregistration.k8s.io/v1beta1
apiextensions.k8s.io/v1
apiregistration.k8s.io/v1
apps/v1
authentication.k8s.io/v1
authorization.k8s.io/v1
autoscaling/v1
autoscaling/v2
batch/v1
certificates.k8s.io/v1
coordination.k8s.io/v1
v1
```

**API Version format explanation:**
- **Core API (v1)**: Basic resources like pods, services, configmaps
- **Named groups (apps/v1)**: Organized resource groups like deployments, daemonsets
- **Extended APIs**: Third-party or specialized resources (e.g., networking.k8s.io/v1)

**Practical uses of `api-versions`:**
```bash
# Check available versions for specific API group
kubectl api-versions | grep apps
# Output: apps/v1

# Verify API compatibility when writing YAML manifests
# If you see 'apps/v1' is available, you can use:
# apiVersion: apps/v1
# kind: Deployment

# Check for beta vs stable APIs
kubectl api-versions | grep autoscaling
# Output: autoscaling/v1, autoscaling/v2
# v1 = stable, v2 = newer features
```

**Why this matters:**
- **Writing YAML**: You need the correct `apiVersion` field in your manifests
- **Compatibility**: Different Kubernetes versions support different API versions
- **Feature access**: Newer API versions may have additional features
- **Efficiency**: Short names make commands faster to type
- **Troubleshooting**: Understanding namespaced vs cluster resources helps with permissions and scope

### Core Resource Management
```bash
# Pods
kubectl get pods
kubectl get pods -n <namespace>
kubectl get pods --all-namespaces
kubectl describe pod <pod-name>
kubectl delete pod <pod-name>

# Deployments
kubectl get deployments
kubectl create deployment nginx --image=nginx
kubectl scale deployment nginx --replicas=3
kubectl rollout status deployment/nginx
kubectl rollout history deployment/nginx

# Services
kubectl get services
kubectl expose deployment nginx --port=80 --type=ClusterIP
kubectl describe service nginx

# Namespaces
kubectl get namespaces
kubectl create namespace dev
kubectl delete namespace dev
```

### Imperative vs Declarative Commands
```bash
# Imperative (direct commands)
kubectl create deployment web --image=nginx
kubectl expose deployment web --port=80
kubectl scale deployment web --replicas=5

# Declarative (using YAML files)
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
kubectl apply -k ./manifests/

# Generate YAML without applying
kubectl create deployment web --image=nginx --dry-run=client -o yaml
kubectl run test-pod --image=busybox --dry-run=client -o yaml
```

## Advanced kubectl Techniques

### Resource Selection and Filtering
```bash
# Label selectors
kubectl get pods -l app=nginx
kubectl get pods -l 'environment in (production, staging)'
kubectl get pods -l app=nginx,version!=v1

# Field selectors
kubectl get pods --field-selector status.phase=Running
kubectl get pods --field-selector metadata.namespace=kube-system

# Combining selectors
kubectl get pods -l app=nginx --field-selector status.phase=Running
```

### Advanced Output and Formatting
```bash
# Custom columns
kubectl get pods -o custom-columns=NAME:.metadata.name,STATUS:.status.phase,NODE:.spec.nodeName

# JSONPath queries
kubectl get pods -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.status.phase}{"\n"}{end}'

# Sort by creation time
kubectl get pods --sort-by=.metadata.creationTimestamp

# Watch for changes
kubectl get pods --watch
kubectl get pods --watch-only
```

### Resource Patching and Editing
```bash
# Strategic merge patch
kubectl patch deployment nginx -p '{"spec":{"replicas":5}}'

# JSON patch
kubectl patch pod nginx --type='json' -p='[{"op": "replace", "path": "/spec/containers/0/image", "value":"nginx:1.20"}]'

# Edit resources directly
kubectl edit deployment nginx
kubectl edit configmap my-config

# Replace resources
kubectl replace -f updated-deployment.yaml
```

## kubectl Port-Forward and Networking

### Port-Forward Capabilities
Port-forward creates a secure tunnel between your local machine and a pod/service in the cluster.

```bash
# Forward to a specific pod
kubectl port-forward pod/nginx-pod 8080:80

# Forward to a deployment (targets one pod)
kubectl port-forward deployment/nginx 8080:80

# Forward to a service
kubectl port-forward service/nginx 8080:80

# Forward to specific address (not just localhost)
kubectl port-forward --address 0.0.0.0 pod/nginx-pod 8080:80

# Multiple port forwards
kubectl port-forward pod/nginx-pod 8080:80 8443:443

# Background port-forward
kubectl port-forward pod/nginx-pod 8080:80 &
```

### Advanced Networking Commands
```bash
# Execute commands in pods
kubectl exec -it nginx-pod -- bash
kubectl exec nginx-pod -- ls /etc

# Execute in specific container (multi-container pods)
kubectl exec -it nginx-pod -c sidecar-container -- bash

# Copy files to/from pods
kubectl cp /local/file nginx-pod:/remote/path
kubectl cp nginx-pod:/remote/file /local/path
kubectl cp nginx-pod:/remote/file /local/path -c container-name

# Network debugging
kubectl run network-test --image=busybox --rm -it -- sh
kubectl run curl-test --image=curlimages/curl --rm -it -- sh
```

### Proxy and Direct API Access
```bash
# Start kubectl proxy (secure access to API server)
kubectl proxy --port=8080

# Access API directly through proxy
curl http://localhost:8080/api/v1/pods
curl http://localhost:8080/api/v1/namespaces/default/pods

# Raw API access (with authentication)
kubectl get --raw /api/v1/nodes
kubectl get --raw /metrics
kubectl get --raw /api/v1/namespaces/kube-system/pods
```

## Troubleshooting with kubectl

### Log Analysis
```bash
# View pod logs
kubectl logs nginx-pod

# Follow logs (real-time)
kubectl logs -f nginx-pod

# Previous container logs (after restart)
kubectl logs nginx-pod --previous

# Multi-container pod logs
kubectl logs nginx-pod -c sidecar-container

# Logs with timestamps
kubectl logs nginx-pod --timestamps

# Tail logs (last N lines)
kubectl logs nginx-pod --tail=50

# Logs from multiple pods
kubectl logs -l app=nginx --tail=10
```

### Event Monitoring
```bash
# Get events in current namespace
kubectl get events

# Get events sorted by time
kubectl get events --sort-by='.metadata.creationTimestamp'

# Watch events in real-time
kubectl get events --watch

# Events for specific resource
kubectl describe pod nginx-pod  # includes events
kubectl get events --field-selector involvedObject.name=nginx-pod
```

### Resource Usage and Performance
```bash
# Node resource usage
kubectl top nodes

# Pod resource usage
kubectl top pods
kubectl top pods --containers

# Resource usage by namespace
kubectl top pods -n kube-system

# Describe resource limits and requests
kubectl describe pod nginx-pod | grep -A5 -B5 "Limits\|Requests"
```

### Debug Running Pods
```bash
# Create debug container in existing pod (Kubernetes 1.23+)
kubectl debug nginx-pod -it --image=busybox --target=nginx

# Create debug copy of pod
kubectl debug nginx-pod -it --image=busybox --copy-to=nginx-debug

# Debug nodes
kubectl debug node/node-name -it --image=busybox
```

## Best Practices

### Configuration Management
```bash
# Use specific namespace
kubectl config set-context --current --namespace=production

# Use resource quotas
kubectl describe resourcequota -n development

# Validate YAML before applying
kubectl apply --dry-run=client -f deployment.yaml
kubectl apply --dry-run=server -f deployment.yaml

# Use kustomize for environment-specific configs
kubectl apply -k overlays/production/
```

### Security Considerations
```bash
# Check permissions
kubectl auth can-i create pods
kubectl auth can-i create pods --as=system:serviceaccount:default:default

# View service account permissions
kubectl describe clusterrolebinding
kubectl get rolebinding -A

# Use least privilege contexts
kubectl config use-context limited-user-context
```

### Efficiency Tips
```bash
# Use aliases
alias k=kubectl
alias kgp='kubectl get pods'
alias kgs='kubectl get services'

# Tab completion (add to ~/.bashrc or ~/.zshrc)
source <(kubectl completion bash)  # for bash
source <(kubectl completion zsh)   # for zsh

# Use short names
kubectl get po    # instead of kubectl get pods
kubectl get svc   # instead of kubectl get services
kubectl get deploy # instead of kubectl get deployments

# Batch operations
kubectl delete pods pod1 pod2 pod3
kubectl get pods,services,deployments
```

### Monitoring and Observability
```bash
# Continuous monitoring
watch kubectl get pods
watch kubectl top nodes

# Resource changes
kubectl get pods --watch-only

# Diff before applying changes
kubectl diff -f updated-deployment.yaml

# Rollback capabilities
kubectl rollout undo deployment/nginx
kubectl rollout undo deployment/nginx --to-revision=2
```

## Summary

kubectl is the Swiss Army knife of Kubernetes operations. It serves as:
- **API Gateway**: Translates commands to REST API calls
- **Configuration Manager**: Handles authentication and cluster contexts  
- **Development Tool**: Enables port-forwarding, exec, and file copying
- **Operations Tool**: Provides logging, monitoring, and debugging capabilities
- **Administration Interface**: Manages resources, permissions, and cluster state

Understanding kubectl's architecture and capabilities is essential for effective Kubernetes operations, from basic resource management to complex troubleshooting scenarios.

---

# Appendix: Advanced Architecture Diagrams

*The following section contains detailed technical architecture diagrams for advanced users and SMEs who want to understand the underlying networking mechanisms of kubectl port-forward and proxy functionality.*

## A.1 kubectl Port-Forward Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          kubectl port-forward Architecture                     │
└─────────────────────────────────────────────────────────────────────────────────┘

Local Machine                    Kubernetes Cluster                    Target Pod
┌──────────────────────┐        ┌─────────────────────────────────┐   ┌─────────────┐
│                      │        │                                 │   │             │
│  ┌─────────────────┐ │        │  ┌─────────────────────────────┐│   │ ┌─────────┐ │
│  │  Application    │ │        │  │        API Server           ││   │ │  nginx  │ │
│  │ (Browser/curl)  │ │        │  │    (kube-apiserver)         ││   │ │ Port:80 │ │
│  └─────────────────┘ │        │  └─────────────────────────────┘│   │ └─────────┘ │
│           │           │        │               │                 │   │      ▲      │
│           ▼           │        │               │                 │   │      │      │
│  ┌─────────────────┐ │        │               ▼                 │   │      │      │
│  │    kubectl      │ │ HTTPS  │  ┌─────────────────────────────┐│   │      │      │
│  │  port-forward   │◄┼────────┼─▶│      Streaming API          ││   │      │      │
│  │   Process       │ │        │  │   /api/v1/namespaces/       ││   │      │      │
│  └─────────────────┘ │        │  │   {ns}/pods/{pod}/          ││   │      │      │
│           ▲           │        │  │   portforward               ││   │      │      │
│           │           │        │  └─────────────────────────────┘│   │      │      │
│  ┌─────────────────┐ │        │               │                 │   │      │      │
│  │  Local Socket   │ │        │               │ SPDY/WebSocket  │   │      │      │
│  │   Port: 8080    │ │        │               │    Stream       │   │      │      │
│  └─────────────────┘ │        │               ▼                 │   │      │      │
│                      │        │  ┌─────────────────────────────┐│   │      │      │
└──────────────────────┘        │  │         kubelet             ││   │      │      │
                                 │  │    (on worker node)        ││   │      │      │
Network Flow:                    │  └─────────────────────────────┘│   │      │      │
1. App → localhost:8080          │               │                 │   │      │      │
2. kubectl forwards to API       │               │ Direct TCP      │   │      │      │
3. API streams to kubelet        │               │ Connection      │   │      │      │
4. kubelet connects to pod       │               ▼                 │   │      │      │
5. Response flows back           │  ┌─────────────────────────────┐│   │      │      │
                                 │  │       Container            ││───┼──────┘      │
                                 │  │       Network              ││   │             │
                                 │  │    (Pod's localhost)       ││   │             │
                                 │  └─────────────────────────────┘│   │             │
                                 └─────────────────────────────────┘   └─────────────┘

Connection Details:
• kubectl creates local socket listener on port 8080
• Establishes HTTPS connection to API server's streaming endpoint
• API server creates SPDY/WebSocket stream to target kubelet
• kubelet establishes direct TCP connection to pod's port 80
• Bidirectional data flow: Local App ↔ kubectl ↔ API ↔ kubelet ↔ Pod
```

## A.2 kubectl Proxy Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            kubectl proxy Architecture                          │
└─────────────────────────────────────────────────────────────────────────────────┘

Local Machine                    Kubernetes Cluster
┌────────────────────────────┐  ┌─────────────────────────────────────────────────┐
│                            │  │                                                 │
│  ┌───────────────────────┐ │  │  ┌─────────────────────────────────────────────┐│
│  │     Browser/Client    │ │  │  │            API Server                      ││
│  │   (curl, postman)     │ │  │  │        (kube-apiserver)                    ││
│  └───────────────────────┘ │  │  │                                             ││
│             │               │  │  │  ┌─────────────────────────────────────────┐││
│             ▼               │  │  │  │          REST API Endpoints             │││
│  ┌───────────────────────┐ │  │  │  │  • /api/v1/pods                        │││
│  │    kubectl proxy      │ │  │  │  │  • /api/v1/services                     │││
│  │                       │ │  │  │  │  • /apis/apps/v1/deployments            │││
│  │  ┌─────────────────┐  │ │  │  │  │  • /metrics                             │││
│  │  │  HTTP Server    │  │ │  │  │  │  • /logs                                │││
│  │  │  Port: 8080     │  │ │  │  │  └─────────────────────────────────────────┘││
│  │  └─────────────────┘  │ │  │  │                                             ││
│  │           │            │ │  │  │  ┌─────────────────────────────────────────┐││
│  │           ▼            │ │  │  │  │       Authentication & Authorization     │││
│  │  ┌─────────────────┐  │ │  │  │  │  • Client Certificates                  │││
│  │  │  Request Proxy  │  │ │  │  │  │  • Bearer Tokens                        │││
│  │  │   & Rewriter    │  │ │  │  │  │  • RBAC Validation                      │││
│  │  └─────────────────┘  │ │  │  │  └─────────────────────────────────────────┘││
│  │           │            │ │  │  └─────────────────────────────────────────────┘│
│  │           ▼            │ │  │                         ▲                       │
│  │  ┌─────────────────┐  │ │  │                         │                       │
│  │  │  HTTPS Client   │──┼─┼──┼─────────────────────────┘                       │
│  │  │  (with auth)    │  │ │  │          HTTPS + Client Certs                   │
│  │  └─────────────────┘  │ │  │                                                 │
│  └───────────────────────┘ │  └─────────────────────────────────────────────────┘
└────────────────────────────┘

Request Flow Example:
┌────────────────────────────────────────────────────────────────────────────┐
│                            Request Transformation                          │
└────────────────────────────────────────────────────────────────────────────┘

Client Request:                           kubectl proxy Action:
┌─────────────────────────┐                ┌──────────────────────────────┐
│ GET http://localhost:   │                │ 1. Receives HTTP request     │
│ 8080/api/v1/pods        │   ────────►    │ 2. Adds authentication       │
└─────────────────────────┘                │ 3. Rewrites to HTTPS         │
                                          │ 4. Forwards to API server    │
                                          └──────────────────────────────┘
                                                        │
                                                        ▼
API Server Request:                       ┌──────────────────────────────┐
┌─────────────────────────┐               │ HTTPS GET https://k8s-api:   │
│ HTTPS GET https://      │  ◄────────    │ 6443/api/v1/pods             │
│ k8s-api:6443/api/v1/pods│               │ Authorization: Bearer <token>│
│ + Client Certificate    │               │ Client-Certificate: <cert>   │
└─────────────────────────┘               └──────────────────────────────┘

Network Benefits:
• Eliminates need for client-side authentication setup
• Provides secure local HTTP interface to HTTPS API
• Enables easy API exploration and debugging
• Handles certificate management automatically
• Allows direct API access without kubectl command syntax
```

## A.3 Port-Forward vs Proxy Comparison

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Port-Forward vs Proxy Network Patterns                  │
└─────────────────────────────────────────────────────────────────────────────┘

kubectl port-forward                     kubectl proxy
┌─────────────────────────┐               ┌─────────────────────────┐
│  Purpose: Access        │               │  Purpose: API Server    │
│  Application in Pod     │               │  Access & Exploration   │
└─────────────────────────┘               └─────────────────────────┘

Connection Pattern:                      Connection Pattern:
Client → kubectl → API → kubelet → Pod   Client → kubectl → API Server

Use Cases:                               Use Cases:
• Debug application                      • API exploration  
• Access web UI                         • Metrics collection
• Database connections                   • Custom API clients
• Development/testing                    • Dashboard access

Network Layers:                         Network Layers:
┌─────────────────────────┐              ┌─────────────────────────┐
│ Application Protocol    │              │ HTTP/REST Protocol      │
│ (HTTP, MySQL, etc.)     │              │ (JSON responses)        │
├─────────────────────────┤              ├─────────────────────────┤
│ TCP Stream              │              │ HTTP Proxy Layer        │
├─────────────────────────┤              ├─────────────────────────┤
│ SPDY/WebSocket Stream   │              │ HTTPS Client Layer      │
├─────────────────────────┤              ├─────────────────────────┤
│ HTTPS to API Server     │              │ HTTPS to API Server     │
└─────────────────────────┘              └─────────────────────────┘

Security:                               Security:
• End-to-end encryption                 • kubectl handles auth
• No local cert needed                  • No client cert setup needed
• Temporary tunnel                      • Local HTTP interface
```

## A.4 Technical Implementation Notes

### Port-Forward Implementation Details:
- Uses Kubernetes streaming API endpoints (`/portforward`)
- Leverages SPDY protocol for multiplexed streams over HTTP/2
- Creates bidirectional tunnel through API server
- kubelet handles final TCP connection to container

### Proxy Implementation Details:
- Acts as HTTP reverse proxy with authentication injection
- Rewrites incoming HTTP requests to authenticated HTTPS
- Handles all Kubernetes API authentication mechanisms
- Provides RESTful interface without kubectl command syntax

### Security Considerations:
- Both methods inherit kubectl's authentication configuration
- Port-forward: Temporary, session-based access to specific applications
- Proxy: Broader API access requiring appropriate RBAC permissions
- Neither method bypasses Kubernetes security policies
