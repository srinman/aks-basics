# Docker VM Setup with Azure Bastion

If you don't have Docker Desktop installed locally, you can create an Azure VM with Docker pre-installed and connect to it securely using Azure Bastion in developer mode. This provides a frictionless experience for learning container basics.

## Why Use a Docker VM?

✅ **No Local Installation**: Don't need Docker Desktop on your machine  
✅ **Consistent Environment**: Same setup for all learners  
✅ **Secure Access**: Azure Bastion provides secure SSH without public IPs  
✅ **Cloud Resources**: Use Azure compute for building and running containers  
✅ **Easy Cleanup**: Delete the VM when done, no local artifacts  
✅ **Cost-Effective**: Pay only for what you use, stop VM when not needed  

## Prerequisites

- Azure subscription
- Azure CLI installed (`az`)
- SSH client (built-in on macOS/Linux, Windows 10+)

## Architecture

```
┌─────────────────────────────────────────────┐
│           Your Local Machine                │
│                                             │
│  ┌──────────────────────────────────┐      │
│  │  Azure CLI / SSH Client          │      │
│  └───────────────┬──────────────────┘      │
└──────────────────┼──────────────────────────┘
                   │
                   │ Secure connection
                   ▼
┌─────────────────────────────────────────────┐
│              Azure Cloud                    │
│                                             │
│  ┌──────────────────────────────────┐      │
│  │  Azure Bastion (Dev Mode)        │      │
│  │  - SSH tunnel                    │      │
│  │  - No public IP needed           │      │
│  └───────────────┬──────────────────┘      │
│                  │                          │
│                  │ Private connection       │
│                  ▼                          │
│  ┌──────────────────────────────────┐      │
│  │  Docker VM (Private IP only)     │      │
│  │  - Ubuntu 22.04 LTS              │      │
│  │  - Docker Engine                 │      │
│  │  - Docker Compose                │      │
│  │  - Azure CLI                     │      │
│  └──────────────────────────────────┘      │
│                                             │
│  ┌──────────────────────────────────┐      │
│  │  Azure Container Registry         │      │
│  └──────────────────────────────────┘      │
└─────────────────────────────────────────────┘
```

## Quick Setup Script

Use this automated script for fastest setup:

```bash
#!/bin/bash

# Set variables
RESOURCE_GROUP="rg-docker-vm"
LOCATION="eastus"
VM_NAME="docker-vm"
VNET_NAME="docker-vnet"
SUBNET_NAME="docker-subnet"
BASTION_SUBNET="AzureBastionSubnet"
BASTION_NAME="docker-bastion"
VM_SIZE="Standard_B2s"  # 2 vCPU, 4GB RAM - $30/month if running 24/7
ADMIN_USERNAME="dockeradmin"

# Create resource group
echo "Creating resource group..."
az group create \
  --name $RESOURCE_GROUP \
  --location $LOCATION

# Create virtual network
echo "Creating virtual network..."
az network vnet create \
  --resource-group $RESOURCE_GROUP \
  --name $VNET_NAME \
  --address-prefix 10.0.0.0/16 \
  --subnet-name $SUBNET_NAME \
  --subnet-prefix 10.0.1.0/24

# Create Bastion subnet
echo "Creating Bastion subnet..."
az network vnet subnet create \
  --resource-group $RESOURCE_GROUP \
  --vnet-name $VNET_NAME \
  --name $BASTION_SUBNET \
  --address-prefix 10.0.2.0/26

# Create VM with Docker (using cloud-init)
echo "Creating VM with Docker..."
az vm create \
  --resource-group $RESOURCE_GROUP \
  --name $VM_NAME \
  --image Ubuntu2204 \
  --size $VM_SIZE \
  --admin-username $ADMIN_USERNAME \
  --generate-ssh-keys \
  --public-ip-address "" \
  --vnet-name $VNET_NAME \
  --subnet $SUBNET_NAME \
  --custom-data @docker-cloud-init.yaml

# Create Bastion in developer mode
echo "Creating Azure Bastion (this takes 5-10 minutes)..."
az network bastion create \
  --name $BASTION_NAME \
  --resource-group $RESOURCE_GROUP \
  --vnet-name $VNET_NAME \
  --location $LOCATION \
  --sku Developer

echo ""
echo "✅ Setup complete!"
echo ""
echo "Connect to your VM:"
echo "  az network bastion ssh \\"
echo "    --name $BASTION_NAME \\"
echo "    --resource-group $RESOURCE_GROUP \\"
echo "    --target-resource-id \$(az vm show -g $RESOURCE_GROUP -n $VM_NAME --query id -o tsv) \\"
echo "    --auth-type ssh-key \\"
echo "    --username $ADMIN_USERNAME \\"
echo "    --ssh-key ~/.ssh/id_rsa"
echo ""
echo "💡 Tip: Create an alias for easy connection:"
echo "  alias docker-vm='az network bastion ssh --name $BASTION_NAME --resource-group $RESOURCE_GROUP --target-resource-id \$(az vm show -g $RESOURCE_GROUP -n $VM_NAME --query id -o tsv) --auth-type ssh-key --username $ADMIN_USERNAME --ssh-key ~/.ssh/id_rsa'"
```

## Cloud-Init Configuration

Create a file named `docker-cloud-init.yaml` for automated Docker installation:

```yaml
#cloud-config

package_update: true
package_upgrade: true

packages:
  - apt-transport-https
  - ca-certificates
  - curl
  - gnupg
  - lsb-release
  - git
  - vim
  - jq

runcmd:
  # Install Docker
  - curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
  - echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
  - apt-get update
  - apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
  
  # Add admin user to docker group
  - usermod -aG docker dockeradmin
  
  # Install Azure CLI
  - curl -sL https://aka.ms/InstallAzureCLIDeb | bash
  
  # Enable and start Docker
  - systemctl enable docker
  - systemctl start docker
  
  # Create working directory
  - mkdir -p /home/dockeradmin/containers
  - chown -R dockeradmin:dockeradmin /home/dockeradmin/containers

write_files:
  - path: /etc/docker/daemon.json
    content: |
      {
        "log-driver": "json-file",
        "log-opts": {
          "max-size": "10m",
          "max-file": "3"
        }
      }

final_message: "Docker VM is ready! Docker version: $(docker --version)"
```

## Step-by-Step Setup

### Step 1: Create Resource Group

```bash
# Set variables
RESOURCE_GROUP="rg-docker-vm"
LOCATION="eastus"

# Create resource group
az group create \
  --name $RESOURCE_GROUP \
  --location $LOCATION
```

### Step 2: Create Virtual Network

```bash
VNET_NAME="docker-vnet"
SUBNET_NAME="docker-subnet"

# Create VNet with VM subnet
az network vnet create \
  --resource-group $RESOURCE_GROUP \
  --name $VNET_NAME \
  --address-prefix 10.0.0.0/16 \
  --subnet-name $SUBNET_NAME \
  --subnet-prefix 10.0.1.0/24

# Create Bastion subnet (required name: AzureBastionSubnet)
az network vnet subnet create \
  --resource-group $RESOURCE_GROUP \
  --vnet-name $VNET_NAME \
  --name AzureBastionSubnet \
  --address-prefix 10.0.2.0/26
```

### Step 3: Create VM with Docker

```bash
VM_NAME="docker-vm"
ADMIN_USERNAME="dockeradmin"

# Create the cloud-init file first (see above)
# Then create VM
az vm create \
  --resource-group $RESOURCE_GROUP \
  --name $VM_NAME \
  --image Ubuntu2204 \
  --size Standard_B2s \
  --admin-username $ADMIN_USERNAME \
  --generate-ssh-keys \
  --public-ip-address "" \
  --vnet-name $VNET_NAME \
  --subnet $SUBNET_NAME \
  --custom-data docker-cloud-init.yaml

# Note: No public IP address is created (--public-ip-address "")
```

### Step 4: Create Azure Bastion

```bash
BASTION_NAME="docker-bastion"

# Create Bastion in Developer mode (faster, cheaper)
az network bastion create \
  --name $BASTION_NAME \
  --resource-group $RESOURCE_GROUP \
  --vnet-name $VNET_NAME \
  --location $LOCATION \
  --sku Developer

# This takes 5-10 minutes to provision
```

### Step 5: Connect to VM

```bash
# Get VM resource ID
VM_ID=$(az vm show \
  --resource-group $RESOURCE_GROUP \
  --name $VM_NAME \
  --query id \
  --output tsv)

# Connect via Bastion
az network bastion ssh \
  --name $BASTION_NAME \
  --resource-group $RESOURCE_GROUP \
  --target-resource-id $VM_ID \
  --auth-type ssh-key \
  --username $ADMIN_USERNAME \
  --ssh-key ~/.ssh/id_rsa
```

### Step 6: Verify Docker Installation

Once connected to the VM:

```bash
# Check Docker version
docker --version

# Check Docker Compose
docker compose version

# Check Azure CLI
az --version

# Run test container
docker run hello-world

# Check Docker info
docker info

# Verify user is in docker group
groups
```

## Creating a Connection Alias

For easier access, create an alias:

```bash
# Add to your ~/.bashrc or ~/.zshrc
alias docker-vm='az network bastion ssh \
  --name docker-bastion \
  --resource-group rg-docker-vm \
  --target-resource-id $(az vm show -g rg-docker-vm -n docker-vm --query id -o tsv) \
  --auth-type ssh-key \
  --username dockeradmin \
  --ssh-key ~/.ssh/id_rsa'

# Reload shell configuration
source ~/.bashrc  # or source ~/.zshrc

# Now connect with just:
docker-vm
```

## Using the Docker VM

### Build Images Locally

```bash
# Connect to VM
docker-vm

# Clone your repository or create Dockerfile
mkdir -p ~/containers/flask-echo
cd ~/containers/flask-echo

# Create files (copy from examples)
# Then build
docker build -t flask-echo:v1.0.0 .

# Run container
docker run -d -p 8080:8080 flask-echo:v1.0.0

# Test (from within VM)
curl http://localhost:8080/
```

### Push Images to ACR

```bash
# Login to Azure
az login

# Login to ACR
REGISTRY_NAME="myregistry"
az acr login --name $REGISTRY_NAME

# Tag image for ACR
docker tag flask-echo:v1.0.0 ${REGISTRY_NAME}.azurecr.io/flask-echo:v1.0.0

# Push to ACR
docker push ${REGISTRY_NAME}.azurecr.io/flask-echo:v1.0.0
```

### Transfer Files to VM

#### Using SCP via Bastion Tunnel

```bash
# Create SSH tunnel (from local machine)
az network bastion tunnel \
  --name docker-bastion \
  --resource-group rg-docker-vm \
  --target-resource-id $(az vm show -g rg-docker-vm -n docker-vm --query id -o tsv) \
  --resource-port 22 \
  --port 50022

# In another terminal, use SCP with tunnel
scp -P 50022 -r ./flask-echo dockeradmin@localhost:~/containers/
```

#### Using Git (Recommended)

```bash
# Connect to VM
docker-vm

# Clone repository
cd ~/containers
git clone https://github.com/yourusername/aks-basics.git
cd aks-basics/containers/examples/flask-echo

# Build and run
docker build -t flask-echo:latest .
docker run -d -p 8080:8080 flask-echo:latest
```

## Cost Management

### VM Sizes and Costs

| VM Size | vCPU | RAM | Cost/Month (24/7) | Best For |
|---------|------|-----|-------------------|----------|
| Standard_B1s | 1 | 1 GB | ~$7.50 | Learning |
| Standard_B2s | 2 | 4 GB | ~$30 | Recommended |
| Standard_B2ms | 2 | 8 GB | ~$60 | Heavy workloads |

### Bastion Costs

| SKU | Features | Cost/Hour | Cost/Month (24/7) |
|-----|----------|-----------|-------------------|
| Developer | SSH only, 2 connections | ~$0.027 | ~$20 |
| Basic | SSH + RDP, 50 connections | ~$0.19 | ~$140 |

### Cost Optimization

```bash
# Stop VM when not in use (deallocates resources)
az vm deallocate \
  --resource-group rg-docker-vm \
  --name docker-vm

# Start VM when needed
az vm start \
  --resource-group rg-docker-vm \
  --name docker-vm

# Check VM status
az vm get-instance-view \
  --resource-group rg-docker-vm \
  --name docker-vm \
  --query instanceView.statuses[1].displayStatus \
  --output tsv

# Auto-shutdown at night (configure in portal or CLI)
az vm auto-shutdown \
  --resource-group rg-docker-vm \
  --name docker-vm \
  --time 1900 \
  --timezone "Eastern Standard Time"
```

### Stop/Start Script

```bash
#!/bin/bash
# save as docker-vm-control.sh

RESOURCE_GROUP="rg-docker-vm"
VM_NAME="docker-vm"

case "$1" in
  start)
    echo "Starting VM..."
    az vm start -g $RESOURCE_GROUP -n $VM_NAME
    ;;
  stop)
    echo "Stopping VM..."
    az vm deallocate -g $RESOURCE_GROUP -n $VM_NAME
    ;;
  status)
    az vm get-instance-view -g $RESOURCE_GROUP -n $VM_NAME \
      --query instanceView.statuses[1].displayStatus -o tsv
    ;;
  *)
    echo "Usage: $0 {start|stop|status}"
    exit 1
    ;;
esac
```

## Troubleshooting

### Cannot Connect via Bastion

```bash
# Check Bastion status
az network bastion show \
  --name docker-bastion \
  --resource-group rg-docker-vm \
  --query provisioningState

# Check VM is running
az vm get-instance-view \
  --resource-group rg-docker-vm \
  --name docker-vm \
  --query instanceView.statuses[1].displayStatus

# Verify SSH key
ls -la ~/.ssh/id_rsa

# Test with password auth instead
az network bastion ssh \
  --name docker-bastion \
  --resource-group rg-docker-vm \
  --target-resource-id $VM_ID \
  --auth-type password \
  --username dockeradmin
```

### Docker Not Installed

```bash
# Connect to VM and check cloud-init logs
sudo cat /var/log/cloud-init-output.log

# Manually install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
newgrp docker

# Verify
docker --version
```

### Permission Denied on Docker Commands

```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Logout and login again, or:
newgrp docker

# Verify group membership
groups
```

### Out of Disk Space

```bash
# Check disk usage
df -h

# Clean up Docker
docker system prune -a --volumes

# Check Docker disk usage
docker system df
```

## Security Best Practices

### 1. Network Security

```bash
# VM has no public IP - only accessible via Bastion ✅
# Bastion subnet is isolated ✅
# Consider adding NSG for additional security:

az network nsg create \
  --resource-group rg-docker-vm \
  --name docker-vm-nsg

# Allow SSH from Bastion subnet only
az network nsg rule create \
  --resource-group rg-docker-vm \
  --nsg-name docker-vm-nsg \
  --name AllowSSHFromBastion \
  --priority 100 \
  --source-address-prefixes 10.0.2.0/26 \
  --destination-port-ranges 22 \
  --protocol Tcp \
  --access Allow
```

### 2. VM Security

```bash
# Enable Azure Security Center
az security pricing create \
  --name VirtualMachines \
  --tier Standard

# Keep VM updated
ssh into VM:
sudo apt update
sudo apt upgrade -y

# Enable automatic security updates
sudo apt install unattended-upgrades
sudo dpkg-reconfigure --priority=low unattended-upgrades
```

### 3. Docker Security

```bash
# Scan images before use
docker scan flask-echo:latest

# Don't run containers as root
docker run --user 1000:1000 ...

# Use read-only filesystem when possible
docker run --read-only ...
```

## Complete Cleanup

```bash
# Delete everything
az group delete \
  --name rg-docker-vm \
  --yes \
  --no-wait

# Verify deletion
az group list --output table
```

## Comparison: Docker VM vs az acr build

| Aspect | Docker VM | az acr build |
|--------|-----------|--------------|
| Setup Time | 10-15 minutes | None |
| Local Testing | ✅ Yes | ❌ No |
| Interactive | ✅ Yes | ❌ No |
| Cost | ~$50/month | Per build |
| Learning | Great | Limited |
| Production | No | Yes |

**Recommendation**: Use Docker VM for learning and experimentation, use `az acr build` for production workflows.

## Next Steps

Now that you have a Docker environment:

1. Follow the [Flask Echo App tutorial](examples/flask-echo/README.md)
2. Build both Flask and FastAPI apps
3. Experiment with [Dockerfile best practices](dockerfile-guide.md)
4. Learn [container management](running-containers.md)
5. Push images to [Azure Container Registry](acr-guide.md)

## Additional Resources

- [Azure Bastion Documentation](https://docs.microsoft.com/azure/bastion/)
- [Azure VM Sizes](https://docs.microsoft.com/azure/virtual-machines/sizes)
- [Docker Installation Guide](https://docs.docker.com/engine/install/ubuntu/)
- [Cloud-init Documentation](https://cloudinit.readthedocs.io/)
