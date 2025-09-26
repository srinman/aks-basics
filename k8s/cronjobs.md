# Kubernetes CronJobs - Scheduled Task Automation

This guide explains Kubernetes CronJobs, their architecture, scheduling patterns, and provides hands-on examples for automating recurring tasks in your cluster.

## 📖 What are Kubernetes CronJobs?

A **CronJob** in Kubernetes creates Jobs on a time-based schedule, similar to the Unix cron utility. CronJobs are perfect for recurring tasks like backups, reports, cleanup operations, and periodic data processing.

### Key Characteristics:
- **Time-based scheduling**: Uses cron syntax for flexible scheduling
- **Job creation**: Automatically creates Job resources at scheduled times
- **Concurrency control**: Manages overlapping executions
- **History management**: Keeps track of successful and failed job runs
- **Timezone support**: Can schedule across different timezones

## 🏗️ CronJob Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       Kubernetes CronJob Architecture                       │
└─────────────────────────────────────────────────────────────────────────────┘

CronJob Controller (Part of kube-controller-manager)
┌─────────────────────────────────────────────────────────────────────────────┐
│  • Monitors CronJob resources                                               │
│  • Evaluates cron schedule expressions                                      │
│  • Creates Job resources at scheduled times                                 │
│  • Manages job history and cleanup                                          │
│  • Handles concurrency policies                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
CronJob Resource: backup-cronjob
┌─────────────────────────────────────────────────────────────────────────────┐
│ Spec:                                                                       │
│   schedule: "0 2 * * *"           # Every day at 2 AM                      │
│   concurrencyPolicy: Forbid       # Don't allow overlapping jobs           │
│   successfulJobsHistoryLimit: 3   # Keep 3 successful jobs                 │
│   failedJobsHistoryLimit: 1       # Keep 1 failed job                      │
│   jobTemplate: <job-spec>          # Template for created jobs             │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
            ┌───────────────────────┼───────────────────────┐
            │                       │                       │
            ▼                       ▼                       ▼
    ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
    │ Job (Day 1)     │     │ Job (Day 2)     │     │ Job (Day 3)     │
    │ Status: Success │     │ Status: Running │     │ Status: Pending │
    │ ┌─────────────┐ │     │ ┌─────────────┐ │     │                 │
    │ │   Pod       │ │     │ │   Pod       │ │     │   (will create  │
    │ │ Exit: 0     │ │     │ │ Running...  │ │     │    pod later)   │
    │ └─────────────┘ │     │ └─────────────┘ │     │                 │
    └─────────────────┘     └─────────────────┘     └─────────────────┘

Timeline:
Day 1: 02:00 → Job Created → Pod Runs → Success → Kept (history)
Day 2: 02:00 → Job Created → Pod Runs → Running...
Day 3: 02:00 → Job Created → Will start at scheduled time
```

## ⏰ Cron Schedule Syntax

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          Cron Schedule Format                               │
└─────────────────────────────────────────────────────────────────────────────┘

 ┌───────────── minute (0 - 59)
 │ ┌───────────── hour (0 - 23)
 │ │ ┌───────────── day of the month (1 - 31)
 │ │ │ ┌───────────── month (1 - 12)
 │ │ │ │ ┌───────────── day of the week (0 - 6) (Sunday to Saturday)
 │ │ │ │ │
 * * * * *

Common Examples:
┌─────────────────────────┬─────────────────────────────────────────────────────┐
│ Schedule                │ Description                                         │
├─────────────────────────┼─────────────────────────────────────────────────────┤
│ "0 2 * * *"            │ Daily at 2:00 AM                                   │
│ "*/15 * * * *"         │ Every 15 minutes                                    │
│ "0 */2 * * *"          │ Every 2 hours                                       │
│ "0 9 * * 1-5"          │ Weekdays at 9:00 AM                               │
│ "0 0 1 * *"            │ First day of every month at midnight               │
│ "0 0 * * 0"            │ Every Sunday at midnight                            │
│ "30 3 * * 6"           │ Every Saturday at 3:30 AM                          │
│ "0 8-17 * * 1-5"       │ Every hour from 8 AM to 5 PM, Monday to Friday     │
└─────────────────────────┴─────────────────────────────────────────────────────┘

Special Strings (some implementations):
@yearly   = "0 0 1 1 *"     (once a year)
@monthly  = "0 0 1 * *"     (once a month)
@weekly   = "0 0 * * 0"     (once a week)
@daily    = "0 0 * * *"     (once a day)
@hourly   = "0 * * * *"     (once an hour)
```

## 🚀 Practical Examples

### Example 1: Daily Database Backup

Create a file called `database-backup-cronjob.yaml`:

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: database-backup
  labels:
    app: backup
    type: database
spec:
  # Run every day at 2 AM
  schedule: "0 2 * * *"
  
  # Don't allow concurrent executions
  concurrencyPolicy: Forbid
  
  # Keep history of jobs
  successfulJobsHistoryLimit: 7   # Keep 7 successful backups
  failedJobsHistoryLimit: 3       # Keep 3 failed attempts
  
  # Suspend the CronJob (useful for maintenance)
  suspend: false
  
  # Job template
  jobTemplate:
    spec:
      # Timeout after 1 hour
      activeDeadlineSeconds: 3600
      
      template:
        metadata:
          labels:
            app: backup
            job-type: database-backup
        spec:
          restartPolicy: OnFailure
          containers:
          - name: backup-container
            image: postgres:13
            env:
            - name: PGPASSWORD
              value: "backup_password"
            command:
            - /bin/bash
            - -c
            - |
              echo "Starting database backup at $(date)"
              
              # Simulate backup process
              echo "Connecting to database..."
              sleep 5
              
              echo "Dumping database tables..."
              # In real scenario: pg_dump -h db-host -U username dbname > backup.sql
              for table in users orders products; do
                echo "Backing up table: $table"
                sleep 3
              done
              
              echo "Compressing backup files..."
              sleep 2
              
              echo "Uploading to backup storage..."
              sleep 5
              
              echo "Database backup completed successfully at $(date)"
              echo "Backup size: 2.3 GB"
              echo "Files: backup-$(date +%Y%m%d).sql.gz"
              
              exit 0
            resources:
              requests:
                memory: "256Mi"
                cpu: "200m"
              limits:
                memory: "512Mi"
                cpu: "500m"
```

### Example 2: Log Cleanup CronJob

Create a file called `log-cleanup-cronjob.yaml`:

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: log-cleanup
  labels:
    app: maintenance
    type: cleanup
spec:
  # Run every Sunday at 3 AM
  schedule: "0 3 * * 0"
  
  # Allow concurrent runs (cleanup is typically safe)
  concurrencyPolicy: Allow
  
  successfulJobsHistoryLimit: 3
  failedJobsHistoryLimit: 1
  
  jobTemplate:
    spec:
      template:
        spec:
          restartPolicy: OnFailure
          containers:
          - name: log-cleaner
            image: busybox:1.35
            command:
            - /bin/sh
            - -c
            - |
              echo "Starting log cleanup at $(date)"
              
              # Simulate finding old log files
              echo "Scanning for log files older than 30 days..."
              sleep 3
              
              # Simulate cleanup
              OLD_LOGS=("app-2024-08-01.log" "app-2024-08-02.log" "error-2024-07-30.log")
              
              for log in "${OLD_LOGS[@]}"; do
                echo "Removing old log file: $log"
                sleep 1
              done
              
              # Simulate disk space report
              echo "Cleanup completed!"
              echo "Freed disk space: 1.2 GB"
              echo "Remaining log files: 145"
              
              exit 0
            resources:
              requests:
                memory: "64Mi"
                cpu: "100m"
              limits:
                memory: "128Mi"
                cpu: "200m"
```

### Example 3: Report Generation CronJob

Create a file called `report-generator-cronjob.yaml`:

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: daily-report
  labels:
    app: reporting
spec:
  # Run every weekday at 8 AM
  schedule: "0 8 * * 1-5"
  
  # Replace if previous job is still running
  concurrencyPolicy: Replace
  
  successfulJobsHistoryLimit: 5
  failedJobsHistoryLimit: 2
  
  jobTemplate:
    spec:
      parallelism: 1
      completions: 1
      
      template:
        spec:
          restartPolicy: Never
          containers:
          - name: report-generator
            image: busybox:1.35
            command:
            - /bin/sh
            - -c
            - |
              echo "Starting daily report generation at $(date)"
              
              # Simulate data collection
              echo "Collecting user activity data..."
              sleep 5
              
              echo "Collecting sales data..."
              sleep 4
              
              echo "Collecting performance metrics..."
              sleep 3
              
              # Simulate report generation
              echo "Generating report sections:"
              SECTIONS=("Executive Summary" "User Analytics" "Sales Report" "Performance Metrics")
              
              for section in "${SECTIONS[@]}"; do
                echo "  - Processing: $section"
                sleep 2
              done
              
              echo "Formatting report..."
              sleep 2
              
              echo "Daily report generated successfully!"
              echo "Report saved as: daily-report-$(date +%Y%m%d).pdf"
              echo "Report size: 2.1 MB"
              
              exit 0
            resources:
              requests:
                memory: "128Mi"
                cpu: "150m"
```

## 📊 CronJob Management Commands

### Basic Operations

```bash
# Apply CronJob configurations
kubectl apply -f database-backup-cronjob.yaml
kubectl apply -f log-cleanup-cronjob.yaml
kubectl apply -f report-generator-cronjob.yaml

# List all CronJobs
kubectl get cronjobs

# Get detailed information
kubectl describe cronjob database-backup

# View CronJob YAML
kubectl get cronjob database-backup -o yaml

# Check CronJob status
kubectl get cronjob database-backup -o wide
```

### Monitoring and Troubleshooting

```bash
# Watch CronJob executions
kubectl get cronjobs --watch

# View jobs created by CronJob
kubectl get jobs -l app=backup

# Check recent job executions
kubectl get jobs --sort-by=.metadata.creationTimestamp

# View logs from CronJob pods
kubectl logs -l app=backup

# Check events
kubectl get events --field-selector involvedObject.name=database-backup
```

### Manual Triggers and Management

```bash
# Manually trigger a CronJob (create job from CronJob template)
kubectl create job manual-backup --from=cronjob/database-backup

# Suspend a CronJob (stops creating new jobs)
kubectl patch cronjob database-backup -p '{"spec":{"suspend":true}}'

# Resume a suspended CronJob
kubectl patch cronjob database-backup -p '{"spec":{"suspend":false}}'

# Edit CronJob schedule
kubectl edit cronjob database-backup
```

## 🔄 Concurrency Policies

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        CronJob Concurrency Policies                        │
└─────────────────────────────────────────────────────────────────────────────┘

Policy: Allow
┌─────────────────────────────────────────────────────────────────────────────┐
│ Time: 02:00    02:05    02:10    02:15                                     │
│ ──────────────────────────────────────────                                 │
│ Job1:  [████████████████████████████████████████]                          │
│ Job2:         [████████████████████████████████████████]                   │
│ Job3:                  [████████████████████████████████████████]           │
│                                                                             │
│ • Multiple jobs can run simultaneously                                      │
│ • Good for independent, non-conflicting tasks                              │
└─────────────────────────────────────────────────────────────────────────────┘

Policy: Forbid
┌─────────────────────────────────────────────────────────────────────────────┐
│ Time: 02:00    02:05    02:10    02:15                                     │
│ ──────────────────────────────────────────────────────────────────────────  │
│ Job1:  [████████████████████████████████████████]                          │
│ Job2:         ❌ SKIPPED (Job1 still running)                              │
│ Job3:                  [████████████████████████████████████████]           │
│                                                                             │
│ • Skip new job if previous is still running                                 │
│ • Good for resource-intensive or conflicting tasks                         │
└─────────────────────────────────────────────────────────────────────────────┘

Policy: Replace
┌─────────────────────────────────────────────────────────────────────────────┐
│ Time: 02:00    02:05    02:10    02:15                                     │
│ ──────────────────────────────────────────────────────────────────────────  │
│ Job1:  [██████████████] ❌ TERMINATED                                       │
│ Job2:         [████████████████████████████████████████]                   │
│ Job3:                  [██████████████] ❌ TERMINATED                       │
│ Job4:                           [████████████████████████████████████████]  │
│                                                                             │
│ • Terminate running job and start new one                                  │
│ • Good when latest data/execution is more important                        │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 🧪 Advanced Examples

### Example 4: Multi-Container CronJob with Shared Volume

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: data-pipeline
spec:
  schedule: "0 */6 * * *"  # Every 6 hours
  concurrencyPolicy: Forbid
  
  jobTemplate:
    spec:
      template:
        spec:
          restartPolicy: Never
          volumes:
          - name: shared-data
            emptyDir: {}
          
          containers:
          - name: data-extractor
            image: busybox:1.35
            command:
            - /bin/sh
            - -c
            - |
              echo "Extracting data..."
              echo "extracted_data_$(date +%s)" > /shared/raw_data.txt
              sleep 5
              echo "Data extraction completed"
            volumeMounts:
            - name: shared-data
              mountPath: /shared
              
          - name: data-processor
            image: busybox:1.35
            command:
            - /bin/sh
            - -c
            - |
              echo "Waiting for data extraction..."
              while [ ! -f /shared/raw_data.txt ]; do
                sleep 1
              done
              
              echo "Processing data from /shared/raw_data.txt"
              sleep 3
              echo "processed_$(cat /shared/raw_data.txt)" > /shared/processed_data.txt
              echo "Data processing completed"
            volumeMounts:
            - name: shared-data
              mountPath: /shared
```

### Example 5: CronJob with ConfigMap Configuration

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: backup-config
data:
  backup.conf: |
    BACKUP_RETENTION_DAYS=30
    BACKUP_COMPRESSION=gzip
    NOTIFICATION_EMAIL=admin@example.com
    DATABASE_HOST=postgres.default.svc.cluster.local
---
apiVersion: batch/v1
kind: CronJob
metadata:
  name: configurable-backup
spec:
  schedule: "0 1 * * *"
  
  jobTemplate:
    spec:
      template:
        spec:
          restartPolicy: OnFailure
          volumes:
          - name: config-volume
            configMap:
              name: backup-config
              
          containers:
          - name: backup-job
            image: busybox:1.35
            command:
            - /bin/sh
            - -c
            - |
              echo "Loading configuration..."
              source /config/backup.conf
              
              echo "Backup configuration:"
              echo "  Retention: $BACKUP_RETENTION_DAYS days"
              echo "  Compression: $BACKUP_COMPRESSION"
              echo "  Database: $DATABASE_HOST"
              echo "  Notification: $NOTIFICATION_EMAIL"
              
              # Simulate backup with configuration
              echo "Running backup with loaded configuration..."
              sleep 10
              echo "Backup completed successfully"
            volumeMounts:
            - name: config-volume
              mountPath: /config
```

## 🛠️ Troubleshooting CronJobs

### Common Issues and Solutions

**Issue 1: CronJob Not Creating Jobs**
```bash
# Check CronJob status
kubectl describe cronjob <cronjob-name>

# Verify schedule syntax
kubectl get cronjob <cronjob-name> -o yaml | grep schedule

# Check if suspended
kubectl get cronjob <cronjob-name> -o jsonpath='{.spec.suspend}'

# Look at controller events
kubectl get events -n kube-system --field-selector reason=FailedNeedsStart
```

**Issue 2: Jobs Failing Repeatedly**
```bash
# Check job status
kubectl get jobs -l app=<your-app>

# Look at pod logs
kubectl logs -l job-name=<job-name>

# Check resource constraints
kubectl describe job <job-name>

# Review pod events
kubectl describe pods -l job-name=<job-name>
```

**Issue 3: Too Many Jobs in History**
```bash
# Check current job count
kubectl get jobs -l app=<your-app>

# Adjust history limits
kubectl patch cronjob <cronjob-name> -p '{"spec":{"successfulJobsHistoryLimit":3}}'

# Manual cleanup of old jobs
kubectl delete jobs -l app=<your-app> --field-selector status.successful=1
```

### Debugging Commands

```bash
# View CronJob controller logs
kubectl logs -n kube-system -l component=kube-controller-manager | grep cronjob

# Check timezone issues
kubectl get cronjob <name> -o yaml | grep -A5 -B5 schedule

# Test schedule syntax (external tool)
# Use online cron expression testers or:
# python3 -c "from croniter import croniter; print(croniter.get_next(datetime.now(), '0 2 * * *'))"
```

## 📋 Best Practices

### Schedule Design
```yaml
# Good practices for scheduling
spec:
  schedule: "0 2 * * *"              # Use specific times, avoid peak hours
  concurrencyPolicy: Forbid          # Prevent overlapping for resource-heavy tasks
  successfulJobsHistoryLimit: 3      # Keep reasonable history
  failedJobsHistoryLimit: 1          # Keep failed jobs for debugging
  suspend: false                     # Can be used for maintenance windows
  
  jobTemplate:
    spec:
      activeDeadlineSeconds: 3600    # Set timeouts
      backoffLimit: 2                # Limit retries
      
      template:
        spec:
          restartPolicy: OnFailure   # Better than Never for CronJobs
```

### Resource Management
```yaml
containers:
- name: job-container
  resources:
    requests:
      memory: "128Mi"
      cpu: "100m"
    limits:
      memory: "256Mi"
      cpu: "500m"
  
  # Add health checks for long-running jobs
  livenessProbe:
    exec:
      command: ["pgrep", "my-process"]
    initialDelaySeconds: 60
    periodSeconds: 30
```

### Monitoring and Alerting
```bash
# Set up monitoring for CronJob health
kubectl get cronjobs -o json | jq '.items[] | select(.status.lastScheduleTime == null)'

# Monitor failed jobs
kubectl get jobs --field-selector status.successful=0

# Check for suspended CronJobs
kubectl get cronjobs -o json | jq '.items[] | select(.spec.suspend == true)'
```

## 🧹 Cleanup

```bash
# Remove all example CronJobs
kubectl delete cronjob database-backup
kubectl delete cronjob log-cleanup
kubectl delete cronjob daily-report
kubectl delete cronjob data-pipeline
kubectl delete cronjob configurable-backup

# Clean up associated ConfigMap
kubectl delete configmap backup-config

# Remove any remaining jobs
kubectl delete jobs -l app=backup
kubectl delete jobs -l app=maintenance
kubectl delete jobs -l app=reporting

# Verify cleanup
kubectl get cronjobs
kubectl get jobs
```

## 🎯 Key Takeaways

1. **CronJobs automate recurring tasks** using familiar cron syntax
2. **Concurrency policies control** overlapping job executions
3. **History limits manage** the number of kept job records
4. **Resource limits prevent** runaway processes
5. **Proper error handling** includes timeouts and retry limits
6. **Monitoring is essential** for production CronJob reliability

## 🔗 Related Concepts

- **[Jobs](./jobs.md)**: Understanding the Job resources that CronJobs create
- **[Pods](./pods.md)**: The basic units that execute your scheduled tasks
- **[ConfigMaps](./configmapsecrets.md)**: Managing configuration for scheduled jobs
- **[kubectl Commands](./kubectl.md)**: Managing and monitoring CronJobs

---

**Next Steps**: Learn about [DaemonSets](./daemonset.md) for running pods on every node, or explore [Jobs](./jobs.md) for one-time task execution.
