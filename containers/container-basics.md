# Container Fundamentals

## What are Containers?

Containers are lightweight, standalone, executable packages that include everything needed to run an application: code, runtime, system tools, libraries, and settings. They provide a consistent environment for applications to run across different computing environments.

## Why Containers?

### Traditional Deployment Challenges

Before containers, deploying applications faced several challenges:

- **"Works on my machine" problem**: Applications behave differently across development, testing, and production environments
- **Dependency conflicts**: Different applications requiring different versions of the same library
- **Resource overhead**: Virtual machines require entire OS installations
- **Slow deployment**: Setting up environments manually is time-consuming and error-prone

### Container Benefits

Containers solve these problems by:

1. **Consistency**: Same container runs identically everywhere
2. **Isolation**: Each container runs in its own isolated environment
3. **Portability**: Build once, run anywhere (cloud, on-premises, local)
4. **Efficiency**: Containers share the host OS kernel, using fewer resources than VMs
5. **Speed**: Start in seconds vs. minutes for VMs
6. **Scalability**: Easy to scale horizontally by running multiple container instances

## Containers vs. Virtual Machines

| Aspect | Containers | Virtual Machines |
|--------|-----------|------------------|
| Size | Megabytes | Gigabytes |
| Startup Time | Seconds | Minutes |
| OS | Shares host kernel | Full OS per VM |
| Isolation | Process-level | Complete isolation |
| Resource Usage | Lightweight | Heavy |
| Use Case | Microservices, apps | Full OS environments |

## OCI (Open Container Initiative)

### What is OCI?

The Open Container Initiative is an open governance structure for creating industry standards around container formats and runtimes. It ensures container images and runtimes are compatible across different platforms and tools.

### OCI Standards

The OCI maintains three specifications:

1. **Image Specification (image-spec)**: Defines how to create and package container images
2. **Runtime Specification (runtime-spec)**: Defines how to run containers
3. **Distribution Specification (distribution-spec)**: Defines how to distribute container images

### Why OCI Compliance Matters

OCI compliance ensures:

- **Interoperability**: Images built with Docker work with containerd, Podman, etc.
- **No vendor lock-in**: Choose tools based on features, not compatibility
- **Future-proof**: Standards ensure long-term compatibility
- **Ecosystem support**: Wide tool and platform support

### OCI Image Format

An OCI-compliant image consists of:

1. **Image Manifest**: JSON document describing the image
2. **Image Configuration**: JSON document with image config and metadata
3. **Filesystem Layers**: Compressed tar archives containing the filesystem changes
4. **Image Index (optional)**: Points to multiple manifests for multi-platform images

```json
{
  "schemaVersion": 2,
  "config": {
    "mediaType": "application/vnd.oci.image.config.v1+json",
    "digest": "sha256:abc123...",
    "size": 1234
  },
  "layers": [
    {
      "mediaType": "application/vnd.oci.image.layer.v1.tar+gzip",
      "digest": "sha256:def456...",
      "size": 5678
    }
  ]
}
```

## Container Architecture

### How Containers Work

```
┌─────────────────────────────────────┐
│        Application Layer            │
├─────────────────────────────────────┤
│  Container 1  │  Container 2  │ ... │
│  App + Deps   │  App + Deps   │     │
├─────────────────────────────────────┤
│      Container Runtime              │
│      (Docker, containerd)           │
├─────────────────────────────────────┤
│      Host Operating System          │
├─────────────────────────────────────┤
│      Physical/Virtual Hardware      │
└─────────────────────────────────────┘
```

### Key Components

1. **Container Runtime**: Software that runs containers (Docker Engine, containerd, CRI-O)
2. **Container Images**: Read-only templates used to create containers
3. **Container Registry**: Storage and distribution system for container images
4. **Host OS Kernel**: Shared kernel providing isolation through namespaces and cgroups

### Linux Kernel Features

Containers rely on Linux kernel features:

- **Namespaces**: Isolate processes, network, filesystem, etc.
  - PID namespace: Process isolation
  - NET namespace: Network stack isolation
  - MNT namespace: Filesystem mount isolation
  - UTS namespace: Hostname isolation
  - IPC namespace: Inter-process communication isolation
  
- **Control Groups (cgroups)**: Limit and isolate resource usage
  - CPU limits
  - Memory limits
  - Disk I/O limits
  - Network bandwidth limits

- **Union Filesystems**: Layer filesystem changes efficiently
  - OverlayFS
  - AUFS
  - Btrfs

## Container Lifecycle

Understanding the container lifecycle is essential:

```
┌─────────┐    build     ┌───────┐    push      ┌──────────┐
│ Docker- │  ─────────>  │ Image │  ──────────> │ Registry │
│  file   │              └───────┘              └──────────┘
└─────────┘                  │                        │
                             │ pull                   │
                             ▼                        ▼
                        ┌─────────┐            ┌──────────┐
                        │  Local  │ <────────  │  Remote  │
                        │  Image  │            │  Image   │
                        └─────────┘            └──────────┘
                             │
                             │ run
                             ▼
                        ┌─────────┐
                        │Running  │
                        │Container│
                        └─────────┘
                             │
                    ┌────────┼────────┐
                    ▼        ▼        ▼
                 [stop]  [pause]  [kill]
                    │        │        │
                    └────────┴────────┘
                             │
                             ▼
                        ┌─────────┐
                        │ Stopped │
                        │Container│
                        └─────────┘
                             │
                             │ remove
                             ▼
                          [deleted]
```

### Lifecycle States

1. **Image**: Template stored on disk or in registry
2. **Created**: Container created but not started
3. **Running**: Container actively running
4. **Paused**: Container processes suspended
5. **Stopped**: Container stopped but not removed
6. **Removed**: Container deleted from system

## Container Image Layers

Container images are built in layers:

```
┌─────────────────────────────┐
│    Application Layer        │  <- Your app code
├─────────────────────────────┤
│    Dependencies Layer       │  <- pip install ...
├─────────────────────────────┤
│    Runtime Layer           │  <- Python runtime
├─────────────────────────────┤
│    Base OS Layer           │  <- Alpine/Ubuntu base
└─────────────────────────────┘
```

### Layer Benefits

- **Efficiency**: Shared layers save disk space
- **Caching**: Unchanged layers don't need rebuilding
- **Distribution**: Only changed layers need downloading
- **Version control**: Each layer has a unique hash

### Example Layer Structure

```dockerfile
FROM python:3.11-slim          # Layer 1: Base image
WORKDIR /app                   # Layer 2: Create directory
COPY requirements.txt .        # Layer 3: Copy requirements
RUN pip install -r requirements.txt  # Layer 4: Install deps
COPY app.py .                  # Layer 5: Copy app code
CMD ["python", "app.py"]       # Layer 6: Set command (metadata)
```

## Container Registries

Container registries store and distribute container images:

### Types of Registries

1. **Public Registries**
   - Docker Hub: `docker.io`
   - GitHub Container Registry: `ghcr.io`
   - Quay.io: `quay.io`

2. **Private Registries**
   - Azure Container Registry (ACR): `<registry-name>.azurecr.io`
   - Amazon ECR: `<account>.dkr.ecr.<region>.amazonaws.com`
   - Google Container Registry: `gcr.io/<project-id>`
   - Self-hosted: Harbor, GitLab Registry

### Azure Container Registry (ACR)

ACR is Azure's managed container registry service:

- **OCI Compliant**: Stores Docker images and OCI artifacts
- **Geo-replication**: Replicate images across Azure regions
- **Security**: Private networking, encryption, Azure AD integration
- **Build Service**: Build images without local Docker
- **Integration**: Native integration with AKS and other Azure services

## Best Practices

### Image Design

1. **Use minimal base images**: Alpine, distroless, or scratch
2. **Layer optimization**: Order Dockerfile commands from least to most frequently changing
3. **Multi-stage builds**: Separate build and runtime environments
4. **Security scanning**: Scan images for vulnerabilities
5. **Version tagging**: Use semantic versioning, avoid `latest` tag in production

### Security

1. **Run as non-root user**: Avoid running containers as root
2. **Scan for vulnerabilities**: Use tools like Trivy, Clair
3. **Minimal permissions**: Grant only necessary permissions
4. **Secrets management**: Don't bake secrets into images
5. **Update regularly**: Keep base images and dependencies updated

### Performance

1. **Optimize layer caching**: Structure Dockerfile for efficient caching
2. **Minimize image size**: Remove unnecessary files and dependencies
3. **Use .dockerignore**: Exclude unnecessary files from build context
4. **Parallel builds**: Build independent layers in parallel
5. **Resource limits**: Set appropriate CPU and memory limits

## Next Steps

Now that you understand container fundamentals, proceed to:

- [Dockerfile Guide](dockerfile-guide.md): Learn to create your own container images
- [Running Containers Locally](running-containers.md): Practice running containers
- [Azure Container Registry](acr-guide.md): Work with ACR for building and storing images

## Additional Resources

- [OCI Specifications](https://github.com/opencontainers)
- [Docker Documentation](https://docs.docker.com/)
- [Container Security Best Practices](https://cheatsheetseries.owasp.org/cheatsheets/Docker_Security_Cheat_Sheet.html)
- [Kubernetes Container Runtime Interface](https://kubernetes.io/docs/concepts/architecture/cri/)
