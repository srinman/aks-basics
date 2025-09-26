# Kubernetes Jobs - Running Tasks to Completion

This guide explains Kubernetes Jobs, their architecture, use cases, and provides hands-on examples for running batch workloads and one-time tasks.

## 📖 What are Kubernetes Jobs?

A **Job** in Kubernetes creates one or more pods and ensures that a specified number of them successfully terminate. Jobs are designed for **batch workloads** and **finite tasks** that need to run to completion, unlike Deployments which are meant for long-running services.

### Key Characteristics:
- **Run to completion**: Pods are expected to finish their work and exit
- **Success tracking**: Job tracks how many pods completed successfully
- **Retry logic**: Automatically restarts failed pods (with backoff)
- **Parallelism**: Can run multiple pods concurrently
- **Cleanup**: Can automatically clean up completed pods

## 🏗️ Job Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Kubernetes Jobs Architecture                        │
└─────────────────────────────────────────────────────────────────────────────┘

Job Controller (Part of kube-controller-manager)
┌─────────────────────────────────────────────────────────────────────────────┐
│  • Watches Job resources                                                    │
│  • Creates pods based on Job spec                                          │
│  • Tracks completion status                                                 │
│  • Handles retries and failures                                            │
│  • Updates Job status                                                       │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
Job Resource: data-processing-job
┌─────────────────────────────────────────────────────────────────────────────┐
│ Spec:                                                                       │
│   completions: 3          # Total successful pods needed                   │
│   parallelism: 2          # Max concurrent pods                            │
│   backoffLimit: 6         # Max retries for failed pods                    │
│   template: <pod-spec>    # Pod template                                   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
        ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
        │ Pod 1           │ │ Pod 2           │ │ Pod 3           │
        │ Status: Running │ │ Status: Success │ │ Status: Pending │
        │ ┌─────────────┐ │ │ ┌─────────────┐ │ │ ┌─────────────┐ │
        │ │   Process   │ │ │ │   Process   │ │ │ │   Process   │ │
        │ │ Exit Code:? │ │ │ │ Exit Code: 0│ │ │ │ Exit Code:? │ │
        │ └─────────────┘ │ │ └─────────────┘ │ │ └─────────────┘ │
        └─────────────────┘ └─────────────────┘ └─────────────────┘

Job Lifecycle:
1. Job created → Job Controller creates pods
2. Pods run → Execute the specified task
3. Pods complete → Exit with code 0 (success) or non-zero (failure)
4. Job tracks → Counts successful completions
5. Job finishes → When completions = spec.completions
```

## 🆚 Jobs vs Other Workload Types

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Workload Types Comparison                                │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Deployment    │    │      Job        │    │   CronJob       │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ • Long-running  │    │ • Run to        │    │ • Scheduled     │
│ • Always restart│    │   completion    │    │   jobs          │
│ • Service apps  │    │ • Batch work    │    │ • Recurring     │
│ • Rolling       │    │ • One-time      │    │ • Cron-like     │
│   updates       │    │   tasks         │    │   syntax        │
│                 │    │ • Data          │    │ • Backup,       │
│ Examples:       │    │   processing    │    │   cleanup       │
│ • Web servers   │    │                 │    │                 │
│ • APIs          │    │ Examples:       │    │ Examples:       │
│ • Databases     │    │ • Data import   │    │ • Daily backup  │
│ • Microservices │    │ • ML training   │    │ • Log rotation  │
└─────────────────┘    │ • Image resize  │    │ • Report gen    │
                       │ • Migrations    │    │ • Cleanup tasks │
                       └─────────────────┘    └─────────────────┘
```

## 🚀 Simple Job Example: Data Processing

Let's create a practical example that processes data files and demonstrates Job concepts.

### Example 1: Basic Job - File Processing

Create a file called `data-processing-job.yaml`:

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: data-processing-job
  labels:
    app: data-processor
spec:
  # Job will complete when 1 pod succeeds
  completions: 1
  
  # Only 1 pod will run at a time
  parallelism: 1
  
  # Retry up to 3 times if pods fail
  backoffLimit: 3
  
  # Pod template
  template:
    metadata:
      labels:
        app: data-processor
        job: data-processing
    spec:
      restartPolicy: Never  # Important: Jobs need Never or OnFailure
      containers:
      - name: processor
        image: busybox:1.35
        command: 
        - /bin/sh
        - -c
        - |
          echo "Starting data processing job at $(date)"
          echo "Processing file: input-data.txt"
          
          # Simulate data processing work
          for i in $(seq 1 10); do
            echo "Processing record $i/10"
            sleep 2
          done
          
          echo "Data processing completed successfully at $(date)"
          echo "Results written to: output-results.txt"
          
          # Exit with success
          exit 0
        resources:
          requests:
            memory: "64Mi"
            cpu: "100m"
          limits:
            memory: "128Mi"
            cpu: "200m"
```

**Apply and monitor the Job:**

```bash
# Create the job
kubectl apply -f data-processing-job.yaml

# Watch job progress
kubectl get jobs --watch

# Check job details
kubectl describe job data-processing-job

# View pod logs
kubectl logs -l job=data-processing

# Check job status
kubectl get job data-processing-job -o yaml | grep -A 10 "status:"
```

### Example 2: Parallel Job - Batch Processing

Create a file called `parallel-job.yaml`:

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: parallel-processing-job
  labels:
    app: parallel-processor
spec:
  # Need 5 successful completions
  completions: 5
  
  # Run up to 3 pods in parallel
  parallelism: 3
  
  # Retry up to 2 times
  backoffLimit: 2
  
  template:
    metadata:
      labels:
        app: parallel-processor
    spec:
      restartPolicy: Never
      containers:
      - name: worker
        image: busybox:1.35
        command:
        - /bin/sh
        - -c
        - |
          # Get a unique ID for this pod
          POD_ID=$(hostname | cut -d'-' -f4-)
          echo "Worker $POD_ID starting at $(date)"
          
          # Simulate different processing times
          WORK_TIME=$((5 + RANDOM % 10))
          echo "Worker $POD_ID will work for $WORK_TIME seconds"
          
          # Do the work
          sleep $WORK_TIME
          
          echo "Worker $POD_ID completed successfully at $(date)"
          exit 0
        resources:
          requests:
            memory: "32Mi"
            cpu: "50m"
```

**Apply and observe parallel execution:**

```bash
# Create parallel job
kubectl apply -f parallel-job.yaml

# Watch pods being created and completed
kubectl get pods --watch -l app=parallel-processor

# Monitor job progress
kubectl get job parallel-processing-job --watch

# View logs from all workers
kubectl logs -l app=parallel-processor --prefix=true
```

## 📊 Job Status and Monitoring

### Understanding Job Status

```bash
# Detailed job status
kubectl describe job data-processing-job
```

**Key status fields:**
```yaml
status:
  conditions:
  - type: Complete
    status: "True"
    lastProbeTime: "2025-09-26T10:30:00Z"
    lastTransitionTime: "2025-09-26T10:30:00Z"
  startTime: "2025-09-26T10:28:00Z"
  completionTime: "2025-09-26T10:30:00Z"
  succeeded: 1      # Number of successfully completed pods
  failed: 0         # Number of failed pods
```

### Job Monitoring Commands

```bash
# List all jobs
kubectl get jobs

# Job details with wide output
kubectl get jobs -o wide

# Watch job progress
kubectl get jobs --watch

# Check job events
kubectl describe job <job-name>

# Monitor associated pods
kubectl get pods -l job-name=<job-name>

# View pod logs
kubectl logs job/<job-name>

# Get job YAML status
kubectl get job <job-name> -o yaml
```

## 🔄 Job Lifecycle States

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            Job Lifecycle                                    │
└─────────────────────────────────────────────────────────────────────────────┘

Created → Running → Completed/Failed
   │         │           │
   │         │           └── Complete (succeeded >= completions)
   │         │           └── Failed (failed >= backoffLimit)
   │         │
   │         └── Pods: Pending → Running → Succeeded/Failed
   │
   └── Job Controller creates initial pods

Job Conditions:
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│    Active       │    │    Complete     │    │     Failed      │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ • Has running/  │    │ • All required  │    │ • Too many pod  │
│   pending pods  │    │   pods succeeded│    │   failures      │
│ • Still working │    │ • Job finished  │    │ • Exceeded      │
│ • Not finished  │    │   successfully  │    │   backoffLimit  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🛠️ Advanced Job Patterns

### Pattern 1: Job with Init Container

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: job-with-init
spec:
  template:
    spec:
      restartPolicy: Never
      initContainers:
      - name: setup
        image: busybox:1.35
        command: ['sh', '-c', 'echo "Preparing data..." && sleep 5']
      containers:
      - name: main-job
        image: busybox:1.35
        command: ['sh', '-c', 'echo "Processing prepared data..." && sleep 10']
```

### Pattern 2: Job with Volume for Data Sharing

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: job-with-storage
spec:
  template:
    spec:
      restartPolicy: Never
      volumes:
      - name: shared-data
        emptyDir: {}
      containers:
      - name: data-processor
        image: busybox:1.35
        command:
        - /bin/sh
        - -c
        - |
          echo "Writing results to shared volume..."
          echo "Processing complete" > /data/result.txt
          cat /data/result.txt
        volumeMounts:
        - name: shared-data
          mountPath: /data
```

### Pattern 3: Indexed Job (Kubernetes 1.21+)

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: indexed-job
spec:
  completions: 3
  parallelism: 2
  completionMode: Indexed  # Each pod gets a unique index
  template:
    spec:
      restartPolicy: Never
      containers:
      - name: worker
        image: busybox:1.35
        command:
        - /bin/sh
        - -c
        - |
          echo "Processing batch ${JOB_COMPLETION_INDEX}"
          # Each pod processes different data based on index
          sleep $((5 + JOB_COMPLETION_INDEX * 2))
          echo "Batch ${JOB_COMPLETION_INDEX} completed"
```

## 🧪 Hands-On Exercises

### Exercise 1: Failing Job with Retries

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: failing-job-demo
spec:
  completions: 1
  backoffLimit: 3
  template:
    spec:
      restartPolicy: Never
      containers:
      - name: unreliable-worker
        image: busybox:1.35
        command:
        - /bin/sh
        - -c
        - |
          # Simulate unreliable process (50% failure rate)
          if [ $((RANDOM % 2)) -eq 0 ]; then
            echo "Task failed! Exiting with error."
            exit 1
          else
            echo "Task completed successfully!"
            exit 0
          fi
```

**Observe retry behavior:**
```bash
kubectl apply -f failing-job-demo.yaml
kubectl get pods --watch -l job-name=failing-job-demo
kubectl describe job failing-job-demo
```

### Exercise 2: Job Completion Time Comparison

```bash
# Sequential job (parallelism: 1)
cat <<EOF | kubectl apply -f -
apiVersion: batch/v1
kind: Job
metadata:
  name: sequential-job
spec:
  completions: 4
  parallelism: 1
  template:
    spec:
      restartPolicy: Never
      containers:
      - name: worker
        image: busybox:1.35
        command: ['sleep', '10']
EOF

# Parallel job (parallelism: 4)
cat <<EOF | kubectl apply -f -
apiVersion: batch/v1
kind: Job
metadata:
  name: parallel-job-demo
spec:
  completions: 4
  parallelism: 4
  template:
    spec:
      restartPolicy: Never
      containers:
      - name: worker
        image: busybox:1.35
        command: ['sleep', '10']
EOF

# Compare completion times
kubectl get jobs --watch
```

## 🛠️ Troubleshooting Jobs

### Common Issues and Solutions

**Issue 1: Job Stuck in Active State**
```bash
# Check pod status
kubectl get pods -l job-name=<job-name>

# Look for failed pods
kubectl describe pods -l job-name=<job-name>

# Check resource constraints
kubectl describe nodes
```

**Issue 2: Pods Keep Restarting**
```bash
# Check restart policy (should be Never or OnFailure)
kubectl get job <job-name> -o yaml | grep restartPolicy

# Check exit codes
kubectl logs <pod-name> --previous
```

**Issue 3: Job Never Completes**
```bash
# Check if completions is set correctly
kubectl describe job <job-name>

# Look at pod logs for errors
kubectl logs -l job-name=<job-name>

# Check resource limits
kubectl top pods -l job-name=<job-name>
```

### Debugging Commands

```bash
# View job events
kubectl get events --field-selector involvedObject.name=<job-name>

# Check job controller logs
kubectl logs -n kube-system -l component=kube-controller-manager

# Delete stuck job
kubectl delete job <job-name>

# Force delete if stuck
kubectl delete job <job-name> --force --grace-period=0
```

## 📋 Best Practices

### Job Configuration
- **Always set `restartPolicy`**: Use `Never` or `OnFailure`
- **Set appropriate `backoffLimit`**: Usually 3-6 retries
- **Use resource limits**: Prevent resource starvation
- **Set `activeDeadlineSeconds`**: Timeout for long-running jobs

### Error Handling
```yaml
spec:
  backoffLimit: 3                    # Max retries
  activeDeadlineSeconds: 3600        # 1 hour timeout
  template:
    spec:
      restartPolicy: Never           # Required for Jobs
      containers:
      - name: job-container
        image: my-app:latest
        resources:                   # Always set limits
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "500m"
```

### Monitoring and Cleanup
```bash
# Set TTL for automatic cleanup
spec:
  ttlSecondsAfterFinished: 86400  # Delete after 24 hours

# Manual cleanup
kubectl delete jobs --field-selector status.successful=1
kubectl delete jobs --all
```

## 🧹 Cleanup

```bash
# Clean up all example jobs
kubectl delete job data-processing-job
kubectl delete job parallel-processing-job
kubectl delete job job-with-init
kubectl delete job job-with-storage
kubectl delete job indexed-job
kubectl delete job failing-job-demo
kubectl delete job sequential-job
kubectl delete job parallel-job-demo

# Verify cleanup
kubectl get jobs
kubectl get pods
```

## 🎯 Key Takeaways

1. **Jobs are for finite tasks** that need to run to completion
2. **Completions and parallelism** control how many pods run and when
3. **RestartPolicy must be Never or OnFailure** for Jobs
4. **BackoffLimit controls retries** for failed pods
5. **Jobs track success/failure** and provide reliable task execution
6. **Use Jobs for batch processing**, data migrations, and one-time tasks

## 🔗 Related Concepts

- **[CronJobs](./cronjobs.md)**: Scheduled recurring jobs
- **[Pods](./pods.md)**: Understanding the basic unit Jobs create  
- **[Deployments](./deploymentdemo.md)**: Long-running services vs batch jobs
- **[kubectl Commands](./kubectl.md)**: Managing and monitoring jobs

---

**Next Steps**: Learn about [CronJobs](./cronjobs.md) for scheduled recurring tasks, or explore [Deployments](./deploymentdemo.md) for long-running applications.
