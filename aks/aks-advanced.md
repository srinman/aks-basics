# AKS Architecture Component Mapping

This document provides a comprehensive mapping table showing how OSS Kubernetes components are implemented in Azure Kubernetes Service (AKS), detailing the relationship between upstream Kubernetes and Azure-specific implementations.

## 📋 OSS Kubernetes ↔ AKS Component Mapping

| OSS Kubernetes Component | AKS Implementation | Repository/Source | Implementation Method | Implementation Details |
|---------------------------|--------------------|--------------------|----------------------|------------------------|
| **Control Plane Components** | | | | |
| **kube-apiserver** | Azure-managed API Server | Azure Platform | **Azure Platform Service** | • Managed by Azure control plane<br/>• Horizontal scaling handled by Azure<br/>• No direct access to kube-apiserver processes<br/>• Exposed via Azure Load Balancer |
| **etcd** | Azure-managed etcd | Azure Platform | **Azure Platform Service** | • Fully managed by Azure<br/>• Backup and restore handled by Azure<br/>• High availability across Azure availability zones<br/>• No customer access to etcd cluster |
| **kube-scheduler** | Azure-managed Scheduler | Azure Platform | **Azure Platform Service** | • Standard Kubernetes scheduler<br/>• Enhanced with Azure-specific scheduling logic<br/>• Integrates with Azure VM availability sets and zones<br/>• Supports Azure spot instances |
| **kube-controller-manager** | Azure-managed Controller Manager | Azure Platform | **Azure Platform Service** | • Standard Kubernetes controllers<br/>• Enhanced with Azure cloud-specific controllers<br/>• Node lifecycle management integrated with Azure VM operations<br/>• PersistentVolume controller integrated with Azure storage |
| **cloud-controller-manager** | Azure Cloud Controller Manager | [`kubernetes-sigs/cloud-provider-azure`](https://github.com/kubernetes-sigs/cloud-provider-azure) | **Deployment** | • Implements cloud-specific control logic<br/>• **Image**: `mcr.microsoft.com/oss/kubernetes/azure-cloud-controller-manager`<br/>• **Controllers**: Node, Route, Service (LoadBalancer)<br/>• **Version**: v1.32.3+ (matches AKS versions)<br/>• **Integration**: Native Azure API integration for VMs, Load Balancers, NSGs |
| **Node Components** | | | | |
| **kubelet** | Standard kubelet | Kubernetes upstream | **systemd service** | • Standard Kubernetes kubelet<br/>• Azure-specific configuration for IMDS integration<br/>• Container runtime: containerd<br/>• Integrated with Azure Monitor for metrics collection |
| **kube-proxy** | Standard kube-proxy | Kubernetes upstream | **DaemonSet** | • Standard Kubernetes kube-proxy<br/>• iptables or ipvs mode supported<br/>• Integrates with Azure networking (kubenet/CNI)<br/>• Service load balancing handled by Azure Load Balancer |
| **Container Runtime** | containerd | containerd.io | **systemd service** | • Default: containerd (CRI-compliant)<br/>• Windows: containerd or docker (deprecated)<br/>• Runtime class support for different workload types<br/>• Integration with Azure Container Registry (ACR) |
| **Storage Components** | | | | |
| **CSI Driver (Azure Disk)** | Azure Disk CSI Driver | [`kubernetes-sigs/azuredisk-csi-driver`](https://github.com/kubernetes-sigs/azuredisk-csi-driver) | **DaemonSet + Deployment** | • Native CSI implementation<br/>• **Image**: `mcr.microsoft.com/oss/v2/kubernetes-csi/azuredisk-csi`<br/>• **Version**: v1.33.5+ (latest)<br/>• **Features**: Dynamic provisioning, snapshots, resize<br/>• **Storage Types**: Premium SSD, Standard SSD, Ultra Disk, Premium SSD v2 |
| **CSI Driver (Azure File)** | Azure File CSI Driver | [`kubernetes-sigs/azurefile-csi-driver`](https://github.com/kubernetes-sigs/azurefile-csi-driver) | **DaemonSet + Deployment** | • Native CSI implementation for Azure Files<br/>• ReadWriteMany support for shared storage<br/>• NFS and SMB protocol support<br/>• Integration with Azure AD for authentication |
| **Networking Components** | | | | |
| **CNI Plugin (Basic)** | kubenet | Kubernetes upstream | **Host Binary** | • Default networking: kubenet<br/>• Pod CIDR: 10.244.0.0/16 (default)<br/>• Node-to-pod communication via Azure routes<br/>• Limited to 400 nodes per cluster |
| **CNI Plugin (Advanced)** | Azure CNI | [`Azure/azure-container-networking`](https://github.com/Azure/azure-container-networking) | **Host Binary + DaemonSet** | • Azure-native networking plugin<br/>• Pods get Azure VNet IPs directly<br/>• Integration with Azure Virtual Network<br/>• Support for Network Policies |
| **Network Policy** | Azure Network Policies / Calico | Azure CNI + Calico | **DaemonSet** | • Azure-native network policies (Azure CNI)<br/>• Calico for advanced policy management<br/>• Integration with Azure Firewall and NSGs |
| **DNS** | CoreDNS | CoreDNS upstream | **Deployment** | • Standard CoreDNS with Azure-specific configuration<br/>• Integration with Azure Private DNS zones<br/>• Custom DNS forwarding to Azure DNS |
| **Monitoring & Observability** | | | | |
| **Metrics Server** | metrics-server | Kubernetes SIG Instrumentation | **Deployment** | • Standard metrics-server deployment<br/>• Integration with Azure Monitor<br/>• HPA/VPA metrics collection |
| **Azure Monitor Integration** | Azure Monitor Agent | Microsoft Azure | **DaemonSet** | • Container Insights for comprehensive monitoring<br/>• Log Analytics workspace integration<br/>• Prometheus metrics collection<br/>• Custom metrics and alerting |
| **Authentication & Authorization** | | | | |
| **Azure AD Integration** | Azure AD OIDC | Microsoft Azure AD | **Azure Platform Service** | • Native Azure AD integration for cluster authentication<br/>• RBAC with Azure AD users and groups<br/>• Managed identity integration<br/>• Workload identity (OIDC) support |
| **Azure RBAC** | Azure RBAC for Kubernetes | Microsoft Azure | **Azure Platform Service** | • Azure RBAC controls applied to Kubernetes resources<br/>• Fine-grained permissions using Azure roles<br/>• Integration with existing Azure IAM |
| **Service Mesh** | | | | |
| **Istio** | Azure Service Mesh (Istio) | Istio + Azure enhancements | **DaemonSet + Deployment** | • Managed Istio add-on (preview)<br/>• Integration with Azure Application Gateway<br/>• Azure Monitor integration for service mesh metrics |
| **Add-ons & Extensions** | | | | |
| **Ingress Controller** | Multiple Options | Various | **Deployment** | • **Application Gateway Ingress Controller (AGIC)**<br/>• **NGINX Ingress Controller**<br/>• **Traefik**, **HAProxy**, etc.<br/>• Integration with Azure Application Gateway |
| **Cluster Autoscaler** | AKS Cluster Autoscaler | [`kubernetes/autoscaler`](https://github.com/kubernetes/autoscaler) | **Deployment** | • Standard cluster-autoscaler with Azure provider<br/>• Integration with Azure VM Scale Sets<br/>• Node pool scaling (1-1000 nodes)<br/>• Multiple node pools support |
| **Vertical Pod Autoscaler** | VPA | [`kubernetes/autoscaler`](https://github.com/kubernetes/autoscaler) | **Deployment** | • Standard VPA implementation<br/>• Integration with Azure Monitor metrics<br/>• Resource recommendation engine |

## 🔍 Implementation Method Details

### Deployment Types Explained

**Azure Platform Service**: Components fully managed by Azure control plane, no customer visibility or control

**systemd service**: Traditional Linux system services running directly on the host OS

**DaemonSet**: Kubernetes workload that ensures one pod runs on every (or selected) cluster node

**Deployment**: Standard Kubernetes workload with replica management and rolling updates

**Host Binary**: Binary executable installed directly on the host OS (typically in `/opt/cni/bin/`)

### Key Component Implementation Details

#### Cloud Controller Manager
**Repository**: https://github.com/kubernetes-sigs/cloud-provider-azure
- **Deployment Method**: Kubernetes Deployment (multiple replicas with leader election)
- **Binary**: `/usr/local/bin/cloud-controller-manager`
- **Image**: `mcr.microsoft.com/oss/kubernetes/azure-cloud-controller-manager`
- **Namespace**: `kube-system`

**Key Implementation Files**:
```bash
cmd/cloud-controller-manager/controller-manager.go  # Main entry point
pkg/provider/azure.go                              # Azure cloud provider implementation
pkg/provider/azure_controller_*.go                 # Individual controller implementations
```

#### Azure Disk CSI Driver
**Repository**: https://github.com/kubernetes-sigs/azuredisk-csi-driver
- **Controller**: Deployment (csi-azuredisk-controller)
- **Node Plugin**: DaemonSet (csi-azuredisk-node)
- **Image**: `mcr.microsoft.com/oss/v2/kubernetes-csi/azuredisk-csi:v1.33.5`

**Key Implementation Details**:
```go
// From pkg/azuredisk/azuredisk.go
import "sigs.k8s.io/cloud-provider-azure/pkg/provider"

// Integration with cloud-provider-azure
driver.cloud = azure.GetCloudProvider(...)
```

#### Networking Components

**kubenet**: Standard Kubernetes networking with Azure route table integration
- **Method**: Host binary + kernel routing
- **Location**: `/opt/cni/bin/bridge`, `/opt/cni/bin/host-local`

**Azure CNI**: Azure-native networking plugin
- **Repository**: https://github.com/Azure/azure-container-networking
- **Method**: Host binary + DaemonSet for IP management

## 📊 Architecture Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        AKS Cluster Architecture                             │
└─────────────────────────────────────────────────────────────────────────────┘

Azure Control Plane (Fully Managed)
┌─────────────────────────────────────────────────────────────────────────────┐
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐ ┌─────────────┐ │
│  │  kube-apiserver │ │      etcd       │ │ kube-scheduler  │ │kube-ctrl-mgr│ │
│  │   (Azure)       │ │   (Azure)       │ │   (Azure)       │ │  (Azure)    │ │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘ └─────────────┘ │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │             Azure Cloud Controller Manager                              │ │
│  │       (kubernetes-sigs/cloud-provider-azure)                          │ │
│  │  • Node Controller  • Route Controller  • Service Controller          │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ Azure ARM API
                                    ▼
Azure Node Pools (Customer Managed)
┌─────────────────────────────────────────────────────────────────────────────┐
│  Node 1                    Node 2                    Node 3                 │
│  ┌─────────────────────┐   ┌─────────────────────┐   ┌─────────────────────┐ │
│  │     kubelet         │   │     kubelet         │   │     kubelet         │ │
│  │   kube-proxy        │   │   kube-proxy        │   │   kube-proxy        │ │
│  │   containerd        │   │   containerd        │   │   containerd        │ │
│  │                     │   │                     │   │                     │ │
│  │  ┌───────────────┐  │   │  ┌───────────────┐  │   │  ┌───────────────┐  │ │
│  │  │Azure Disk CSI │  │   │  │Azure Disk CSI │  │   │  │Azure Disk CSI │  │ │
│  │  │   Driver      │  │   │  │   Driver      │  │   │  │   Driver      │  │ │
│  │  └───────────────┘  │   │  └───────────────┘  │   │  └───────────────┘  │ │
│  │  ┌───────────────┐  │   │  ┌───────────────┐  │   │  ┌───────────────┐  │ │
│  │  │Azure File CSI │  │   │  │Azure File CSI │  │   │  │Azure File CSI │  │ │
│  │  │   Driver      │  │   │  │   Driver      │  │   │  │   Driver      │  │ │
│  │  └───────────────┘  │   │  └───────────────┘  │   │  └───────────────┘  │ │
│  └─────────────────────┘   └─────────────────────┘   └─────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 🎯 Key Implementation Insights

1. **Hybrid Deployment Model**: AKS uses a mix of Azure platform services (control plane), systemd services (node agents), and Kubernetes workloads (add-ons)

2. **Cloud Controller Manager**: Deployed as a standard Kubernetes Deployment with leader election, sourced from https://github.com/kubernetes-sigs/cloud-provider-azure

3. **CSI Pattern**: Storage drivers follow the standard CSI pattern with controller Deployments and node DaemonSets

4. **Node Agent Strategy**: Core node components (kubelet, containerd) run as systemd services for reliability and early startup

5. **Add-on Ecosystem**: Optional features like monitoring, ingress, and autoscaling are deployed as standard Kubernetes workloads

6. **Azure Integration Points**: All Azure-specific logic is encapsulated in dedicated components that integrate with Azure ARM APIs

---

## � Appendix: Node Controller Deep Dive

### OSS Kubernetes Node Controller Implementation

The node controller in upstream Kubernetes is part of the `kube-controller-manager` and handles several critical responsibilities:

#### Core Responsibilities

**1. Node Lifecycle Management**
- **CIDR Block Assignment**: Assigns CIDR blocks to nodes for pod networking
- **Cloud Provider Integration**: Syncs node list with cloud provider APIs
- **Node Registration**: Validates and processes new node registrations

**2. Health Monitoring**
- **Heartbeat Mechanism**: Monitors node status updates and lease renewals
- **Status Updates**: Processes `NodeStatus` updates from kubelet every ~10 seconds
- **Lease Objects**: Tracks `kube-node-lease` namespace lease renewals for faster failure detection

**3. Eviction Policies**
- **Rate Limiting**: Uses `--node-eviction-rate` (default 0.1/sec) to prevent thundering herd
- **Zone Awareness**: Applies different eviction rates based on availability zones
- **Grace Periods**: Respects pod termination grace periods during eviction

#### Key Configuration Parameters

```yaml
# OSS Kubernetes Node Controller Configuration
--node-monitor-period=5s                    # How often to check node status
--node-monitor-grace-period=40s              # Grace period before marking node unhealthy
--pod-eviction-timeout=5m                   # Time to wait before evicting pods
--node-eviction-rate=0.1                    # Rate of node evictions per second
--secondary-node-eviction-rate=0.01         # Rate for unhealthy zones
--large-cluster-size-threshold=50           # Threshold for large cluster behavior
--unhealthy-zone-threshold=0.55             # Percentage of unhealthy nodes in zone
```

#### Node Status Conditions

```yaml
# Example Node Conditions
conditions:
- type: Ready
  status: "True"
  reason: KubeletReady
- type: MemoryPressure
  status: "False"
  reason: KubeletHasSufficientMemory
- type: DiskPressure
  status: "False"
  reason: KubeletHasNoDiskPressure
- type: PIDPressure
  status: "False"
  reason: KubeletHasSufficientPID
- type: NetworkUnavailable
  status: "False"
  reason: RouteCreated
```

### AKS Node Controller Implementation

In AKS, node controller functionality is split between multiple components that integrate with Azure infrastructure:

#### 1. Azure Cloud Controller Manager (Node Controller)

**Repository**: [`kubernetes-sigs/cloud-provider-azure`](https://github.com/kubernetes-sigs/cloud-provider-azure)

**Implementation Location**: `cmd/cloud-controller-manager/app/core.go`

```go
// Key implementation: startCloudNodeLifecycleController
func startCloudNodeLifecycleController(
    ctx context.Context, 
    controllerContext genericcontrollermanager.ControllerContext, 
    completedConfig *cloudcontrollerconfig.CompletedConfig, 
    cloud cloudprovider.Interface
) (http.Handler, bool, error) {
    
    cloudNodeLifecycleController, err := nodelifecyclecontroller.NewCloudNodeLifecycleController(
        completedConfig.SharedInformers.Core().V1().Nodes(),
        completedConfig.ClientBuilder.ClientOrDie("node-controller"),
        cloud,
        completedConfig.ComponentConfig.KubeCloudShared.NodeMonitorPeriod.Duration,
    )
    
    go cloudNodeLifecycleController.Run(ctx, controllerContext.ControllerManagerMetrics)
    return nil, true, nil
}
```

**AKS-Specific Features**:
- **Azure VM Integration**: Direct integration with Azure VM APIs for node status
- **Azure Resource Locking**: Uses lease-based locking to coordinate with AKS Resource Provider
- **Zone Awareness**: Leverages Azure Availability Zone information for intelligent eviction
- **VMSS Integration**: Special handling for Virtual Machine Scale Set nodes

#### 2. Azure Cloud Node Manager

**Repository**: [`kubernetes-sigs/cloud-provider-azure`](https://github.com/kubernetes-sigs/cloud-provider-azure)

**Binary**: `azure-cloud-node-manager`
**Image**: `mcr.microsoft.com/oss/kubernetes/azure-cloud-node-manager`
**Deployment**: DaemonSet on each node

**Implementation Location**: `cmd/cloud-node-manager/app/nodemanager.go`

```go
// Key implementation: CloudNodeController
type CloudNodeController struct {
    nodeName      string
    waitForRoutes bool
    nodeProvider  NodeProvider
    nodeInformer  coreinformers.NodeInformer
    kubeClient    clientset.Interface
    recorder      record.EventRecorder
    
    nodeStatusUpdateFrequency time.Duration
    labelReconcileInfo []labelReconcile
    enableBetaTopologyLabels bool
}
```

**Node Provider Implementations**:

1. **IMDS Node Provider** (Default):
   ```go
   // pkg/node/node.go - IMDSNodeProvider
   func (np *IMDSNodeProvider) GetNodeAddresses(ctx context.Context, nodeName types.NodeName) ([]v1.NodeAddress, error) {
       // Uses Azure Instance Metadata Service (IMDS)
       // Endpoint: http://169.254.169.254/metadata/instance
   }
   ```

2. **ARM Node Provider** (Alternative):
   ```go
   // pkg/node/nodearm.go - ARMNodeProvider  
   func (np *ARMNodeProvider) GetNodeAddresses(ctx context.Context, nodeName types.NodeName) ([]v1.NodeAddress, error) {
       // Uses Azure Resource Manager APIs
       // Requires explicit cloud configuration
   }
   ```

#### 3. AKS Node Management Features

**Enhanced Node Lifecycle**:

```yaml
# AKS Node Labels (Auto-Applied)
labels:
  topology.kubernetes.io/region: eastus
  topology.kubernetes.io/zone: eastus-1
  node.kubernetes.io/instance-type: Standard_D2s_v3
  kubernetes.azure.com/agentpool: nodepool1
  kubernetes.azure.com/cluster: aks-cluster-name
  kubernetes.azure.com/node-image-version: AKSUbuntu-1804gen2
  kubernetes.azure.com/os-sku: Ubuntu
  kubernetes.io/arch: amd64
  kubernetes.io/os: linux
  
# AKS-Specific Taints
taints:
- key: kubernetes.azure.com/scalesetpriority
  value: spot
  effect: NoSchedule  # For spot instances
```

**Node Status Updates**:

```go
// Enhanced with Azure-specific information
func (cnc *CloudNodeController) UpdateNodeStatus(ctx context.Context) {
    // Standard Kubernetes node status
    // + Azure VM metadata
    // + Network interface information  
    // + Availability zone details
    // + VM size and SKU information
}
```

#### 4. Integration with Azure Infrastructure

**Azure Resource Manager Integration**:
```go
// Direct Azure VM API calls for node management
func (az *Cloud) GetNodeByProviderID(ctx context.Context, providerID string) (*v1.Node, error) {
    // Calls Azure Compute REST API
    // /subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Compute/virtualMachines/{vmName}
}
```

**Lease Management**:
```go
// Azure-specific resource locking
const (
    AzureResourceLockLeaseName = "aks-managed-resource-locker"
    AzureResourceLockLeaseNamespace = "kube-system"  
    AzureResourceLockLeaseDuration = int32(15 * 60) // 15 minutes
)
```

### Key Differences: OSS vs AKS Node Controller

| Aspect | OSS Kubernetes | AKS Implementation |
|--------|----------------|-------------------|
| **Deployment** | Part of kube-controller-manager | Split: Cloud Controller Manager + Node Manager DaemonSet |
| **Node Discovery** | Kubelet self-registration | Azure VM API + IMDS integration |
| **Metadata Source** | Kubelet-reported only | Azure VM metadata + Kubelet |
| **Eviction Logic** | Standard rate limiting | Azure zone-aware + AKS RP coordination |
| **Network Status** | Basic connectivity checks | Azure networking integration (VNet, NSG) |
| **Lease Objects** | Standard kube-node-lease | Enhanced with Azure resource locking |
| **Node Labels** | Basic topology labels | Rich Azure metadata labels |
| **Health Checks** | Kubelet heartbeat only | Kubelet + Azure VM status |

### Configuration Examples

**AKS Cloud Controller Manager**:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cloud-controller-manager
  namespace: kube-system
spec:
  replicas: 2
  selector:
    matchLabels:
      component: cloud-controller-manager
  template:
    spec:
      containers:
      - name: cloud-controller-manager
        image: mcr.microsoft.com/oss/kubernetes/azure-cloud-controller-manager:v1.32.3
        command:
        - cloud-controller-manager
        - --allocate-node-cidrs=true
        - --cloud-config=/etc/kubernetes/azure.json
        - --cloud-provider=azure
        - --cluster-cidr=10.244.0.0/16
        - --controllers=*,-cloud-node
        - --configure-cloud-routes=true
        - --leader-elect=true
        - --route-reconciliation-period=10s
        - --v=2
```

**AKS Cloud Node Manager**:
```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: cloud-node-manager
  namespace: kube-system
spec:
  selector:
    matchLabels:
      component: cloud-node-manager
  template:
    spec:
      containers:
      - name: cloud-node-manager
        image: mcr.microsoft.com/oss/kubernetes/azure-cloud-node-manager:v1.32.3
        command:
        - cloud-node-manager
        - --node-name=$(NODE_NAME)
        - --wait-routes=true
        env:
        - name: NODE_NAME
          valueFrom:
            fieldRef:
              fieldPath: spec.nodeName
```

---

## 📡 Appendix: Control Plane to Node Communication Deep Dive

### OSS Kubernetes Control Plane Communication Patterns

OSS Kubernetes follows a "hub-and-spoke" architecture where all API communication is centralized through the kube-apiserver:

#### Node to Control Plane Communication

**1. Primary Communication Path**
```bash
# All node communication goes through kube-apiserver
Node Components → kube-apiserver (Port 443/HTTPS)
├── kubelet → API Server (Node status, pod status, logs)
├── kube-proxy → API Server (Service/Endpoint updates)  
└── Pod ServiceAccounts → API Server (Kubernetes API calls)
```

**Security Mechanisms**:
- **TLS Authentication**: Nodes use client certificates for mutual TLS
- **Bootstrap Token**: Initial node registration and certificate requests
- **Service Account Tokens**: Pods use JWT tokens for API access
- **RBAC Authorization**: Role-based access control for all requests

**Kubelet TLS Bootstrapping Process**:
```yaml
# 1. Initial Bootstrap Request
POST /api/v1/certificatesigningrequests
Authorization: Bearer <bootstrap-token>

# 2. Node Certificate Approval (auto-approved or manual)
kubectl certificate approve <csr-name>

# 3. Ongoing Communication with Client Certificate  
Authorization: X509 Client Certificate
```

#### Control Plane to Node Communication

**1. API Server to Kubelet**
```bash
# Direct HTTPS connections for:
kube-apiserver → kubelet:10250 (HTTPS)
├── kubectl exec → kubelet (pod execution)
├── kubectl logs → kubelet (log streaming)  
├── kubectl port-forward → kubelet (port forwarding)
└── Node status queries → kubelet (health checks)
```

**Security Considerations**:
- **Kubelet Certificate Authority**: `--kubelet-certificate-authority` for kubelet cert verification
- **Kubelet Authorization**: Enable `--authorization-mode=Webhook` on kubelet
- **Network Security**: Typically requires secure network or tunneling

**2. API Server to Pods/Services**
```bash
# Proxy connections (generally insecure)
kube-apiserver → Node:NodePort (HTTP/HTTPS)
├── kubectl proxy → Service endpoints
├── Direct pod access → Pod IPs
└── Service proxy → Service ClusterIPs
```

**3. SSH Tunnels (Deprecated)**
```bash
# Legacy secure communication method
kube-apiserver → SSH Server:22 → kubelet:10250
# Deprecated since Kubernetes v1.18
```

**4. Konnectivity Service (Modern Approach)**
```yaml
# Architecture Components
apiVersion: v1
kind: ConfigMap
metadata:
  name: konnectivity-server-conf
  namespace: kube-system
data:
  uds-name: "/etc/kubernetes/konnectivity-server/konnectivity-server.socket"
  cluster-cert: "/etc/kubernetes/pki/apiserver.crt"
  cluster-key: "/etc/kubernetes/pki/apiserver.key"
```

**Konnectivity Flow**:
```bash
# 1. Agents initiate connections from nodes
konnectivity-agent → konnectivity-server (Control Plane)

# 2. Server proxies API server requests through established tunnels
API Server → konnectivity-server → konnectivity-agent → kubelet
```

### AKS Control Plane Communication Implementation

AKS implements a sophisticated communication architecture that enhances the OSS Kubernetes model with Azure-specific optimizations:

#### AKS Communication Architecture Overview

```bash
┌─────────────────────────────────────────────────────────────────────────────┐
│                     AKS Control Plane (Azure Managed)                      │
│  ┌─────────────────┐    ┌──────────────────────────────────────────────┐   │
│  │  kube-apiserver │◄──►│          Konnectivity Server                │   │
│  │   (Multiple)    │    │      (Built-in, Azure Enhanced)            │   │
│  └─────────────────┘    └──────────────────────────────────────────────┘   │
└─────────────────────────────────┬───────────────────────────────────────────┘
                                  │ Secure Tunnels (Multiple)
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        AKS Node Pools (Customer VNet)                      │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    konnectivity-agent                              │   │
│  │              (DaemonSet on every node)                            │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────────────────┐   │
│  │     kubelet     │ │   kube-proxy    │ │    Azure Node Extensions    │   │
│  └─────────────────┘ └─────────────────┘ └─────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### 1. Enhanced Node to Control Plane Communication

**AKS Konnectivity Integration**:
```yaml
# AKS automatically deploys konnectivity-agent
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: konnectivity-agent
  namespace: kube-system
spec:
  template:
    spec:
      containers:
      - name: konnectivity-agent
        image: mcr.microsoft.com/oss/kubernetes/konnectivity-agent:v0.1.5
        command:
        - /proxy-agent
        args:
        - --logtostderr=true
        - --ca-cert=/var/lib/konnectivity-agent/ca.crt
        - --proxy-server-host=<aks-konnectivity-server-endpoint>
        - --proxy-server-port=8132
        - --admin-server-port=8133
        - --health-server-port=8134
        - --service-account-token-path=/var/run/secrets/tokens/konnectivity-agent-token
        volumeMounts:
        - name: konnectivity-agent-token
          mountPath: /var/run/secrets/tokens
          readOnly: true
```

**Multiple Communication Paths**:
```bash
# Primary: Konnectivity tunnel (for control plane initiated connections)
Node → konnectivity-agent → AKS Control Plane

# Direct: API Server access (for node initiated connections)  
kubelet → Azure Load Balancer → kube-apiserver
kube-proxy → Azure Load Balancer → kube-apiserver
Pods → Azure Load Balancer → kube-apiserver
```

**Azure-Enhanced Security**:
- **Azure AD Integration**: Node identity via managed identity
- **Azure Key Vault**: Certificate management and rotation
- **Azure Private Link**: Private API server endpoints
- **Azure Firewall**: Network-level security controls

#### 2. AKS API Server VNet Integration

**Traditional AKS Architecture**:
```bash
# Standard AKS (Legacy)
Node → Internet → Azure Load Balancer → API Server
          └─► Konnectivity tunnel for reverse communication
```

**API Server VNet Integration Architecture**:
```bash
# Modern AKS with VNet Integration
┌─────────────────────────────────────────────────────────────────────────┐
│                        Customer VNet                                   │
│  ┌──────────────────────┐    ┌──────────────────────────────────────┐  │
│  │   API Server Subnet  │    │         Node Subnet                  │  │
│  │   (Delegated /28)    │    │      (Customer managed)             │  │
│  │  ┌─────────────────┐ │    │  ┌─────────────────┐                │  │
│  │  │  API Server ILB │◄┼────┤  │      Nodes      │                │  │
│  │  │   (Private IP)  │ │    │  │   (Direct comm) │                │  │
│  │  └─────────────────┘ │    │  └─────────────────┘                │  │
│  └──────────────────────┘    └──────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
```

**Benefits of VNet Integration**:
- **No Tunneling Required**: Direct IP connectivity between nodes and API server
- **Reduced Latency**: Elimination of internet routing and tunnel overhead  
- **Enhanced Security**: All traffic remains within Azure private network
- **Simplified Networking**: No complex tunnel management or external dependencies

**Implementation Details**:
```yaml
# API Server VNet Integration Configuration
az aks create \
  --name myAKSCluster \
  --enable-apiserver-vnet-integration \
  --apiserver-subnet-id /subscriptions/.../subnets/apiserver-subnet \
  --vnet-subnet-id /subscriptions/.../subnets/node-subnet
```

#### 3. Communication Flow Analysis

**Standard AKS Communication Patterns**:

| Direction | Component | Protocol | Port | Path | Security |
|-----------|-----------|----------|------|------|----------|
| **Node → API** | kubelet | HTTPS | 443 | Azure LB → API Server | mTLS + Azure AD |
| **Node → API** | kube-proxy | HTTPS | 443 | Azure LB → API Server | Service Account JWT |
| **Pod → API** | Applications | HTTPS | 443 | Azure LB → API Server | Service Account JWT |
| **API → Node** | kubectl exec | HTTPS | 10250 | Konnectivity tunnel | mTLS over tunnel |
| **API → Node** | kubectl logs | HTTPS | 10250 | Konnectivity tunnel | mTLS over tunnel |
| **API → Node** | Admission webhooks | HTTPS | 443/8443 | Konnectivity tunnel | mTLS over tunnel |

**VNet Integration Communication Patterns**:

| Direction | Component | Protocol | Port | Path | Security |
|-----------|-----------|----------|------|------|----------|
| **Node → API** | kubelet | HTTPS | 443 | Direct IP (ILB) | mTLS + Azure AD |
| **Node → API** | kube-proxy | HTTPS | 443 | Direct IP (ILB) | Service Account JWT |
| **Pod → API** | Applications | HTTPS | 443 | Direct IP (ILB) | Service Account JWT |
| **API → Node** | kubectl exec | HTTPS | 10250 | Direct IP routing | mTLS |
| **API → Node** | kubectl logs | HTTPS | 10250 | Direct IP routing | mTLS |
| **API → Node** | Admission webhooks | HTTPS | 443/8443 | Direct IP routing | mTLS |

#### 4. Security and Network Policies

**Network Security Group (NSG) Rules for VNet Integration**:
```json
{
  "securityRules": [
    {
      "name": "AllowAPIServerToNodes", 
      "properties": {
        "protocol": "TCP",
        "sourceAddressPrefix": "172.16.0.0/28",  // API Server subnet
        "destinationAddressPrefix": "172.16.1.0/24", // Node subnet
        "destinationPortRanges": ["443", "4443"],
        "access": "Allow",
        "priority": 1000,
        "direction": "Inbound"
      }
    },
    {
      "name": "AllowAzureLBToAPIServer",
      "properties": {
        "protocol": "TCP", 
        "sourceAddressPrefix": "AzureLoadBalancer",
        "destinationAddressPrefix": "172.16.0.0/28",
        "destinationPortRange": "9988",
        "access": "Allow",
        "priority": 1001,
        "direction": "Inbound"
      }
    }
  ]
}
```

**Azure Private Link Integration**:
```bash
# Private Link Service for API Server access from external VNets
az network private-link-service create \
  --name aks-api-server-pls \
  --resource-group myRG \
  --subnet myAPIServerSubnet \
  --lb-frontend-ip-configs myAPIServerILBFrontend
```

#### 5. Troubleshooting Communication Issues

**Common Connection Problems**:

1. **Konnectivity Agent Issues**:
```bash
# Check agent status
kubectl get pods -n kube-system -l k8s-app=konnectivity-agent

# View agent logs
kubectl logs -n kube-system -l k8s-app=konnectivity-agent

# Common symptoms: kubectl exec/logs timeouts
```

2. **VNet Integration Issues**:
```bash
# Verify API server connectivity
kubectl get --raw /healthz

# Test direct IP connectivity
telnet <api-server-internal-lb-ip> 443

# Check NSG rules
az network nsg rule list --nsg-name <nsg-name> --resource-group <rg>
```

3. **Certificate Problems**:
```bash
# Check kubelet certificates
sudo journalctl -u kubelet -n 50

# Verify API server cert
openssl s_client -connect <api-server>:443 -servername kubernetes

# Check certificate expiration
kubectl get csr
```

**Performance Optimization**:

```bash
# Konnectivity scaling (for large clusters)  
konnectivity-server:
  --agent-port=8132
  --admin-port=8133  
  --health-port=8134
  --mode=grpc
  --proxy-strategies=destHost  # Route by destination
  --delete-existing-uds-file=true
```

### Key Differences: OSS vs AKS Communication

| Aspect | OSS Kubernetes | AKS Standard | AKS VNet Integration |
|--------|----------------|--------------|----------------------|
| **Node → API** | Direct HTTPS (unsecured network) | Azure LB + Internet routing | Direct private IP (no internet) |
| **API → Node** | SSH tunnels/Konnectivity (manual) | Managed Konnectivity (auto) | Direct IP routing (no tunnel) |
| **Network Path** | Cluster network only | Internet + Azure backbone | Private VNet only |
| **Security** | Manual TLS setup | Azure AD + managed certs | Azure AD + private network |
| **Performance** | Variable (network dependent) | Good (Azure backbone) | Excellent (direct routing) |
| **Complexity** | Manual configuration | Managed service | Managed + simplified networking |
| **Connectivity** | Public/Private manual setup | Public by default | Private by design |
| **Scalability** | Manual scaling | Auto-scaling components | Auto-scaling + direct routing |

### Configuration Examples

**Standard AKS with Enhanced Security**:
```yaml
# AKS with private cluster + authorized IP ranges
az aks create \
  --name myAKSCluster \
  --enable-private-cluster \
  --api-server-authorized-ip-ranges "203.0.113.0/24,198.51.100.0/24"
```

**AKS with Full VNet Integration**:
```yaml
# Complete private setup with VNet integration
az aks create \
  --name myAKSCluster \
  --enable-private-cluster \
  --enable-apiserver-vnet-integration \
  --apiserver-subnet-id $API_SERVER_SUBNET_ID \
  --vnet-subnet-id $NODE_SUBNET_ID \
  --network-plugin azure \
  --docker-bridge-address 172.17.0.1/16 \
  --dns-service-ip 10.2.0.10 \
  --service-cidr 10.2.0.0/24
```

## 🔗 References

- [OSS Kubernetes Control Plane Communication](https://kubernetes.io/docs/concepts/architecture/control-plane-node-communication/)
- [Kubernetes Konnectivity Service](https://kubernetes.io/docs/tasks/extend-kubernetes/setup-konnectivity/)
- [OSS Kubernetes Node Architecture](https://kubernetes.io/docs/concepts/architecture/nodes/)
- [Kubernetes Node Controller Source](https://github.com/kubernetes/kubernetes/tree/master/pkg/controller/nodelifecycle)
- [AKS API Server VNet Integration](https://docs.microsoft.com/en-us/azure/aks/api-server-vnet-integration)
- [AKS Private Clusters](https://docs.microsoft.com/en-us/azure/aks/private-clusters)
- [AKS Architecture Documentation](https://docs.microsoft.com/en-us/azure/aks/)
- [Cloud Provider Azure Repository](https://github.com/kubernetes-sigs/cloud-provider-azure)
- [Azure Disk CSI Driver Repository](https://github.com/kubernetes-sigs/azuredisk-csi-driver)
- [Azure File CSI Driver Repository](https://github.com/kubernetes-sigs/azurefile-csi-driver)
- [Azure Container Networking Repository](https://github.com/Azure/azure-container-networking)
- [Azure Instance Metadata Service (IMDS)](https://docs.microsoft.com/en-us/azure/virtual-machines/windows/instance-metadata-service)
