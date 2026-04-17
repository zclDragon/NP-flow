#!/usr/bin/env bash
# 钩子脚本：在 DeerFlow 容器启动前启动 PostgreSQL，并等待数据库 ready

set -euo pipefail

POSTGRESQL_START_SCRIPT="/Users/zhuchenglong/workspace/dev_db_datas/start-postgresql.sh"
CONTAINER_NAME="${CONTAINER_NAME:-local-postgresql}"
POSTGRES_DB="${POSTGRES_DB:-app_db}"
POSTGRES_USER="${POSTGRES_USER:-app_user}"
MAX_ATTEMPTS="${POSTGRES_READY_MAX_ATTEMPTS:-60}"
SLEEP_SECONDS="${POSTGRES_READY_SLEEP_SECONDS:-1}"
NETWORK_NAME="${POSTGRESQL_NETWORK_NAME:-deer-flow-dev_deer-flow-dev}"
COMPOSE_PROJECT="${COMPOSE_PROJECT_NAME:-deer-flow-dev}"
COMPOSE_NETWORK_LABEL="${COMPOSE_NETWORK_LABEL:-deer-flow-dev}"

if [ ! -f "$POSTGRESQL_START_SCRIPT" ]; then
    echo "警告：未找到 PostgreSQL 启动脚本：$POSTGRESQL_START_SCRIPT"
    exit 0
fi

ensure_network() {
    local inspect_output compose_network_label compose_project_label

    if ! inspect_output="$(docker network inspect "$NETWORK_NAME" 2>/dev/null)"; then
        echo "创建 Docker 网络: $NETWORK_NAME"
        docker network create \
            --label "com.docker.compose.project=${COMPOSE_PROJECT}" \
            --label "com.docker.compose.network=${COMPOSE_NETWORK_LABEL}" \
            "$NETWORK_NAME" >/dev/null
        return
    fi

    compose_network_label="$(printf '%s' "$inspect_output" | sed -n 's/.*"com.docker.compose.network":"\([^"]*\)".*/\1/p')"
    compose_project_label="$(printf '%s' "$inspect_output" | sed -n 's/.*"com.docker.compose.project":"\([^"]*\)".*/\1/p')"

    if [ "$compose_network_label" = "$COMPOSE_NETWORK_LABEL" ] && [ "$compose_project_label" = "$COMPOSE_PROJECT" ]; then
        return
    fi

    echo "检测到 Docker 网络标签不匹配，重建网络: $NETWORK_NAME"
    docker network rm "$NETWORK_NAME" >/dev/null 2>&1 || true
    docker network create \
        --label "com.docker.compose.project=${COMPOSE_PROJECT}" \
        --label "com.docker.compose.network=${COMPOSE_NETWORK_LABEL}" \
        "$NETWORK_NAME" >/dev/null
}

ensure_network

echo "启动 PostgreSQL 数据库..."
cd "$(dirname "$POSTGRESQL_START_SCRIPT")" && "$POSTGRESQL_START_SCRIPT"

echo "等待 PostgreSQL 就绪..."
for attempt in $(seq 1 "$MAX_ATTEMPTS"); do
    if docker exec "$CONTAINER_NAME" pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB" >/dev/null 2>&1; then
        echo "PostgreSQL 已就绪。"
        exit 0
    fi

    if [ "$attempt" -eq "$MAX_ATTEMPTS" ]; then
        echo "错误：等待 PostgreSQL 就绪超时（${MAX_ATTEMPTS}s）。"
        exit 1
    fi

    sleep "$SLEEP_SECONDS"
done
