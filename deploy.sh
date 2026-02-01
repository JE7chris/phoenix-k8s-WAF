#!/bin/bash

# 定义版本号 (使用时间戳，避免版本冲突)
TAG="v$(date +%Y%m%d-%H%M%S)"
IMAGE="je7chris/phoenix-app:$TAG"

echo "🚀 开始构建镜像: $IMAGE"

# 1. 构建镜像
docker build -t $IMAGE ./app

# 2. 搬运镜像 (如果你用了方案一，这就不用了，但为了保险先留着)
echo "🚚 正在搬运镜像到 Minikube..."
minikube image load $IMAGE --overwrite=true

# 3. 更新 K8s
echo "♻️ 更新 Deployment..."
kubectl set image deployment/phoenix-deploy phoenix-container=$IMAGE

echo "✅ 部署完成！当前版本: $TAG"
