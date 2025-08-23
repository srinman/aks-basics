# Kubernetes Pods Demo

## Overview
A Pod is the smallest deployable unit in Kubernetes. It represents a group of one or more containers that share storage, network, and specifications for how to run the containers. Think of a Pod as a "logical host" similar to a VM, but much more lightweight.

## Key Concepts
- **Pod as a VM analogy**: A Pod provides isolated process namespace, network namespace, and filesystem (like a lightweight VM)
- **Linux constructs**: Pods use Linux namespaces and cgroups for isolation
- **Shared resources**: All containers in a Pod share the same IP address and storage volumes
- **Ephemeral nature**: Pods are designed to be disposable and replaceable

## Demo Commands

### 1. Deploy a Simple Pod

Create and deploy a basic nginx pod using bash EOF syntax:

```bash
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: demo-pod
  labels:
    app: demo
spec:
  containers:
  - name: nginx
    image: nginx:latest
    ports:
    - containerPort: 80
EOF
```

### 2. Deploy a Debug Pod (Full Linux Tools)

Since nginx containers have limited utilities, deploy a netshoot pod for full Linux exploration with networking tools:

```bash
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: debug-pod
spec:
  containers:
  - name: netshoot
    image: nicolaka/netshoot
    command: ['sleep', '3600']
EOF
```

### 3. Basic Pod Display Commands

```bash
# List all pods
kubectl get pods

# Show detailed pod information
kubectl describe pod demo-pod
kubectl describe pod debug-pod

# Get pod YAML configuration
kubectl get pod demo-pod -o yaml

# Get pod details with node placement
kubectl get pod demo-pod -o wide

# Watch pod status in real-time
kubectl get pods -w
```

### 4. Inspect Pod's Linux Environment

#### System Information (VM-like inspection)
```bash
# Show kernel and system info (like uname on a VM)
kubectl exec -it demo-pod -- uname -a

# Show container OS details
kubectl exec -it demo-pod -- cat /etc/os-release

# Show hostname (each pod has unique hostname)
kubectl exec -it demo-pod -- hostname

# Show environment variables
kubectl exec -it demo-pod -- env
```

```bash
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: debug-pod
spec:
  containers:
  - name: netshoot
    image: nicolaka/netshoot
    command: ['sleep', '3600']
EOF
```

#### Process Inspection (Linux constructs)
```bash
# Note: nginx container has limited utilities, use /proc for process info
# Show process namespaces (PID 1 is nginx in container)
kubectl exec -it demo-pod -- ls -la /proc/1/

# Show init process (compare to systemd on VM)
kubectl exec -it demo-pod -- cat /proc/1/comm

# Show process status
kubectl exec -it demo-pod -- cat /proc/1/status

# List all processes via /proc (since ps not available)
kubectl exec -it demo-pod -- ls /proc/*/comm 2>/dev/null | head -10

# Use debug pod for full process inspection:

kubectl exec -it debug-pod -- ps aux
kubectl exec -it debug-pod -- ps -ef  
kubectl exec -it debug-pod -- top -b -n 1

# open a new terminal and enter the following command
kubectl exec -it debug-pod -- sleep 100

# switch back to the original terminal   
kubectl exec -it debug-pod -- ps aux
```

#### Network Inspection (VM comparison)
```bash
# Show network interfaces (most containers have ip command)
kubectl exec -it debug-pod -- ip addr show
# (or)
kubectl exec -it debug-pod -- cat /proc/net/dev

# Show routing table
kubectl exec -it debug-pod -- ip route
# (or)
kubectl exec -it debug-pod -- cat /proc/net/route

# Show DNS configuration
kubectl exec -it debug-pod -- cat /etc/resolv.conf

```


### 5. Pod Construction – Inside Out (From YAML to Running Processes)

This section explains how a Pod “comes to life” in Kubernetes and how Linux namespaces + an **infra (pause) container** form the *pod sandbox* that other containers join. We’ll start with a special debug manifest (`sshrootpod.yaml`) that uses `nsenter` to attach to the host’s PID 1 (NOT a normal application pod), then walk through how a regular pod is actually built under the hood, exposing the infra container with `crictl`.

#### 5.1 Start: The `sshrootpod.yaml` (Host Namespace Entry Pod)

`sshrootpod.yaml` (simplified – runtime fields removed):
```bash
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: nsenter-test
spec:
  hostPID: true
  hostNetwork: true
  hostIPC: true
  containers:
  - name: nsenter
    image: alpine
    securityContext:
      privileged: true
    command: ["nsenter","--target","1","--mount","--uts","--ipc","--net","--pid","bash","-l"]
    tty: true
    stdin: true
EOF
```

Key points:
1. `--target 1` attaches to the **host’s PID 1** (usually `systemd`), so once inside you are effectively in the host namespaces listed by the flags.
2. `--mount --uts --ipc --net --pid` tells `nsenter` to join those namespaces of PID 1.
3. `privileged: true` + `hostPID/hostNetwork/hostIPC: true` weaken isolation—this pod is *only for deep debugging*.
4. This does **not** represent normal pod isolation; instead it *bypasses* it to inspect the node.

Create it:
```bash
kubectl apply -f sshrootpod.yaml
kubectl get pod nsenter-test -o wide
```

Enter the container (which immediately nsenters host namespaces):
```bash
kubectl exec -it nsenter-test -- bash
```
Validate you are in host PID namespace (your PID won’t be 1, but `/proc/1` is host init):
```bash
ps -p 1 -o pid,cmd
readlink /proc/1/ns/pid
hostnamectl status | head -3
ip addr show | head -20
```
You’ll see full host processes, interfaces, etc.

> NOTE: Normal application pods do NOT see host PID 1. We use this privileged pattern strictly to learn how the kubelet + container runtime assemble pods.

#### 5.2 Normal Pod Lifecycle (What Really Happens)

When you create a regular pod (e.g. `demo-pod` earlier):
1. **API Server** stores pod object (Desired State)
2. **Scheduler** assigns a `nodeName`
3. **Kubelet** on that node asks the **CRI runtime** (containerd / CRI-O) to:
   - Create a **Pod Sandbox** (the “infra” / “pause” container). This creates the network namespace, loopback, veth pair, applies DNS, hostname (UTS), IPC namespace, etc.
   - Start each user container *joining* the sandbox’s network + IPC + UTS namespaces.
   - Optionally configure PID namespace sharing (off by default unless `shareProcessNamespace: true`).
4. CNI plugin allocates pod IP and plugs veth into the node bridge / overlay.
5. Readiness/liveness probes begin; controllers observe status.

Infra container:
* Image is usually `registry.k8s.io/pause:<tag>` (AKS may use `mcr.microsoft.com/oss/kubernetes/pause:<tag>`)
* It does almost nothing (sleeps) but **holds** the namespaces alive.

#### 5.3 Inspecting the Infra (Pause) Container with `crictl`

First find the node of a standard pod (NOT the nsenter one):
```bash
kubectl get pod demo-pod -o wide
NODE=$(kubectl get pod demo-pod -o jsonpath='{.spec.nodeName}')
echo $NODE
```

Open a node debug shell (pick one method):
```bash
# Option A (K8s 1.25+):
kubectl debug node/$NODE -it --image=nicolaka/netshoot -- chroot /host bash

# Option B (SSH if you have direct node access) – outside scope here.
```

Inside the node shell install / use crictl (AKS usually has it preinstalled at /usr/bin/crictl):
```bash
crictl pods | grep demo-pod          # Lists Pod sandboxes
crictl ps -a | grep demo-pod         # Lists containers (including pause)
```

Show the pod sandbox (infra) details:
```bash
POD_ID=$(crictl pods --name demo-pod -q)
crictl inspectp $POD_ID
crictl inspectp $POD_ID  | grep pause

crictl inspectp $POD_ID | jq -r '.info.image'
crictl inspectp $POD_ID | jq -r '.info.runtimeType'

# OCI spec passed to runc
crictl inspectp $POD_ID | jq -r '.info.runtimeSpec'

# pid of the sandbox container
crictl inspectp $POD_ID | jq -r '.info.pid'

# check containerd status
ps -ef | grep containerd
systemctl status containerd

# check logs for containerd 
journalctl --unit=containerd.service  

# moving between pods
crictl ps
# get container id of an nginx
crictl inspect <containerid> | jq '.info.pid'
# check process with grep
ps -ef | grep  <pid>
# get ppid of ps -ef and issue ps -ef | grep <ppid>      - this should be containerd-shim 
# enter its namespace
nsenter -t <pid> -a
# now you are in a different pod!
cat /etc/hostname 
```

**Understanding the Pod Sandbox Output:**

The `crictl inspectp` command reveals the **pod sandbox** - the foundational Linux construct that Kubernetes creates before any application containers. This is the "infra container" that holds the shared namespaces:

**Key sections to examine:**

1. **`.info.pid`** - The sandbox process PID (the "pause" container's PID)
2. **`.info.runtimeSpec.linux.namespaces`** - Linux namespaces created for this pod
3. **`.info.config.linux.security_context`** - Security constraints
4. **`.status.network.ip`** - Pod IP address assigned by CNI

**Linux Namespace Creation:**
```bash
crictl inspectp $POD_ID | jq '.info.runtimeSpec.linux.namespaces'
```

This shows how Kubernetes constructs pod isolation using Linux namespaces:

**IMPORTANT: PID Namespace Behavior**
- **By default**: Each container gets its **own PID namespace** - each sees its own process tree starting from PID 1
- **Exception**: When `shareProcessNamespace: true` is set, all containers in the pod share one PID namespace

**Namespace Types:**
- **`"type": "pid"`** - **Each container isolated by default** (separate process trees with own PID 1)
- **`"type": "ipc"`** - **Shared between containers** in the pod (shared memory/semaphores)  
- **`"type": "uts"`** - **Shared between containers** in the pod (same hostname/domain name)
- **`"type": "mount"`** - **Each container isolated** (separate filesystem views)
- **`"type": "network", "path": "/var/run/netns/..."`** - **Shared between containers** in the pod (same IP/interfaces)

**Why does network show a path but others don't?**
- Network namespace is **materialized early** by the CNI plugin and bind-mounted under `/var/run/netns/`
- Other namespaces are created but only get concrete `/proc/<pid>/ns/*` paths when containers join them
- The sandbox spec declares namespace *types to create*; container specs add actual *paths to join*

**Pod IP and Network Plumbing:**
```bash
crictl inspectp $POD_ID | jq '.status.network'
```
Shows the pod's IP address and network interface details - this is how the pod gets its cluster-routable IP.

**Security Context:**
```bash
crictl inspectp $POD_ID | jq '.info.config.linux.security_context'
```
Reveals Linux capabilities, SELinux labels, and other security constraints applied to the pod sandbox.

List the workload container(s):
```bash
crictl ps --pod $POD_ID   # Under containerd shows ONLY workload containers (NOT the pause sandbox)

# Application container (named nginx here)
APP_CTR_ID=$(crictl ps --pod $POD_ID | awk '/nginx/{print $1}')
echo "App container: $APP_CTR_ID"

# Inspect its namespaces
crictl inspect $APP_CTR_ID | jq '.info.runtimeSpec.linux.namespaces'
```

**Why doesn't `crictl ps ` show the pause container?**

In **containerd** (which AKS uses), the pause container is implemented as a **sandbox**, not a regular container:

1. **Sandbox vs Container distinction**: The pause container is the "pod sandbox" that creates and holds namespaces
2. **`crictl ps`** lists **containers** (your workload: nginx, app containers)  
3. **`crictl pods`** lists **sandboxes** (the pause/infra containers)
4. The sandbox is a different OCI runtime construct - it's the namespace anchor, not a typical container

**In other CRI runtimes** (like CRI-O), you might see the pause container listed with name "POD" in `crictl ps`, but containerd treats it as a separate sandbox entity.

**To see the pause process**, use the sandbox PID:
```bash
SANDBOX_PID=$(crictl inspectp $POD_ID | jq -r '.info.pid')
ps -p $SANDBOX_PID -o pid,ppid,cmd
```
This shows the actual pause process (usually `/pause` binary) running as the namespace holder.

Getting the *sandbox (pause) PID* (since it is not listed as a normal container in containerd output):
```bash
SANDBOX_PID=$(crictl inspectp $POD_ID | jq -r '.info.pid')
echo Sandbox PID: $SANDBOX_PID
APP_PID=$(crictl inspect $APP_CTR_ID | jq -r '.info.pid')
echo App PID: $APP_PID

SANDBOX_PID=$(crictl inspectp $POD_ID | jq -r '.info.pid')
echo Sandbox PID: $SANDBOX_PID
APP_PID=$(crictl inspect $APP_CTR_ID | jq -r '.info.pid')
echo App PID: $APP_PID

# Find the parent process of the sandbox container
echo "=== Finding Container Runtime Process Tree ==="
SANDBOX_PPID=$(ps -ef | awk -v pid=$SANDBOX_PID '$2 == pid {print $3}')
echo "Sandbox Parent PID: $SANDBOX_PPID"

# Show the complete process tree from the container runtime
echo "=== Complete Process Tree ==="
pstree -a -p $SANDBOX_PPID
``` 

**Understanding the Process Tree Output:**

The process tree shows the complete Linux process hierarchy for the pod:

**Typical Structure:**
```
containerd-shim(12345)
├─pause(23456)           # Sandbox container (namespace holder)  
└─nginx(34567)           # Application container (joins sandbox namespaces)
```

**Key Insights:**
- **Container Runtime Management**: containerd-shim manages both sandbox and application containers
- **Separate Processes**: Each container runs as an independent Linux process
- **Namespace Sharing**: Despite being separate processes, containers share network/IPC/UTS namespaces
- **Process Isolation**: Each container has its own PID namespace (unless `shareProcessNamespace: true`)

# Compare namespace symlinks directly
```
for NS in net uts ipc pid mnt; do 
  echo "[$NS namespace]"
  SANDBOX_NS=$(readlink /proc/$SANDBOX_PID/ns/$NS)
  APP_NS=$(readlink /proc/$APP_PID/ns/$NS)
  echo "  Sandbox:     $SANDBOX_NS"
  echo "  Application: $APP_NS"
  if [ "$SANDBOX_NS" = "$APP_NS" ]; then
    echo "  Status: SHARED ✓"
  else
    echo "  Status: ISOLATED ✗"
  fi
  echo
done
```

**What this comprehensive loop demonstrates:**

This loop compares **all major namespace IDs** between the sandbox (pause) container and the application container, showing the complete picture of **shared** vs **isolated** namespaces:

1. **`for NS in net uts ipc pid mnt`**: Loops through all key namespaces used by containers
   - `net` = Network namespace (IP, interfaces, routing)
   - `uts` = Unix Timesharing namespace (hostname, domain)  
   - `ipc` = Inter-process communication namespace (shared memory, semaphores)
   - `pid` = Process ID namespace (process isolation)
   - `mnt` = Mount namespace (filesystem views, mount points)

2. **Comparison Logic**: Captures both namespace IDs and compares them
3. **Status Indication**: Shows "SHARED ✓" or "ISOLATED ✗" for each namespace type

**Expected Output:**
```
[net namespace]
  Sandbox:     net:[4026532517]
  Application: net:[4026532517]
  Status: SHARED ✓

[uts namespace]  
  Sandbox:     uts:[4026532516]
  Application: uts:[4026532516]
  Status: SHARED ✓

[ipc namespace]
  Sandbox:     ipc:[4026532514]
  Application: ipc:[4026532514]
  Status: SHARED ✓

[pid namespace]
  Sandbox:     pid:[4026532515]
  Application: pid:[4026532518]
  Status: ISOLATED ✗

[mnt namespace]
  Sandbox:     mnt:[4026532519]
  Application: mnt:[4026532521]
  Status: ISOLATED ✗
```

**Complete Kubernetes Pod Namespace Architecture:**
- **SHARED namespaces** (net, uts, ipc): Enable pod-level networking, hostname, and IPC
- **ISOLATED namespaces** (pid, mnt): Provide container-level process and filesystem isolation
- This selective sharing vs isolation is the **core design of Kubernetes pods**



#### 5.4 Observe from Inside the Pod
From inside `demo-pod`:
```bash
kubectl exec -it demo-pod -- sh -c 'readlink /proc/self/ns/net; readlink /proc/self/ns/ipc; readlink /proc/self/ns/uts'
```
Compare with infra container namespace IDs collected via `crictl` – they match.

#### 5.4.1 Pod Architecture Diagram

The following diagram illustrates how a Kubernetes pod is constructed using Linux namespaces and the pause container:

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                KUBERNETES POD                                    │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────────────┐                    ┌─────────────────────┐            │
│  │   PAUSE CONTAINER   │                    │ APPLICATION CONTAINER│            │
│  │   (Pod Sandbox)     │                    │     (nginx)          │            │
│  │                     │                    │                     │            │
│  │ PID: 1234          │◄────────────────►  │ PID: 5678           │            │
│  │ Image: pause:3.9   │  SHARES NAMESPACES │ Image: nginx:latest │            │
│  │                     │                    │                     │            │
│  │ ┌─────────────────┐ │                    │ ┌─────────────────┐ │            │
│  │ │ NAMESPACES      │ │                    │ │ NAMESPACES      │ │            │
│  │ │ net:[4026532517]│ │◄──── SHARED ─────► │ │ net:[4026532517]│ │            │
│  │ │ uts:[4026532516]│ │◄──── SHARED ─────► │ │ uts:[4026532516]│ │            │
│  │ │ ipc:[4026532514]│ │◄──── SHARED ─────► │ │ ipc:[4026532514]│ │            │
│  │ │ pid:[4026532515]│ │                    │ │ pid:[4026532518]│ │◄─ ISOLATED │
│  │ │ mnt:[4026532519]│ │                    │ │ mnt:[4026532521]│ │◄─ ISOLATED │
│  │ └─────────────────┘ │                    │ └─────────────────┘ │            │
│  └─────────────────────┘                    └─────────────────────┘            │
│                                                                                 │
├─────────────────────────────────────────────────────────────────────────────────┤
│                              SHARED RESOURCES                                   │
│  • Same IP Address: 10.244.1.15                                               │
│  • Same Hostname: demo-pod-abc123                                             │
│  • Same Network Interfaces: eth0, lo                                          │
│  • Shared Memory & Semaphores (IPC)                                           │
│  • Localhost Communication Between Containers                                  │
├─────────────────────────────────────────────────────────────────────────────────┤
│                             ISOLATED RESOURCES                                 │
│  • Separate Process Trees (each sees own PID 1)                               │
│  • Separate Filesystem Views                                                   │
│  • Independent /proc, /sys, mount points                                       │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│                            CONTAINER RUNTIME LAYER                             │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│              containerd-shim (PID: 999)                                       │
│                       │                                                        │
│          ┌────────────┴────────────┐                                          │
│          │                         │                                          │
│     pause (PID: 1234)         nginx (PID: 5678)                              │
│   (Namespace Holder)         (Application Process)                            │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│                                 HOST NODE                                       │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  • Host PID Namespace: [4026531836]                                           │
│  • Host Network: eth0, bridges, iptables rules                                │
│  • CNI Plugin: Creates veth pair, assigns Pod IP                              │
│  • kubelet: Orchestrates pod creation via CRI                                 │
│  • containerd: Manages container lifecycle                                     │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

**Key Architecture Points:**

1. **Pause Container Purpose**: Acts as the "namespace anchor" that creates and holds shared namespaces
2. **Selective Sharing**: Network, UTS, and IPC namespaces are shared; PID and mount are isolated
3. **Container Runtime**: containerd-shim manages both pause and application containers as separate processes
4. **Pod-Level Networking**: Single IP address shared by all containers via shared network namespace
5. **Process Isolation**: Each container has its own process tree despite namespace sharing

**This design enables:**
- **Tight Coupling**: Containers in a pod can communicate via localhost and shared memory
- **Security Isolation**: Containers cannot interfere with each other's processes or filesystem
- **Resource Efficiency**: Shared networking eliminates the need for inter-container networking overhead
- **Atomic Deployment**: Pod as the smallest deployable unit ensures containers are co-located

#### 5.5 CNI & Network Plumbing Glance
On the node:
```bash
ip link | grep -E "eth0|veth"
crictl inspectp $POD_ID | jq '.info.runtimeSpec.linux.devices?|length'
iptables -t nat -S | grep -i kubernetes | head -10   # (may vary by CNI)
```
The pod gets one side of a veth pair (`eth0` inside pod). The other side sits in the host netns attached to a bridge (e.g. `cni0`) or an overlay device.

#### 5.6 PID Namespace Sharing (Optional Demo)
Enable in a new pod spec:
```bash
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata: { name: shared-pid-demo }
spec:
  shareProcessNamespace: true  # EXCEPTION: Forces all containers to share ONE PID namespace
  containers:
  - name: one
    image: nicolaka/netshoot
    command: ["sleep","300"]
  - name: two
    image: nicolaka/netshoot
    command: ["sleep","300"]
EOF
kubectl exec -it shared-pid-demo -c one -- ps -ef | head
kubectl exec -it shared-pid-demo -c two -- ps -ef | head
# Now both containers will see ALL processes from BOTH containers (shared PID namespace)
```
You’ll now see both containers’ processes because they share the PID namespace.

#### 5.7 Recap
| Layer | Component | Role |
|-------|-----------|------|
| API | Pod object | Desired state stored in etcd |
| Scheduler | Binds pod to node | Decides placement |
| Kubelet | Pod manager | Orchestrates CRI calls |
| CRI Runtime | containerd/CRI-O | Creates sandbox + containers |
| Infra (pause) container | Namespace anchor | Holds net/ipc/uts, minimal process |
| Workload containers | Your images | Join infra namespaces |

The **infra container glues shared namespaces**; removing it would tear down the network namespace and thus the pod.

> Use `nsenter-test` ONLY for node-level investigation. Use normal pods + `crictl` to understand pod internals safely.


### 6. Advanced Infrastructure Commands

#### Node and Cluster Context
```bash
# Show which node the pod is running on
kubectl get pod demo-pod -o wide

# Get node details where pod is running
NODE=$(kubectl get pod demo-pod -o jsonpath='{.spec.nodeName}')
kubectl describe node $NODE

# Show all pods on the same node
kubectl get pods --all-namespaces -o wide --field-selector spec.nodeName=$NODE
```

#### Pod Networking Deep Dive
```bash
# Get pod IP address
POD_IP=$(kubectl get pod demo-pod -o jsonpath='{.status.podIP}')
echo "Pod IP: $POD_IP"

# Test pod connectivity from another pod
kubectl run debug-pod2 --image=nicolaka/netshoot -it --rm -- /bin/sh
# Inside debug pod: ping $POD_IP, curl $POD_IP, nslookup, dig, etc.

```

#### Linux Namespace Exploration
```bash
# Show process namespaces (this is KEY to understanding container isolation)
kubectl exec -it demo-pod -- ls -la /proc/self/ns/

# Compare namespaces between pods
kubectl exec -it debug-pod -- ls -la /proc/self/ns/

# Show container limits (cgroups)
kubectl exec -it demo-pod -- cat /sys/fs/cgroup/memory/memory.limit_in_bytes 2>/dev/null || echo "cgroup v2"

# Show container process limits
kubectl exec -it demo-pod -- ulimit -a
```

##### Understanding Namespace Output

The `/proc/self/ns/` command shows Linux namespaces - the core technology that provides container isolation. Here's how to interpret the output:

**Example Output:**
```
lrwxrwxrwx 1 root root 0 Aug 16 10:30 cgroup -> 'cgroup:[4026532513]'
lrwxrwxrwx 1 root root 0 Aug 16 10:30 ipc -> 'ipc:[4026532514]'
lrwxrwxrwx 1 root root 0 Aug 16 10:30 mnt -> 'mnt:[4026532512]'
lrwxrwxrwx 1 root root 0 Aug 16 10:30 net -> 'net:[4026532517]'
lrwxrwxrwx 1 root root 0 Aug 16 10:30 pid -> 'pid:[4026532515]'
lrwxrwxrwx 1 root root 0 Aug 16 10:30 user -> 'user:[4026531837]'
lrwxrwxrwx 1 root root 0 Aug 16 10:30 uts -> 'uts:[4026532516]'
```

**Namespace Types Explained:**

| Namespace | Purpose | Container Isolation Effect |
|-----------|---------|---------------------------|
| **pid** | Process ID isolation | Each container sees its own process tree starting from PID 1 |
| **net** | Network isolation | Each pod gets its own IP, network interfaces, routing table |
| **mnt** | Mount/filesystem isolation | Each container has its own filesystem view and mount points |
| **ipc** | Inter-process communication | Shared memory, semaphores isolated between containers |
| **uts** | Unix Timesharing System | Each container can have its own hostname |
| **user** | User ID isolation | Map container users to different host users |
| **cgroup** | Control group isolation | Resource limits (CPU, memory) enforcement |

**Key Insights for Engineers:**

1. **Different Numbers = Different Namespaces**: Each number (e.g., `[4026532515]`) represents a unique namespace instance
2. **Same Numbers = Shared Namespace**: Containers with the same namespace number share that resource
3. **Pod Containers Share Most Namespaces**: All containers in a pod share net, ipc, and uts namespaces
4. **Compare with Host**: Run `ls -la /proc/self/ns/` on the host node to see different numbers

**Practical Commands to Explore:**
```bash
# See the actual namespace numbers for comparison
kubectl exec -it demo-pod -- readlink /proc/self/ns/pid
kubectl exec -it debug-pod -- readlink /proc/self/ns/pid

# Check if containers share network namespace (they should in same pod)
kubectl exec -it demo-pod -- readlink /proc/self/ns/net
kubectl exec -it debug-pod -- readlink /proc/self/ns/net

# Compare hostname isolation
kubectl exec -it demo-pod -- hostname
kubectl exec -it debug-pod -- hostname
```

##### Multi-Container Pod Namespace Demo

Deploy a pod with two containers (both with full tools) to see how they share namespaces:

```bash
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: shared-namespace-pod
spec:
  containers:
  - name: netshoot
    image: nicolaka/netshoot
    command: ['sleep', '3600']
  - name: alpine
    image: alpine
    command: ['sleep', '3600']
EOF
```

**Wait for pod to be ready, then explore shared namespaces:**

```bash
# Check pod status
kubectl get pod shared-namespace-pod

# Compare namespaces between containers in the SAME pod
echo "=== NETSHOOT Container Namespaces ==="
kubectl exec -it shared-namespace-pod -c netshoot -- ls -la /proc/self/ns/

echo "=== ALPINE Container Namespaces ==="
kubectl exec -it shared-namespace-pod -c alpine -- ls -la /proc/self/ns/

# Extract just the namespace numbers for easy comparison
echo "=== Namespace ID Comparison ==="
echo "NETSHOOT net namespace:"
kubectl exec -it shared-namespace-pod -c netshoot -- readlink /proc/self/ns/net

echo "ALPINE net namespace:"
kubectl exec -it shared-namespace-pod -c alpine -- readlink /proc/self/ns/net

echo "NETSHOOT ipc namespace:"
kubectl exec -it shared-namespace-pod -c netshoot -- readlink /proc/self/ns/ipc

echo "ALPINE ipc namespace:"
kubectl exec -it shared-namespace-pod -c alpine -- readlink /proc/self/ns/ipc

echo "NETSHOOT uts namespace:"
kubectl exec -it shared-namespace-pod -c netshoot -- readlink /proc/self/ns/uts

echo "ALPINE uts namespace:"
kubectl exec -it shared-namespace-pod -c alpine -- readlink /proc/self/ns/uts

# Compare PID namespaces (should be DIFFERENT)
echo "NETSHOOT pid namespace:"
kubectl exec -it shared-namespace-pod -c netshoot -- readlink /proc/self/ns/pid

echo "ALPINE pid namespace:"
kubectl exec -it shared-namespace-pod -c alpine -- readlink /proc/self/ns/pid
```

**What you'll observe:**

1. **SAME Network Namespace**: Both containers will show identical `net:[XXXXXXX]` numbers
   - They share the same IP address and network interfaces
   - They can communicate via `localhost`

2. **SAME IPC Namespace**: Both containers will show identical `ipc:[XXXXXXX]` numbers
   - They can share memory segments and semaphores

3. **SAME UTS Namespace**: Both containers will show identical `uts:[XXXXXXX]` numbers
   - They share the same hostname

4. **DIFFERENT PID/Mount Namespaces**: Each container has its own process tree and filesystem view

**Practical verification with full toolsets:**

```bash
# Both containers see the same hostname
kubectl exec -it shared-namespace-pod -c netshoot -- hostname
kubectl exec -it shared-namespace-pod -c alpine -- hostname

# Both containers share the same network interface
kubectl exec -it shared-namespace-pod -c netshoot -- ip addr show
kubectl exec -it shared-namespace-pod -c alpine -- ip addr show

# Both can see the same network statistics (netshoot has superior networking tools)
kubectl exec -it shared-namespace-pod -c netshoot -- netstat -i
kubectl exec -it shared-namespace-pod -c netshoot -- ss -tuln

# But they have different process trees (different PID namespaces within the pod)
# *** KEY POINT: Each container has its OWN PID namespace by default ***
kubectl exec -it shared-namespace-pod -c netshoot -- ps aux
kubectl exec -it shared-namespace-pod -c alpine -- ps aux

# Each sees different init process (PID 1) - proving separate PID namespaces
kubectl exec -it shared-namespace-pod -c netshoot -- cat /proc/1/comm
kubectl exec -it shared-namespace-pod -c alpine -- cat /proc/1/comm

# Verify PID namespace isolation - each container thinks it's PID 1
kubectl exec -it shared-namespace-pod -c netshoot -- sh -c 'echo "My PID: $$"; cat /proc/1/comm'
kubectl exec -it shared-namespace-pod -c alpine -- sh -c 'echo "My PID: $$"; cat /proc/1/comm'

# Both containers can use localhost to communicate (same network namespace)
# Method 1: Start HTTP server in background inside the container
kubectl exec -it shared-namespace-pod -c alpine -- sh -c 'echo "Hello from alpine" > /tmp/index.html' 

# in a different terminal, start a simple HTTP server
kubectl exec -it shared-namespace-pod -c alpine -- sh 
httpd -p 8080 -h /tmp 

# back to original terminal
# Verify the server is running
kubectl exec -it shared-namespace-pod -c alpine -- ps aux

# Access it from netshoot container using localhost and superior networking tools
kubectl exec -it shared-namespace-pod -c netshoot -- curl localhost:8080
kubectl exec -it shared-namespace-pod -c netshoot -- wget -qO- localhost:8080

```

**Advanced namespace exploration (both containers have tools):**

```bash
# Compare mount namespaces (should be different)
kubectl exec -it shared-namespace-pod -c netshoot -- mount | head -5
kubectl exec -it shared-namespace-pod -c alpine -- mount | head -5

# Check process isolation - each container only sees its own processes
kubectl exec -it shared-namespace-pod -c netshoot -- ps aux | wc -l
kubectl exec -it shared-namespace-pod -c alpine -- ps aux | wc -l

# Network namespace verification - same interfaces, same IP (netshoot has advanced tools)
kubectl exec -it shared-namespace-pod -c netshoot -- ip route
kubectl exec -it shared-namespace-pod -c alpine -- ip route

# Use netshoot's advanced networking tools for deeper analysis
kubectl exec -it shared-namespace-pod -c netshoot -- nslookup kubernetes.default
kubectl exec -it shared-namespace-pod -c netshoot -- dig kubernetes.default.svc.cluster.local
kubectl exec -it shared-namespace-pod -c netshoot -- tcpdump -i any -c 5
```

**Key Infrastructure Insight:**
- **Pod = Shared Network/IPC/UTS + Separate PID/Mount per container**
- This is why pods are considered the "atomic unit" - containers in a pod are tightly coupled
- Compare this to separate pods which have completely different namespace numbers

### 7. Pod Lifecycle Management

```bash
# Get pod events and troubleshooting info
kubectl get events --field-selector involvedObject.name=demo-pod

# Follow pod logs
kubectl logs -f demo-pod

# Get previous container logs (if pod restarted)
kubectl logs demo-pod --previous

# Port forward to access pod (like SSH tunnel)
kubectl port-forward demo-pod 8080:80
# Then visit http://localhost:8080
```

### 8. Multi-Container Pod Example

```bash
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: multi-container-pod
spec:
  containers:
  - name: nginx
    image: nginx:latest
    ports:
    - containerPort: 80
  - name: sidecar
    image: nicolaka/netshoot
    command: ['sh', '-c', 'while true; do echo "Sidecar running"; sleep 30; done']
EOF

# Access specific container in multi-container pod
kubectl exec -it multi-container-pod -c nginx -- /bin/bash
kubectl exec -it multi-container-pod -c sidecar -- /bin/sh

# Show logs from specific container
kubectl logs multi-container-pod -c sidecar
```

## PID Namespace Summary

**Answer: YES, each container has its own PID namespace by default!**

| Scenario | PID Namespace Behavior | What Containers See |
|----------|----------------------|-------------------|
| **Default Pod** | Each container = separate PID namespace | Each container sees only its own processes, each has its own PID 1 |
| **shareProcessNamespace: true** | All containers = shared PID namespace | All containers see all processes from all containers in the pod |

**Verification Commands:**
```bash
# Default behavior - each container has separate PID namespace
kubectl exec -it shared-namespace-pod -c netshoot -- ps aux | wc -l
kubectl exec -it shared-namespace-pod -c alpine -- ps aux | wc -l
# Different counts = separate PID namespaces

# PID namespace sharing enabled - all containers share one PID namespace  
kubectl exec -it shared-pid-demo -c one -- ps aux | wc -l
kubectl exec -it shared-pid-demo -c two -- ps aux | wc -l
# Same counts = shared PID namespace
```

### 9. Cleanup

```bash
# Delete the demo pods
kubectl delete pod demo-pod
kubectl delete pod debug-pod
kubectl delete pod shared-namespace-pod
kubectl delete pod multi-container-pod

# Verify deletion
kubectl get pods
```

## Key Takeaways for Infrastructure Engineers

1. **Pod ≈ Lightweight VM**: Pods provide process/network isolation like VMs but share the host kernel
2. **Linux Namespaces**: Pods use PID, network, mount, and IPC namespaces for isolation
3. **Cgroups**: Resource limits are enforced using Linux cgroups
4. **Shared Fate**: All containers in a pod are scheduled together and share the same lifecycle
5. **Networking**: Each pod gets its own IP address, containers within a pod communicate via localhost
6. **Storage**: Containers in a pod can share volumes (similar to shared directories)

## Comparison: Pod vs VM vs Container

| Aspect | Traditional VM | Docker Container | Kubernetes Pod |
|--------|---------------|------------------|----------------|
| Isolation | Hardware virtualization | Process isolation | Process isolation + orchestration |
| Resource overhead | High (full OS) | Low (shared kernel) | Low (shared kernel) |
| Startup time | Minutes | Seconds | Seconds |
| Networking | Virtual NIC | Host or bridge network | Cluster-wide IP |
| Storage | Virtual disks | Bind mounts/volumes | Persistent volumes |
| Orchestration | Manual/scripts | Docker Compose | Kubernetes |