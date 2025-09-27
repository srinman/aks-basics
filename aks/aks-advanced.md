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

## 🔗 References

- [Kubernetes Architecture Documentation](https://kubernetes.io/docs/concepts/architecture/)
- [AKS Architecture Documentation](https://docs.microsoft.com/en-us/azure/aks/)
- [Cloud Provider Azure Repository](https://github.com/kubernetes-sigs/cloud-provider-azure)
- [Azure Disk CSI Driver Repository](https://github.com/kubernetes-sigs/azuredisk-csi-driver)
- [Azure File CSI Driver Repository](https://github.com/kubernetes-sigs/azurefile-csi-driver)
- [Azure Container Networking Repository](https://github.com/Azure/azure-container-networking)
