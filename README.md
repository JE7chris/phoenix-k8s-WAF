# Phoenix WAF: Cloud-Native Active Defense System 🛡️

![Kubernetes](https://img.shields.io/badge/Kubernetes-Production-326ce5?logo=kubernetes)
![Python](https://img.shields.io/badge/Python-3.9-blue?logo=python)
![Prometheus](https://img.shields.io/badge/Observability-Prometheus-e6522c?logo=prometheus)
![Grafana](https://img.shields.io/badge/Visualization-Grafana-f46800?logo=grafana)

> **基于 Kubernetes 的云原生 Web 应用防火墙 (WAF)，集成旁路流量嗅探、主动防御与全栈可观测性。**

---

## 🏗️ 核心架构 (Architecture)

本项目采用 Sidecar 模式进行非侵入式流量分析，结合 Redis 异步处理与 Prometheus 监控体系。

```mermaid
graph TD
    User((User)) -->|"HTTP"| SVC["K8s Service :30007"]
    SVC --> Pod["Phoenix Pod"]
    
    subgraph "Phoenix Pod (Sidecar)"
        App["Flask App"]
        Sniffer["Scapy Sniffer"]
        Supervisord["Process Mgr"]
    end
    
    Supervisord --> App
    Supervisord --> Sniffer
    Pod -->|"Traffic Mirror"| Sniffer
    Sniffer -->|"Async Logs"| Redis[("Redis")]
    
    subgraph "Backend"
        Redis
        Analyzer["Analysis Engine"]
        MySQL[("MySQL")]
    end
    
    Analyzer -->|"Consume"| Redis
    Analyzer -->|"Block Rules"| Redis
    Analyzer -->|"Persist"| MySQL
    
    Prometheus -->|"Scrape"| App
    Grafana -->|"Visualize"| Prometheus

## 📂 项目结构 (Project Structure)Plaintext.
├── app/                          # 核心业务源码目录
│   ├── analyzer.py               # 流量分析与日志处理逻辑
│   ├── app.py                    # Flask Web 应用主程序 (业务入口)
│   ├── attacker.py               # 内部测试用的攻击模拟脚本
│   ├── Dockerfile                # 容器镜像构建文件
│   ├── requirements.txt          # Python 依赖清单
│   ├── sniffer.py                # 基于 Scapy 的流量嗅探器 (Sidecar)
│   ├── supervisord.conf          # 进程管理器 (同时启动 Flask 和 Sniffer)
│   └── templates/                # 前端 HTML 模板
│       ├── 403.html              # 恶意请求拦截页面
│       └── dashboard.html        # 实时安全监控大屏
├── k8s/                          # Kubernetes 资源编排清单
│   ├── grafana-deploy.yaml       # Grafana 可视化平台部署
│   ├── mysql.yaml                # MySQL 数据库部署
│   ├── phoenix-config.yaml       # 应用配置文件 (ConfigMap)
│   ├── phoenix-deploy.yaml       # 核心应用 Deployment
│   ├── phoenix-ingress.yaml      # Ingress 路由配置
│   ├── phoenix-secret.yaml       # 敏感信息配置 (Secret)
│   ├── phoenix-service.yaml      # Service 服务暴露
│   ├── prometheus-config.yaml    # Prometheus 抓取规则配置
│   ├── prometheus-deploy.yaml    # Prometheus 监控系统部署
│   ├── redis-deploy.yaml         # Redis 中间件部署
│   └── redis-pvc.yaml            # Redis 数据持久化声明
├── deploy.sh                     # 项目自动化部署脚本
├── vm_attacker.py                # 外部攻击模拟脚本 (用于演示防御效果)
└── README.md                     # 项目说明文档
##🛠️ 技术栈 (Tech Stack)
领域,核心技术,应用场景
云原生编排,Kubernetes (Minikube),Pod 管理、Service 发现、ConfigMap/Secret
容器化,Docker,多阶段镜像构建、环境隔离
开发语言,Python 3.9 (Flask),Web 业务逻辑、WAF 规则引擎、攻击模拟
网络底层,Scapy / Libpcap,旁路流量嗅探、TCP/IP 协议包分析
进程管理,Supervisord,容器内多进程守护 (Web + Sniffer)
中间件,Redis,异步消息队列、黑名单高速缓存
可观测性,Prometheus + Grafana,业务 QPS 监控、延迟报警、系统大屏

##🚀 快速开始 (Quick Start)
前置要求
Kubernetes 集群 (推荐 Minikube)

Docker 环境

kubectl 命令行工具

安装步骤
克隆仓库

Bash
git clone git@github.com:JE7chris/phoenix-k8s-WAF.git
cd phoenix-k8s-WAF
一键部署 可以使用提供的脚本快速部署所有服务：

Bash
chmod +x deploy.sh
./deploy.sh
# 或者手动执行: kubectl apply -f k8s/
访问控制台

WAF 监控大屏： http://<minikube-ip>:30007/dashboard

Grafana 面板： http://<minikube-ip>:30300 (默认账号: admin/admin)

Prometheus： http://<minikube-ip>:30090

攻击测试 运行项目自带的攻击脚本，模拟 SQL 注入和 XSS 攻击流量：

Bash
python3 vm_attacker.py
