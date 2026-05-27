# DeerFlow Sandbox Provisioner 中文说明

Sandbox Provisioner 是一个 FastAPI 服务，用来在 Kubernetes 中动态创建、查询和删除 sandbox Pod。DeerFlow 后端需要执行代码或命令时，会通过 HTTP 调用 provisioner，由 provisioner 调用 K8s API 创建隔离的 sandbox 环境。

## 架构

```text
DeerFlow Backend
  ↓ HTTP
Provisioner :8002
  ↓ K8s API
Kubernetes 创建 sandbox Pod + Service
  ↓
Backend 通过 sandbox_url 访问 sandbox
```

简单理解：

```text
Backend 不直接创建容器
Provisioner 负责管理 K8s 里的 sandbox Pod
Sandbox Pod 负责实际执行代码、bash、文件读写等任务
```

## 工作流程

1. 后端需要 sandbox 时，请求：

```text
POST /api/sandboxes
```

请求体包含：

```json
{
  "sandbox_id": "abc-123",
  "thread_id": "thread-456",
  "user_id": "user-789"
}
```

2. provisioner 创建一个独立的 sandbox Pod。

Pod 中包含：

- sandbox 容器镜像
- `/mnt/user-data` 工作数据目录
- `/mnt/skills` skills 目录
- CPU、内存、临时存储限制
- readiness/liveness 探针

3. provisioner 创建一个 NodePort Service 暴露 sandbox Pod。

4. provisioner 返回 sandbox 地址，例如：

```text
http://NODE_HOST:NodePort
```

5. 后端后续直接访问这个 sandbox 地址执行任务。

6. 不再需要时，后端请求：

```text
DELETE /api/sandboxes/{sandbox_id}
```

provisioner 删除对应的 Pod 和 Service。

## API 接口

### 健康检查

```text
GET /health
```

返回：

```json
{"status":"ok"}
```

### 创建 sandbox

```text
POST /api/sandboxes
```

请求：

```json
{
  "sandbox_id": "abc-123",
  "thread_id": "thread-456",
  "user_id": "user-789"
}
```

返回：

```json
{
  "sandbox_id": "abc-123",
  "sandbox_url": "http://host.docker.internal:32123",
  "status": "Pending"
}
```

同一个 `sandbox_id` 重复创建时，会返回已有 sandbox 信息，不会重复创建。

### 查询单个 sandbox

```text
GET /api/sandboxes/{sandbox_id}
```

返回：

```json
{
  "sandbox_id": "abc-123",
  "sandbox_url": "http://host.docker.internal:32123",
  "status": "Running"
}
```

### 删除 sandbox

```text
DELETE /api/sandboxes/{sandbox_id}
```

返回：

```json
{
  "ok": true,
  "sandbox_id": "abc-123"
}
```

### 列出全部 sandbox

```text
GET /api/sandboxes
```

返回：

```json
{
  "sandboxes": [
    {
      "sandbox_id": "abc-123",
      "sandbox_url": "http://host.docker.internal:32123",
      "status": "Running"
    }
  ],
  "count": 1
}
```

## 配置项

provisioner 通过环境变量配置。

| 变量 | 默认值 | 说明 |
|---|---|---|
| `K8S_NAMESPACE` | `deer-flow` | sandbox Pod 和 Service 所在 namespace |
| `SANDBOX_IMAGE` | `enterprise-public-cn-beijing.cr.volces.com/vefaas-public/all-in-one-sandbox:latest` | sandbox 容器镜像 |
| `SKILLS_HOST_PATH` | 空 | hostPath 模式下的 skills 宿主机路径 |
| `THREADS_HOST_PATH` | 空 | hostPath 模式下的线程数据宿主机路径 |
| `SKILLS_PVC_NAME` | 空 | skills PVC 名称；设置后使用 PVC，不用 hostPath |
| `USERDATA_PVC_NAME` | 空 | 用户工作数据 PVC 名称；设置后使用 PVC，不用 hostPath |
| `KUBECONFIG_PATH` | `/root/.kube/config` | provisioner 容器内 kubeconfig 路径 |
| `NODE_HOST` | `host.docker.internal` | 后端访问 sandbox NodePort 时使用的主机名或 IP |
| `K8S_API_SERVER` | kubeconfig 中的地址 | 覆盖 K8s API Server 地址 |

## 关键配置说明

### SANDBOX_IMAGE

sandbox Pod 使用的镜像。

默认值：

```text
enterprise-public-cn-beijing.cr.volces.com/vefaas-public/all-in-one-sandbox:latest
```

生产环境建议使用公司内部镜像仓库和固定版本，不建议使用 `latest`。

### NODE_HOST

provisioner 返回 sandbox 地址时会使用它：

```text
http://NODE_HOST:NodePort
```

所以 `NODE_HOST` 必须是 DeerFlow 后端能访问到的地址。

如果后端在 Docker 内，可能是：

```text
host.docker.internal
```

如果后端在独立生产机器上，通常应配置为 K8s 节点 IP 或负载均衡地址。

### USERDATA_PVC_NAME

设置后，sandbox Pod 的 `/mnt/user-data` 会来自 PVC。

PVC 模式下，实际子路径是：

```text
deer-flow/users/{user_id}/threads/{thread_id}/user-data
```

适合生产环境和多用户场景。

### SKILLS_PVC_NAME

设置后，sandbox Pod 的 `/mnt/skills` 会来自 PVC，并以只读方式挂载。

适合生产环境统一管理 skills。

## hostPath 和 PVC 的区别

不配置 PVC 时，provisioner 会使用 hostPath：

```text
THREADS_HOST_PATH/{thread_id}/user-data -> /mnt/user-data
SKILLS_HOST_PATH -> /mnt/skills
```

这种方式依赖 K8s 节点本地目录。

生产环境更推荐 PVC，因为：

- 多节点不会出现数据分散到不同节点的问题
- Pod 重建或调度到其他节点后仍能访问同一份数据
- 方便结合 NAS/NFS/云存储做持久化

## 本地 Docker Compose 使用

项目的 docker-compose 配置中已经包含 provisioner 服务。

位置：

```text
docker/docker-compose.yaml
docker/docker-compose-dev.yaml
```

它会：

- 挂载宿主机 kubeconfig 到容器内
- 使用环境变量配置 K8s namespace、sandbox 镜像、路径和 NODE_HOST
- 暴露 `8002` 健康检查和 sandbox 管理 API

示例：

```bash
docker compose -p deer-flow-dev -f docker/docker-compose-dev.yaml up -d provisioner
```

## 生产环境建议

如果公司生产机器不允许 Docker，但允许 K8s，推荐架构是：

```text
生产机器：运行 DeerFlow 主程序
K8s：运行 provisioner 和 sandbox Pod
NAS/NFS/PVC：共享 .deer-flow 和 skills 数据
```

需要运维准备：

- K8s namespace
- provisioner Deployment 和 Service
- provisioner ServiceAccount、Role、RoleBinding
- sandbox 镜像和镜像拉取权限
- USERDATA PVC
- SKILLS PVC
- 生产机器到 provisioner 的网络
- 生产机器到 sandbox NodePort 或等价访问地址的网络

业务侧只需要配置：

```yaml
sandbox:
  use: deerflow.community.aio_sandbox:AioSandboxProvider
  provisioner_url: http://provisioner地址:8002
```

并将运行数据与 skills 指向 NAS/NFS：

```env
DEER_FLOW_HOME=/nas/deerflow/.deer-flow
DEER_FLOW_SKILLS_PATH=/nas/deerflow/skills
```

## 常见问题

### provisioner 连接不上 K8s API

检查：

```bash
kubectl config view --minify -o jsonpath='{.clusters[0].cluster.server}'
```

如果 kubeconfig 中是 `localhost` 或 `127.0.0.1`，provisioner 容器内可能访问不到，需要设置：

```env
K8S_API_SERVER=https://host.docker.internal:端口
```

生产中如果 provisioner 运行在 K8s 内，通常应使用 ServiceAccount，不需要挂载本机 kubeconfig。

### sandbox 创建了但后端访问不到

通常是 `NODE_HOST` 配错，或网络/防火墙不通。

检查：

```bash
kubectl -n deer-flow get svc
```

确认 NodePort 后，从后端机器访问：

```bash
curl http://NODE_HOST:NodePort/v1/sandbox
```

### Pod 一直 ContainerCreating

通常是镜像拉取或 PVC 挂载问题。

检查：

```bash
kubectl -n deer-flow describe pod sandbox-xxxx
```

重点看 Events。

### 文件在主程序有，但 sandbox 看不到

通常是主程序和 K8s sandbox 没有共享同一份存储。

生产建议让主程序和 K8s 都使用同一个 NAS/NFS/PVC 数据源。

## 安全建议

- 生产不要使用 `latest` 镜像标签
- 生产优先使用 PVC，不建议依赖 hostPath
- provisioner 权限只限定在需要的 namespace
- sandbox Pod 设置资源限制，避免资源耗尽
- 私有镜像使用 imagePullSecrets
- 根据公司要求配置 NetworkPolicy
