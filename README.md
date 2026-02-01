# Phoenix WAF：云原生主动防御系统 (Cloud-Native Active Defense System) 🛡️

![Kubernetes](https://img.shields.io/badge/Kubernetes-Production-326ce5?logo=kubernetes)
![Python](https://img.shields.io/badge/Python-3.9-blue?logo=python)
![Prometheus](https://img.shields.io/badge/Observability-Prometheus-e6522c?logo=prometheus)
![Grafana](https://img.shields.io/badge/Visualization-Grafana-f46800?logo=grafana)
![Status](https://img.shields.io/badge/Status-Active-success)

> **一个基于 Kubernetes 的微服务架构 Web 应用防火墙 (WAF)，具备实时流量分析、主动拦截和全栈可观测性能力。**

---

## 📖 项目简介 (Introduction)
**Phoenix WAF** 是我在探索 **SRE (站点可靠性工程)** 和 **DevSecOps** 领域的实践项目。与传统防火墙不同，本项目演示了如何用云原生的方式构建安全体系。

项目包含一个部署在 K8s 中的 Web 应用，并通过 **Sidecar (边车模式)** 挂载了自定义的流量嗅探器。它能异步捕获流量，分析攻击特征（如 SQL 注入、XSS、命令注入），并自动更新 Redis 黑名单以拦截恶意 IP。

### 🌟 核心亮点
* **微服务架构**：基于 Docker 和 Kubernetes 的完全容器化部署。
* **主动防御**：实时检测并拦截 SQL 注入、XSS 和系统命令注入攻击。
* **流量嗅探**：使用 `Scapy` 和 `libpcap` 在 Pod 层面进行旁路流量捕获，不影响业务性能。
* **进程管理**：使用 `supervisord` 在单容器内协同管理 Web 服务与嗅探进程。
* **全栈可观测性**：
    * **安全大屏**：基于 Flask + ECharts 的实时攻击可视化看板。
    * **基础设施监控**：集成 **Prometheus & Grafana**，监控 QPS、延迟和系统资源。

---

## 🏗️ 架构设计 (Architecture)

```mermaid
graph TD
    User((攻击者/用户)) -->|HTTP 请求| NodePort[K8s Service :30007]
    NodePort --> Pod[Phoenix Pod]
    
    subgraph "Phoenix Pod (Sidecar 模式)"
        Flask[Flask 业务应用 :5000]
        Sniffer[Scapy 嗅探器]
        Supervisord[Supervisord 进程守护]
    end
    
    Supervisord -.->|启动 & 监控| Flask
    Supervisord -.->|启动 & 监控| Sniffer
    
    Pod -->|流量镜像| Sniffer
    Sniffer -->|异步日志| Redis[(Redis 队列)]
    
    subgraph "后端服务"
        Redis
        MySQL[(MySQL 日志库)]
        Analyzer[分析引擎]
    end
    
    Analyzer -->|消费数据| Redis
    Analyzer -->|生成拦截规则| Redis
    Analyzer -->|持久化存储| MySQL
    
    subgraph "可观测性平台"
        Prometheus -->|拉取指标| Flask
        Grafana -->|可视化展示| Prometheus
    end
    
    Flask -- 检查黑名单 --> Redis
📂 项目结构 (Project Structure)Plaintext.
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
🛠️ 技术栈 (Tech Stack)类别技术用途容器编排Kubernetes (Minikube)服务部署、Service 发现、ConfigMap 配置管理容器化Docker镜像构建、多阶段构建进程管理Supervisord容器内多进程管理 (Web + Sniffer)开发语言Python 3.9Flask Web 应用、流量嗅探脚本网络技术Scapy / TCPDump网络包捕获与协议分析中间件Redis消息队列、黑名单缓存数据库MySQL攻击日志持久化存储监控告警Prometheus业务指标采集 (Exporter)数据可视化Grafana系统健康度仪表盘🚀 快速开始 (Quick Start)前置要求Kubernetes 集群 (推荐 Minikube)Docker 环境kubectl 命令行工具安装步骤克隆仓库Bashgit clone git@github.com:JE7chris/phoenix-k8s-WAF.git
cd phoenix-k8s-WAF
一键部署可以使用提供的脚本快速部署所有服务：Bashchmod +x deploy.sh
./deploy.sh
# 或者手动执行: kubectl apply -f k8s/
访问控制台WAF 监控大屏： http://<minikube-ip>:30007/dashboardGrafana 面板： http://<minikube-ip>:30300 (默认账号: admin/admin)Prometheus： http://<minikube-ip>:30090攻击测试运行项目自带的攻击脚本，模拟 SQL 注入和 XSS 攻击流量：Bashpython3 vm_attacker.py
