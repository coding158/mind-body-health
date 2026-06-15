#!/usr/bin/env bash
# 同步推送到 GitHub 和 Gitee 两个远程仓库
# Push to both GitHub and Gitee remotes simultaneously
#
# 用法 / Usage: bash tools/push-all.sh

set -e

BRANCH="${1:-main}"

echo "=== 推送到 GitHub (origin) ==="
git push origin "$BRANCH"

echo ""
echo "=== 推送到 Gitee  ==="
git push gitee "$BRANCH"

echo ""
echo "✅ 两边同步完成 / Both remotes synced."
