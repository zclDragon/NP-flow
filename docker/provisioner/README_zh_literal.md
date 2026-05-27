# DeerFlow Sandbox Provisioner

**Sandbox Provisioner** 是一个 FastAPI 服务，用于动态管理 Kubernetes 中的 sandbox Pod。它为 DeerFlow 后端提供 REST API，用于创建、监控和销毁隔离的代码执行 sandbox 环境。

## 架构

```
┌────────────┐  HTTP  ┌─────────────┐  K8s API  ┌──────────────┐
│  Backend   │ ─────▸ │ Provisioner │ ────────▸ │  Host K8s    │
│  (gateway/ │        │   :8002     │           │  API Server  │
│ langgraph) │        └─────────────┘           └──────┬───────┘
└────────────┘                                          │ creates
                                                        │
                          ┌─────────────┐         ┌────▼─────┐
                          │   Backend   │ ──────▸ │  Sandbox │
                          │ (via Docker │ NodePort│  Pod(s)  │
                          │   network)  │         └──────────┘
                          └─────────────┘
```

### 工作方式

1. **后端请求**：当后端需要执行代码时，它会发送一个 `POST /api/sandboxes` 请求，请求中包含 `sandbox_id`、`thread_id` 和可选的 `user_id`。

2. **Pod 创建**：provisioner 会在 `deer-flow` namespace 中创建一个专用 Pod，包含：
   - sandbox 容器镜像（all-in-one-sandbox）
   - 挂载的 HostPath volumes：
     - `/mnt/skills` → 只读访问 public skills
     - `/mnt/user-data` → 读写访问特定 thread 的数据
   - 资源限制（CPU、内存、临时存储）
   - Readiness/liveness probes

3. **Service 创建**：创建一个 NodePort Service 来暴露 Pod，Kubernetes 会从 NodePort 范围中自动分配端口（通常是 30000-32767）。

4. **访问 URL**：provisioner 向后端返回 `http://host.docker.internal:{NodePort}`，后端容器可以直接访问它。

5. **清理**：当会话结束时，`DELETE /api/sandboxes/{sandbox_id}` 会同时移除 Pod 和 Service。

## 要求

宿主机需要有一个正在运行的 Kubernetes 集群（Docker Desktop K8s、OrbStack、minikube、kind 等）。

### 在 Docker Desktop 中启用 Kubernetes

1. 打开 Docker Desktop 设置
2. 进入 “Kubernetes” 标签页
3. 勾选 “Enable Kubernetes”
4. 点击 “Apply & Restart”

### 在 OrbStack 中启用 Kubernetes

1. 打开 OrbStack 设置
2. 进入 “Kubernetes” 标签页
3. 勾选 “Enable Kubernetes”

## API 端点

### `GET /health`

健康检查端点。

**响应**：

```json
{
  "status": "ok"
}
```

### `POST /api/sandboxes`

创建一个新的 sandbox Pod + Service。

**请求**：

```json
{
  "sandbox_id": "abc-123",
  "thread_id": "thread-456",
  "user_id": "user-789"
}
```

`user_id` 为了向后兼容是可选的，默认值为 `default`。当设置了 `USERDATA_PVC_NAME` 时，provisioner 会使用它来隔离基于 PVC 的 user-data 目录。

**响应**：

```json
{
  "sandbox_id": "abc-123",
  "sandbox_url": "http://host.docker.internal:32123",
  "status": "Pending"
}
```

**幂等**：使用相同的 `sandbox_id` 调用时，会返回已有的 sandbox 信息。

### `GET /api/sandboxes/{sandbox_id}`

获取指定 sandbox 的状态和 URL。

**响应**：

```json
{
  "sandbox_id": "abc-123",
  "sandbox_url": "http://host.docker.internal:32123",
  "status": "Running"
}
```

**状态值**：`Pending`、`Running`、`Succeeded`、`Failed`、`Unknown`、`NotFound`

### `DELETE /api/sandboxes/{sandbox_id}`

销毁一个 sandbox Pod + Service。

**响应**：

```json
{
  "ok": true,
  "sandbox_id": "abc-123"
}
```

### `GET /api/sandboxes`

列出当前管理的所有 sandbox。

**响应**：

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

## 配置

provisioner 通过环境变量配置（在 [docker-compose-dev.yaml](../docker-compose-dev.yaml) 中设置）：

| 变量 | 默认值 | 描述 |
|----------|---------|-------------|
| `K8S_NAMESPACE` | `deer-flow` | sandbox 资源所在的 Kubernetes namespace |
| `SANDBOX_IMAGE` | `enterprise-public-cn-beijing.cr.volces.com/vefaas-public/all-in-one-sandbox:latest` | sandbox Pod 使用的容器镜像 |
| `SKILLS_HOST_PATH` | - | skills 目录在**宿主机**上的路径（必须是绝对路径） |
| `THREADS_HOST_PATH` | - | threads 数据目录在**宿主机**上的路径（必须是绝对路径） |
| `SKILLS_PVC_NAME` | empty（使用 hostPath） | skills volume 的 PVC 名称；设置后，sandbox Pod 使用 PVC 而不是 hostPath |
| `USERDATA_PVC_NAME` | empty（使用 hostPath） | user-data volume 的 PVC 名称；设置后，使用带有 `subPath: deer-flow/users/{user_id}/threads/{thread_id}/user-data` 的 PVC |
| `KUBECONFIG_PATH` | `/root/.kube/config` | provisioner 容器**内部**的 kubeconfig 路径 |
| `NODE_HOST` | `host.docker.internal` | 后端容器用于访问宿主机 NodePort 的主机名 |
| `K8S_API_SERVER` | 来自 kubeconfig | 覆盖 K8s API server URL，例如 `https://host.docker.internal:26443` |

### PVC User-Data 升级说明

旧版本 provisioner 从 `threads/{thread_id}/user-data` 挂载 PVC user-data。用户作用域布局从 `deer-flow/users/{user_id}/threads/{thread_id}/user-data` 挂载。

如果现有部署已经在旧布局下有基于 PVC 的 user-data，请在依赖新的 PVC subPath 之前迁移 DeerFlow 数据目录。将 gateway 使用的同一个 PVC 路径挂载为 DeerFlow base directory，然后运行现有的用户隔离迁移脚本：

```bash
cd backend
PYTHONPATH=. python scripts/migrate_user_isolation.py --dry-run
PYTHONPATH=. python scripts/migrate_user_isolation.py --user-id <target-user-id>
```

这会把旧的 `threads/{thread_id}/user-data` 数据移动到 `users/<target-user-id>/threads/{thread_id}/user-data` 下。当 gateway base directory 在 PVC 上挂载到 `deer-flow/` 时，这与新的 provisioner PVC subPath 匹配。只有当旧数据应该保留在默认无认证用户 namespace 中时，才使用 `default` 作为目标用户。在没有 gateway 或 sandbox Pod 写入这些路径时运行迁移。

### 重要：K8S_API_SERVER 覆盖

如果你的 kubeconfig 使用 `localhost`、`127.0.0.1` 或 `0.0.0.0` 作为 API server 地址（这在 OrbStack、minikube、kind 中很常见），provisioner **无法** 从 Docker 容器内部访问它。

**解决方案**：将 `K8S_API_SERVER` 设置为使用 `host.docker.internal`：

```yaml
# docker-compose-dev.yaml
provisioner:
  environment:
    - K8S_API_SERVER=https://host.docker.internal:26443  # 将 26443 替换为你的 API 端口
```

检查你的 kubeconfig API server：

```bash
kubectl config view --minify -o jsonpath='{.clusters[0].cluster.server}'
```

## 前置条件

### 宿主机要求

1. **Kubernetes 集群**：
   - 启用了 Kubernetes 的 Docker Desktop，或
   - OrbStack（内置 K8s），或
   - minikube、kind、k3s 等。

2. **已配置 kubectl**：
   - `~/.kube/config` 必须存在且有效
   - 当前 context 应指向你的本地集群

3. **Kubernetes 访问权限**：
   - provisioner 需要权限来：
     - 在 `deer-flow` namespace 中创建/读取/删除 Pod
     - 在 `deer-flow` namespace 中创建/读取/删除 Service
     - 读取 Namespace（如果缺失则创建 `deer-flow`）

4. **宿主机路径**：
   - `SKILLS_HOST_PATH` 和 `THREADS_HOST_PATH` 必须是**宿主机上的绝对路径**
   - 这些路径会通过 K8s HostPath volumes 挂载到 sandbox Pod 中
   - 这些路径必须存在，并且 K8s 节点可读

### Docker Compose 设置

provisioner 作为 docker-compose-dev stack 的一部分运行：

```bash
# 启动 Docker 服务（只有当 config.yaml 启用 provisioner 模式时，provisioner 才会启动）
make docker-start

# 或者只启动 provisioner
docker compose -p deer-flow-dev -f docker/docker-compose-dev.yaml up -d provisioner
```

compose 文件会：

- 将宿主机的 `~/.kube/config` 挂载到容器中
- 为 `host.docker.internal` 添加 `extra_hosts` 条目（Linux 上需要）
- 配置用于 K8s 访问的环境变量

## 测试

### 手动 API 测试

```bash
# 健康检查
curl http://localhost:8002/health

# 创建 sandbox（通过 provisioner 容器使用内部 DNS）
docker exec deer-flow-provisioner curl -X POST http://localhost:8002/api/sandboxes \
  -H "Content-Type: application/json" \
  -d '{"sandbox_id":"test-001","thread_id":"thread-001","user_id":"user-001"}'

# 检查 sandbox 状态
docker exec deer-flow-provisioner curl http://localhost:8002/api/sandboxes/test-001

# 列出所有 sandbox
docker exec deer-flow-provisioner curl http://localhost:8002/api/sandboxes

# 验证 K8s 中的 Pod 和 Service
kubectl get pod,svc -n deer-flow -l sandbox-id=test-001

# 删除 sandbox
docker exec deer-flow-provisioner curl -X DELETE http://localhost:8002/api/sandboxes/test-001
```

### 从后端容器验证

一旦创建了 sandbox，后端容器（gateway、langgraph）就可以访问它：

```bash
# 从 provisioner 获取 sandbox URL
SANDBOX_URL=$(docker exec deer-flow-provisioner curl -s http://localhost:8002/api/sandboxes/test-001 | jq -r .sandbox_url)

# 从 gateway 容器测试
docker exec deer-flow-gateway curl -s $SANDBOX_URL/v1/sandbox
```

## 故障排查

### 问题：“Kubeconfig not found”

**原因**：kubeconfig 文件不存在于挂载路径。

**解决方案**：

- 确保宿主机上存在 `~/.kube/config`
- 运行 `kubectl config view` 验证
- 检查 docker-compose-dev.yaml 中的 volume mount

### 问题：“Kubeconfig path is a directory”

**原因**：挂载的 `KUBECONFIG_PATH` 指向一个目录，而不是文件。

**解决方案**：

- 确保 compose mount source 是文件，例如 `~/.kube/config`，而不是目录
- 在容器内验证：

  ```bash
  docker exec deer-flow-provisioner ls -ld /root/.kube/config
  ```

- 期望输出应表明它是普通文件（`-`），而不是目录（`d`）

### 问题：“Connection refused” to K8s API

**原因**：provisioner 无法访问 K8s API server。

**解决方案**：

1. 检查你的 kubeconfig server 地址：

   ```bash
   kubectl config view --minify -o jsonpath='{.clusters[0].cluster.server}'
   ```

2. 如果它是 `localhost` 或 `127.0.0.1`，设置 `K8S_API_SERVER`：

   ```yaml
   environment:
     - K8S_API_SERVER=https://host.docker.internal:PORT
   ```

### 问题：创建 Pod 时出现 “Unprocessable Entity”

**原因**：HostPath volumes 包含无效路径，例如带有 `..` 的相对路径。

**解决方案**：

- 为 `SKILLS_HOST_PATH` 和 `THREADS_HOST_PATH` 使用绝对路径
- 验证这些路径存在于你的宿主机上：

  ```bash
  ls -la /path/to/skills
  ls -la /path/to/backend/.deer-flow/threads
  ```

### 问题：Pod 卡在 “ContainerCreating”

**原因**：通常是正在从镜像仓库拉取 sandbox 镜像。

**解决方案**：

- 预拉取镜像：`make docker-init`
- 检查 Pod events：`kubectl describe pod sandbox-XXX -n deer-flow`
- 检查节点：`kubectl get nodes`

### 问题：无法从后端访问 sandbox URL

**原因**：NodePort 不可达，或 `NODE_HOST` 配置错误。

**解决方案**：

- 验证 Service 存在：`kubectl get svc -n deer-flow`
- 从宿主机测试：`curl http://localhost:NODE_PORT/v1/sandbox`
- 确保 docker-compose 中设置了 `extra_hosts`（Linux）
- 检查 `NODE_HOST` 环境变量是否匹配后端访问宿主机的方式

## 安全注意事项

1. **HostPath Volumes**：provisioner 默认会把宿主机目录挂载到 sandbox Pod 中。确保这些路径只包含可信数据。生产环境中，优先使用基于 PVC 的 volumes（设置 `SKILLS_PVC_NAME` 和 `USERDATA_PVC_NAME`），以避免节点特定的数据丢失风险。

2. **资源限制**：每个 sandbox Pod 都有 CPU、内存和存储限制，以防止资源耗尽。

3. **网络隔离**：sandbox Pod 运行在 `deer-flow` namespace 中，但通过 NodePort 共享宿主机网络 namespace。可考虑使用 NetworkPolicies 实现更严格的隔离。

4. **kubeconfig 访问**：provisioner 通过挂载的 kubeconfig 拥有对 Kubernetes 集群的完整访问权限。只应在可信环境中运行它。

5. **镜像可信**：sandbox 镜像应来自可信镜像仓库。请审查并审核镜像内容。

## 未来增强

- [ ] 支持每个 sandbox 自定义资源 requests/limits
- [x] 支持用于更大数据需求的 PersistentVolume
- [ ] 自动清理陈旧 sandbox（基于 timeout）
- [ ] 指标与监控（Prometheus 集成）
- [ ] 多集群支持（路由到不同 K8s 集群）
- [ ] Pod affinity/anti-affinity 规则，用于更好的放置
- [ ] 用于 sandbox 隔离的 NetworkPolicy 模板
