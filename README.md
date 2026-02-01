# Phoenix WAF: Cloud-Native Active Defense System 🛡️

![Kubernetes](https://img.shields.io/badge/Kubernetes-Production-326ce5?logo=kubernetes)
![Python](https://img.shields.io/badge/Python-3.9-blue?logo=python)
![Prometheus](https://img.shields.io/badge/Observability-Prometheus-e6522c?logo=prometheus)
![Grafana](https://img.shields.io/badge/Visualization-Grafana-f46800?logo=grafana)

> **一个基于 Kubernetes 的微服务架构 Web 应用防火墙 (WAF)，集成旁路流量嗅探、主动防御与全栈可观测性能力。**

---

## 📖 项目简介 (Introduction)

**Phoenix WAF** 是一个探索 **SRE (站点可靠性工程)** 与 **DevSecOps** 理念的云原生安全实践项目。

与传统防火墙不同，本项目利用 K8s 的 **Sidecar (边车模式)** 挂载流量嗅探器，实现了对业务零侵入的流量分析。系统能够实时识别 SQL 注入、XSS 等攻击行为，并通过 Redis 异步消息队列实现毫秒级的自动封禁，同时通过 Prometheus 和 Grafana 提供全链路的可观测性监控。

---

## 🏗️ 核心架构 (Core Architecture)

系统采用微服务架构设计，主要包含以下核心组件：

1.  **Phoenix Pod (Sidecar 模式)**:
    * **Supervisord**: 进程管理器，在单容器内同时守护业务进程和嗅探进程。
    * **Flask App**: 模拟存在漏洞的业务应用。
    * **Sniffer**: 基于 `Scapy` 的旁路嗅探器，捕获 Pod 网卡流量。
2.  **Analysis Engine**: 从 Redis 消费流量日志，正则匹配攻击特征。
3.  **Active Defense**: 发现攻击后自动将 IP 写入 Redis 黑名单，Web 端实时阻断。
4.  **Observability**: Prometheus 采集业务指标，Grafana 展示系统大屏。

```mermaid
graph TD
    User((User/Attacker)) -->|"HTTP Request"| NodePort["K8s Service :30007"]
    NodePort --> Pod["Phoenix Pod"]
    
    subgraph "Phoenix Pod (Sidecar Pattern)"
        Supervisord["Supervisord Process Mgr"]
        WebApp["Flask App (Biz Logic)"]
        Sniffer["Scapy Sniffer"]
    end
    
    Supervisord --> WebApp
    Supervisord --> Sniffer
    
    WebApp -.->|"Traffic Mirror"| Sniffer
    WebApp --"Check Blacklist"--> Redis
    
    Sniffer -->|"Async Logs"| Redis[("Redis Queue")]
    
    subgraph "Backend System"
        Redis
        Analyzer["Analysis Engine"]
        MySQL[("MySQL Storage")]
    end
    
    Analyzer -->|"Consume Logs"| Redis
    Analyzer -->|"Update Block Rules"| Redis
    Analyzer -->|"Persist Attacks"| MySQL
    
    subgraph "Observability Stack"
        Prometheus -->|"Scrape Metrics"| WebApp
        Grafana -->|"Visualize"| Prometheus
    end


## 技术栈
领域,关键技术,详细说明
云原生编排,Kubernetes (Minikube),使用 Deployment 管理无状态应用，ConfigMap/Secret 管理配置
容器化,Docker,编写 Dockerfile，使用 Multi-stage 构建镜像
进程管理,Supervisord,容器内多进程守护，确保 Web 和 Sniffer 同时存活
开发语言,Python 3.9,"Flask (Web服务), Scapy (流量分析), Redis-py (数据交互)"
网络底层,TCP/IP & Libpcap,基于 Linux 底层抓包技术，实现非侵入式流量审计
中间件,Redis,作为 List 消息队列缓冲流量日志，作为 Set 存储黑名单 IP
持久化,MySQL 5.7,存储历史攻击日志，用于后续的安全审计和报表
监控告警,Prometheus,使用 prometheus-flask-exporter 埋点采集 QPS 和延迟
可视化,Grafana,定制 dashboard (ID: 17629)，展示系统负载和业务健康度
前端大屏,ECharts + HTML5,自研安全态势感知大屏，实时刷新攻击数据
