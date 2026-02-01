# Phoenix Project: Cloud Native SRE Demo

这是一个基于 Kubernetes 的全栈微服务架构实战项目。

## 🏗️ 架构特性
- **计算**: K8s Deployment 高可用架构 + 资源配额限制 (Resource Quotas)
- **网络**: Nginx Ingress 7层路由 + Service 负载均衡
- **存储**: PVC 数据持久化 (Redis)
- **监控**: Prometheus + Grafana 全链路可观测性
- **配置**: ConfigMap & Secret 配置分离

## 🚀 快速开始
```bash
# 1. 应用配置
kubectl apply -f k8s/

# 2. 访问
http://phoenix.local
```
