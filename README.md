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
