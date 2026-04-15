#!/usr/bin/env bash
# 钩子脚本：在 Docker 启动后启动 PostgreSQL

POSTGRESQL_START_SCRIPT="/Users/zhuchenglong/workspace/dev_db_datas/start-postgresql.sh"

if [ -f "$POSTGRESQL_START_SCRIPT" ]; then
    echo "启动 PostgreSQL 数据库..."
    cd "$(dirname "$POSTGRESQL_START_SCRIPT")" && "$POSTGRESQL_START_SCRIPT"
else
    echo "警告：未找到 PostgreSQL 启动脚本：$POSTGRESQL_START_SCRIPT"
fi
