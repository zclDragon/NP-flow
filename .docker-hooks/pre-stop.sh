#!/usr/bin/env bash
# 钩子脚本：在 Docker 停止前停止 PostgreSQL

POSTGRESQL_STOP_SCRIPT="/Users/zhuchenglong/workspace/dev_db_datas/stop-postgresql.sh"

if [ -f "$POSTGRESQL_STOP_SCRIPT" ]; then
    echo "停止 PostgreSQL 数据库..."
    cd "$(dirname "$POSTGRESQL_STOP_SCRIPT")" && "$POSTGRESQL_STOP_SCRIPT"
else
    echo "警告：未找到 PostgreSQL 停止脚本：$POSTGRESQL_STOP_SCRIPT"
fi
