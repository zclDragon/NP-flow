# Dev 启动说明

## 当前推荐方式

### 1. 首次启动或依赖变更后先构建

```bash
export UV_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
export NPM_REGISTRY=https://registry.npmmirror.com
export UV_HTTP_TIMEOUT=120
export DEER_FLOW_ROOT=$(pwd)
make docker-build
```

适用场景：

- 第一次启动项目
- 改了 backend 或 frontend 的依赖
- 改了 Dockerfile
- 改了 `UV_EXTRAS`

### 2. 日常启动

```bash
export UV_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
export NPM_REGISTRY=https://registry.npmmirror.com
export UV_HTTP_TIMEOUT=120
export DEER_FLOW_ROOT=$(pwd)
make docker-start
```

当前 `make docker-start` 默认只启动容器，不再自动 rebuild。

### 3. 停止服务

```bash
make docker-stop
```

### 4. 查看日志

```bash
make docker-logs
make docker-logs-frontend
make docker-logs-gateway
```

## 为什么这样更快

现在启动方式已经调整为：

- `make docker-build` 负责构建镜像
- `make docker-start` 负责直接启动容器

这样日常启动不会每次都重新 build。

同时 gateway 启动时也不再执行 `uv sync`，而是直接使用镜像里已经安装好的依赖启动。

## 访问地址

启动成功后访问：

- http://localhost:2026

## 常见问题

### 1. 启动时报依赖缺失

说明镜像还是旧的，需要重新构建：

```bash
make docker-build
make docker-start
```

### 2. Docker 拉基础镜像失败

先检查本机 Docker 的 registry mirrors 是否可用。

### 3. 自定义智能体管理提示未开启

确认 [config.yaml](file:///Users/zhuchenglong/workspace/open-source-projects/NP-flow/config.yaml#L884-L885) 已配置：

```yaml
agents_api:
  enabled: true
```
