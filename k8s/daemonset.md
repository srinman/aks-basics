# Kubernetes DaemonSets - Running Pods on Every Node

This guide explains Kubernetes DaemonSets, their architecture, use cases, and provides hands-on examples for deploying system-level services across all cluster nodes.

## 📖 What are Kubernetes DaemonSets?

A **DaemonSet** ensures that all (or some) nodes run a copy of a pod. As nodes are added to the cluster, pods are added to them. As nodes are removed from the cluster, those pods are garbage collected. Deleting a DaemonSet will clean up the pods it created.

### Key Characteristics:
- **One pod per node**: Automatically schedules exactly one pod on each eligible node
- **Node lifecycle tracking**: Adds/removes pods as nodes join/leave the cluster
- **System-level services**: Perfect for cluster-wide infrastructure services
- **Node selection**: Can target specific nodes using node selectors
- **Rolling updates**: Supports controlled updates across all nodes

## 🏗️ DaemonSet Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      Kubernetes DaemonSet Architecture                      │
└─────────────────────────────────────────────────────────────────────────────┘

DaemonSet Controller (Part of kube-controller-manager)
┌─────────────────────────────────────────────────────────────────────────────┐
│  • Watches DaemonSet resources and node changes                             │
│  • Ensures one pod per eligible node                                        │
│  • Handles node additions and removals                                      │
│  • Manages rolling updates across nodes                                     │
│  • Applies node selectors and tolerations                                   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
DaemonSet: monitoring-agent
┌─────────────────────────────────────────────────────────────────────────────┐
│ Spec:                                                                       │
│   selector: app=monitoring-agent                                            │
│   template: <pod-template>          # Pod specification                     │
│   updateStrategy: RollingUpdate     # How to handle updates                 │
│   nodeSelector: <node-requirements> # Which nodes to target                 │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        │                           │                           │
        ▼                           ▼                           ▼
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│ Node 1          │         │ Node 2          │         │ Node 3          │
│ ┌─────────────┐ │         │ ┌─────────────┐ │         │ ┌─────────────┐ │
│ │ Pod Instance│ │         │ │ Pod Instance│ │         │ │ Pod Instance│ │
│ │ monitoring- │ │         │ │ monitoring- │ │         │ │ monitoring- │ │
│ │ agent-xyz   │ │         │ │ agent-abc   │ │         │ │ agent-def   │ │
│ │             │ │         │ │             │ │         │ │             │ │
│ │ Collects:   │ │         │ │ Collects:   │ │         │ │ Collects:   │ │
│ │ • Node logs │ │         │ │ • Node logs │ │         │ │ • Node logs │ │
│ │ • Metrics   │ │         │ │ • Metrics   │ │         │ │ • Metrics   │ │
│ │ • Events    │ │         │ │ • Events    │ │         │ │ • Events    │ │
│ └─────────────┘ │         │ └─────────────┘ │         │ └─────────────┘ │
└─────────────────┘         └─────────────────┘         └─────────────────┘

Lifecycle:
• New node joins → DaemonSet Controller creates pod on new node
• Node removed → DaemonSet Controller removes pod
• DaemonSet updated → Rolling update across all nodes
• Node becomes unschedulable → Pod remains (unless evicted)
```

## 🎯 Common DaemonSet Use Cases

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          DaemonSet Use Cases                               │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────┐  ┌─────────────────────────┐  ┌─────────────────────────┐
│    Log Collection       │  │     Monitoring          │  │    Network Services     │
├─────────────────────────┤  ├─────────────────────────┤  ├─────────────────────────┤
│ • Fluentd               │  │ • Node Exporter         │  │ • kube-proxy            │
│ • Filebeat              │  │ • Datadog Agent         │  │ • Calico CNI            │
│ • Logstash Agent        │  │ • New Relic Agent       │  │ • Weave Net             │
│ • Splunk Forwarder      │  │ • Prometheus Node       │  │ • Cilium Agent          │
└─────────────────────────┘  │   Exporter              │  └─────────────────────────┘
                             └─────────────────────────┘
┌─────────────────────────┐  ┌─────────────────────────┐  ┌─────────────────────────┐
│    Security Scanning    │  │    Storage Drivers      │  │    System Maintenance   │
├─────────────────────────┤  ├─────────────────────────┤  ├─────────────────────────┤
│ • Falco                 │  │ • CSI Node Drivers      │  │ • Node Problem Detector │
│ • Twistlock             │  │ • Rook Ceph Agents      │  │ • Cluster Autoscaler    │
│ • Aqua Security         │  │ • GlusterFS Daemon      │  │ • Node Maintenance      │
│ • CIS Benchmark         │  │ • Local Path Provisioner│  │ • OS Updates            │
└─────────────────────────┘  └─────────────────────────┘  └─────────────────────────┘

Key Principle: If every node needs it, use a DaemonSet!
```

## 🚀 Practical Examples

### Example 1: Log Collection Agent

Create a file called `log-collector-daemonset.yaml`:

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: log-collector
  labels:
    app: log-collector
spec:
  selector:
    matchLabels:
      name: log-collector
      
  template:
    metadata:
      labels:
        name: log-collector
        app: log-collector
    spec:
      # Tolerate master node taints to run on all nodes
      tolerations:
      - key: node-role.kubernetes.io/control-plane
        operator: Exists
        effect: NoSchedule
      - key: node-role.kubernetes.io/master
        operator: Exists
        effect: NoSchedule
        
      containers:
      - name: log-collector
        image: busybox:1.35
        command:
        - /bin/sh
        - -c
        - |
          echo "Log Collector Agent starting on node: $NODE_NAME"
          echo "Collecting logs from: /var/log/pods"
          
          while true; do
            echo "[$(date)] Scanning for new log files..."
            
            # Simulate log collection
            LOG_COUNT=$(find /var/log -name "*.log" 2>/dev/null | wc -l)
            echo "[$(date)] Found $LOG_COUNT log files to process"
            
            # Simulate processing
            echo "[$(date)] Processing application logs..."
            sleep 5
            
            echo "[$(date)] Processing system logs..."
            sleep 3
            
            echo "[$(date)] Forwarding logs to central collector..."
            sleep 2
            
            echo "[$(date)] Log collection cycle completed. Next scan in 30s"
            sleep 30
          done
        
        env:
        - name: NODE_NAME
          valueFrom:
            fieldRef:
              fieldPath: spec.nodeName
        - name: POD_NAME
          valueFrom:
            fieldRef:
              fieldPath: metadata.name
              
        resources:
          requests:
            memory: "64Mi"
            cpu: "50m"
          limits:
            memory: "128Mi"
            cpu: "100m"
            
        volumeMounts:
        - name: varlog
          mountPath: /var/log
          readOnly: true
        - name: varlibdockercontainers
          mountPath: /var/lib/docker/containers
          readOnly: true
          
      # Host volumes to access logs
      volumes:
      - name: varlog
        hostPath:
          path: /var/log
      - name: varlibdockercontainers
        hostPath:
          path: /var/lib/docker/containers
          
      # Ensure pods land on nodes with available disk
      nodeSelector:
        kubernetes.io/os: linux
```

### Example 2: Node Monitoring Agent

Create a file called `node-monitor-daemonset.yaml`:

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: node-monitor
  labels:
    app: node-monitor
spec:
  selector:
    matchLabels:
      name: node-monitor
      
  # Rolling update strategy
  updateStrategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1  # Only update 1 node at a time
      
  template:
    metadata:
      labels:
        name: node-monitor
        app: node-monitor
    spec:
      # Run with host network for accurate monitoring
      hostNetwork: true
      hostPID: true
      
      containers:
      - name: node-monitor
        image: busybox:1.35
        command:
        - /bin/sh
        - -c
        - |
          echo "Node Monitor starting on: $NODE_NAME"
          echo "Pod: $POD_NAME"
          echo "Host Network: $(hostname -i)"
          
          while true; do
            echo "=== Node Health Check at $(date) ==="
            
            # CPU usage simulation
            CPU_USAGE=$((RANDOM % 100))
            echo "CPU Usage: ${CPU_USAGE}%"
            
            # Memory usage simulation
            MEM_USAGE=$((RANDOM % 100))
            echo "Memory Usage: ${MEM_USAGE}%"
            
            # Disk usage simulation
            DISK_USAGE=$((RANDOM % 100))
            echo "Disk Usage: ${DISK_USAGE}%"
            
            # Network check
            echo "Network Interfaces: $(ls /sys/class/net/ | tr '\n' ' ')"
            
            # Process count
            PROC_COUNT=$(ps aux | wc -l)
            echo "Running Processes: $PROC_COUNT"
            
            # Load average simulation
            LOAD_AVG="$((RANDOM % 5)).$((RANDOM % 99))"
            echo "Load Average: $LOAD_AVG"
            
            # Alert simulation
            if [ $CPU_USAGE -gt 80 ]; then
              echo "⚠️  ALERT: High CPU usage detected!"
            fi
            
            if [ $MEM_USAGE -gt 85 ]; then
              echo "⚠️  ALERT: High memory usage detected!"
            fi
            
            echo "Metrics sent to monitoring system"
            echo "Next check in 60 seconds..."
            echo "================================="
            sleep 60
          done
        
        env:
        - name: NODE_NAME
          valueFrom:
            fieldRef:
              fieldPath: spec.nodeName
        - name: POD_NAME
          valueFrom:
            fieldRef:
              fieldPath: metadata.name
              
        resources:
          requests:
            memory: "32Mi"
            cpu: "25m"
          limits:
            memory: "64Mi"
            cpu: "100m"
            
        # Security context for host access
        securityContext:
          privileged: true
          
        volumeMounts:
        - name: proc
          mountPath: /host/proc
          readOnly: true
        - name: sys
          mountPath: /host/sys
          readOnly: true
          
      volumes:
      - name: proc
        hostPath:
          path: /proc
      - name: sys
        hostPath:
          path: /sys
          
      tolerations:
      # Allow running on master nodes
      - operator: Exists
```

### Example 3: Security Scanner DaemonSet

Create a file called `security-scanner-daemonset.yaml`:

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: security-scanner
  labels:
    app: security-scanner
spec:
  selector:
    matchLabels:
      name: security-scanner
      
  template:
    metadata:
      labels:
        name: security-scanner
        app: security-scanner
    spec:
      containers:
      - name: security-scanner
        image: busybox:1.35
        command:
        - /bin/sh
        - -c
        - |
          echo "Security Scanner starting on node: $NODE_NAME"
          
          # Initial scan
          echo "Performing initial security scan..."
          sleep 10
          
          while true; do
            echo "=== Security Scan Report - $(date) ==="
            
            # Simulate vulnerability scan
            echo "Scanning for vulnerabilities..."
            VULN_COUNT=$((RANDOM % 10))
            echo "Found $VULN_COUNT potential vulnerabilities"
            
            # Simulate compliance check
            echo "Running compliance checks..."
            COMPLIANCE_SCORE=$((80 + RANDOM % 20))
            echo "Compliance Score: $COMPLIANCE_SCORE%"
            
            # Simulate file integrity check
            echo "Checking file integrity..."
            INTEGRITY_ISSUES=$((RANDOM % 3))
            echo "File integrity issues: $INTEGRITY_ISSUES"
            
            # Simulate network security scan
            echo "Scanning network connections..."
            SUSPICIOUS_CONN=$((RANDOM % 5))
            echo "Suspicious connections: $SUSPICIOUS_CONN"
            
            # Generate alerts if needed
            if [ $VULN_COUNT -gt 5 ]; then
              echo "🚨 SECURITY ALERT: High vulnerability count!"
            fi
            
            if [ $COMPLIANCE_SCORE -lt 85 ]; then
              echo "⚠️  COMPLIANCE WARNING: Score below threshold"
            fi
            
            echo "Security scan completed. Next scan in 5 minutes."
            echo "============================================="
            sleep 300  # 5 minutes
          done
        
        env:
        - name: NODE_NAME
          valueFrom:
            fieldRef:
              fieldPath: spec.nodeName
              
        resources:
          requests:
            memory: "64Mi"
            cpu: "50m"
          limits:
            memory: "128Mi"
            cpu: "200m"
      
      # Only run on worker nodes (not masters)
      nodeSelector:
        node-role.kubernetes.io/worker: ""
      
      # Don't run on nodes with specific taint
      tolerations:
      - key: "dedicated"
        operator: "Equal"
        value: "monitoring"
        effect: "NoSchedule"
```

## 📊 DaemonSet Management Commands

### Basic Operations

```bash
# Apply DaemonSet configurations
kubectl apply -f log-collector-daemonset.yaml
kubectl apply -f node-monitor-daemonset.yaml
kubectl apply -f security-scanner-daemonset.yaml

# List all DaemonSets
kubectl get daemonsets

# Get DaemonSet details
kubectl describe daemonset log-collector

# View DaemonSet YAML
kubectl get daemonset log-collector -o yaml

# Check DaemonSet status
kubectl get daemonset log-collector -o wide
```

### Monitoring and Status

```bash
# Watch DaemonSet rollout
kubectl rollout status daemonset/log-collector

# View DaemonSet pods across nodes
kubectl get pods -o wide -l app=log-collector

# Check which nodes have DaemonSet pods
kubectl get pods -l app=log-collector --field-selector status.phase=Running

# Monitor DaemonSet events
kubectl get events --field-selector involvedObject.name=log-collector

# View logs from all DaemonSet pods
kubectl logs -l app=log-collector --prefix=true
```

### Updates and Rollbacks

```bash
# Update DaemonSet image
kubectl set image daemonset/log-collector log-collector=busybox:1.36

# Check rollout history
kubectl rollout history daemonset/log-collector

# Rollback to previous version
kubectl rollout undo daemonset/log-collector

# Pause rollout
kubectl rollout pause daemonset/log-collector

# Resume rollout
kubectl rollout resume daemonset/log-collector
```

## 🔄 Update Strategies

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        DaemonSet Update Strategies                         │
└─────────────────────────────────────────────────────────────────────────────┘

RollingUpdate Strategy (Default)
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│ Time:    T0      T1      T2      T3      T4                                │
│ ──────────────────────────────────────────────────────────────────────────  │
│ Node1: [Old] → [New] ✓                                                     │
│ Node2: [Old] ────────→ [New] ✓                                             │
│ Node3: [Old] ──────────────────→ [New] ✓                                   │
│ Node4: [Old] ────────────────────────────→ [New] ✓                         │
│                                                                             │
│ • Updates nodes one by one (configurable)                                  │
│ • Respects maxUnavailable setting                                          │
│ • Safe for critical system services                                        │
│ • Can be paused and resumed                                                 │
└─────────────────────────────────────────────────────────────────────────────┘

OnDelete Strategy
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│ Time:    T0      T1      T2      T3      T4                                │
│ ──────────────────────────────────────────────────────────────────────────  │
│ Node1: [Old] → (manual delete) → [New] ✓                                   │
│ Node2: [Old] ──────────────────────────────────────────────────────────     │
│ Node3: [Old] ──────────────────────────────────────────────────────────     │
│ Node4: [Old] ──────────────────────────────────────────────────────────     │
│                                                                             │
│ • Updates only when pods are manually deleted                              │
│ • Full manual control over update timing                                   │
│ • Good for testing or controlled environments                              │
│ • Requires manual intervention for each node                               │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Rolling Update Configuration

```yaml
spec:
  updateStrategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1        # Number or percentage of nodes that can be unavailable
      # maxUnavailable: 25%    # Alternative: percentage
  
  # For OnDelete strategy:
  # updateStrategy:
  #   type: OnDelete
```

## 🧪 Advanced DaemonSet Features

### Example 4: DaemonSet with Node Affinity

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: gpu-monitor
spec:
  selector:
    matchLabels:
      name: gpu-monitor
      
  template:
    metadata:
      labels:
        name: gpu-monitor
    spec:
      # Only run on nodes with GPUs
      affinity:
        nodeAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
            nodeSelectorTerms:
            - matchExpressions:
              - key: accelerator
                operator: In
                values: ["nvidia-tesla-k80", "nvidia-tesla-p100"]
              - key: instance-type
                operator: In
                values: ["gpu-instance"]
                
      containers:
      - name: gpu-monitor
        image: busybox:1.35
        command:
        - /bin/sh
        - -c
        - |
          echo "GPU Monitor running on node with GPUs: $NODE_NAME"
          while true; do
            echo "Monitoring GPU utilization..."
            echo "GPU Temperature: $((60 + RANDOM % 20))°C"
            echo "GPU Memory Usage: $((RANDOM % 100))%"
            echo "GPU Utilization: $((RANDOM % 100))%"
            sleep 30
          done
        env:
        - name: NODE_NAME
          valueFrom:
            fieldRef:
              fieldPath: spec.nodeName
```

### Example 5: DaemonSet with Multiple Containers

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: comprehensive-monitor
spec:
  selector:
    matchLabels:
      name: comprehensive-monitor
      
  template:
    metadata:
      labels:
        name: comprehensive-monitor
    spec:
      containers:
      # Metrics collector
      - name: metrics-collector
        image: busybox:1.35
        command:
        - /bin/sh
        - -c
        - |
          while true; do
            echo "Collecting system metrics..."
            echo "CPU: $((RANDOM % 100))%, Memory: $((RANDOM % 100))%"
            sleep 30
          done
        resources:
          requests:
            memory: "32Mi"
            cpu: "25m"
            
      # Log forwarder
      - name: log-forwarder
        image: busybox:1.35
        command:
        - /bin/sh
        - -c
        - |
          while true; do
            echo "Forwarding logs to central system..."
            echo "Processed $((RANDOM % 1000)) log entries"
            sleep 45
          done
        resources:
          requests:
            memory: "32Mi"
            cpu: "25m"
            
      # Health checker
      - name: health-checker
        image: busybox:1.35
        command:
        - /bin/sh
        - -c
        - |
          while true; do
            echo "Performing health checks..."
            if [ $((RANDOM % 10)) -gt 8 ]; then
              echo "⚠️  Health issue detected!"
            else
              echo "✅ Node health OK"
            fi
            sleep 60
          done
        resources:
          requests:
            memory: "16Mi"
            cpu: "10m"
```

## 🛠️ Troubleshooting DaemonSets

### Common Issues and Solutions

**Issue 1: DaemonSet Pod Not Scheduled on Some Nodes**
```bash
# Check node taints and tolerations
kubectl describe nodes

# Check node selectors
kubectl get daemonset <name> -o yaml | grep -A10 nodeSelector

# Check node labels
kubectl get nodes --show-labels

# Verify pod can schedule on nodes
kubectl describe pod <daemonset-pod-name>
```

**Issue 2: DaemonSet Update Stuck**
```bash
# Check rollout status
kubectl rollout status daemonset/<name>

# Check for resource constraints
kubectl describe nodes

# Look at pod events
kubectl describe pods -l app=<daemonset-app>

# Check update strategy
kubectl get daemonset <name> -o yaml | grep -A5 updateStrategy
```

**Issue 3: Pods Failing on Specific Nodes**
```bash
# Check pod logs on failing nodes
kubectl logs -l app=<daemonset-app> --field-selector spec.nodeName=<node-name>

# Check node conditions
kubectl describe node <node-name>

# Verify resource availability
kubectl top node <node-name>

# Check for node-specific issues
kubectl get events --field-selector involvedObject.name=<node-name>
```

### Debugging Commands

```bash
# Get DaemonSet pod distribution
kubectl get pods -o wide -l app=<daemonset-app> | awk '{print $7}' | sort | uniq -c

# Check which nodes don't have DaemonSet pods
comm -23 <(kubectl get nodes -o name | cut -d/ -f2 | sort) <(kubectl get pods -l app=<app> -o jsonpath='{.items[*].spec.nodeName}' | tr ' ' '\n' | sort)

# Monitor DaemonSet pod creation
kubectl get pods -l app=<daemonset-app> --watch

# Check DaemonSet controller logs
kubectl logs -n kube-system -l component=kube-controller-manager | grep daemonset
```

## 📋 Best Practices

### Resource Management
```yaml
spec:
  template:
    spec:
      containers:
      - name: daemon-container
        resources:
          requests:
            memory: "64Mi"      # Always set requests for scheduling
            cpu: "50m"
          limits:
            memory: "128Mi"     # Set limits to prevent resource exhaustion
            cpu: "200m"
            
        # Use resource quotas for critical system pods
        priorityClassName: system-node-critical
```

### Security Considerations
```yaml
spec:
  template:
    spec:
      # Minimize privileges
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 2000
        
      containers:
      - name: daemon-container
        securityContext:
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true
          capabilities:
            drop:
            - ALL
            add:
            - NET_BIND_SERVICE  # Only add necessary capabilities
```

### Update Safety
```yaml
spec:
  updateStrategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1       # Conservative updates
      
  template:
    spec:
      containers:
      - name: daemon-container
        # Health checks for safe updates
        readinessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 10
          periodSeconds: 5
          
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
```

### Node Selection Best Practices
```yaml
spec:
  template:
    spec:
      # Use node selectors for targeting
      nodeSelector:
        kubernetes.io/os: linux
        node-type: worker
        
      # Use tolerations for special nodes
      tolerations:
      - key: "dedicated"
        operator: "Equal"
        value: "monitoring"
        effect: "NoSchedule"
        
      # Use affinity for complex placement rules
      affinity:
        nodeAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            preference:
              matchExpressions:
              - key: node-role.kubernetes.io/worker
                operator: Exists
```

## 🧹 Cleanup

```bash
# Remove all example DaemonSets
kubectl delete daemonset log-collector
kubectl delete daemonset node-monitor
kubectl delete daemonset security-scanner
kubectl delete daemonset gpu-monitor
kubectl delete daemonset comprehensive-monitor

# Verify cleanup (may take a moment for pods to terminate)
kubectl get daemonsets
kubectl get pods -l app=log-collector
kubectl get pods -l app=node-monitor
kubectl get pods -l app=security-scanner

# Check that no DaemonSet pods remain
kubectl get pods --all-namespaces | grep -E "(log-collector|node-monitor|security-scanner)"
```

## 🎯 Key Takeaways

1. **DaemonSets ensure one pod per eligible node** automatically
2. **Perfect for system-level services** like monitoring, logging, and security
3. **Node changes are handled automatically** - pods added/removed with nodes
4. **Rolling updates enable safe cluster-wide updates** of critical services
5. **Tolerations and node selectors** provide fine-grained placement control
6. **Resource limits are crucial** to prevent system-level pods from impacting workloads

## 🔗 Related Concepts

- **[Deployments](./deploymentdemo.md)**: Application workloads vs system services
- **[Jobs](./jobs.md)**: One-time tasks vs continuous system services
- **[Pods](./pods.md)**: Understanding the basic units DaemonSets manage
- **[kubectl Commands](./kubectl.md)**: Managing and monitoring DaemonSets

---

**Next Steps**: Learn about [StatefulSets](./statefulsets.md) for stateful applications, or explore [Services](./service.md) for networking DaemonSet pods.
