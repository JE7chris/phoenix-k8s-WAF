from scapy.all import *
import redis
import json
import os
import re
import urllib.parse
from datetime import datetime # 引入时间处理

REDIS_HOST = os.getenv('REDIS_HOST', 'redis')
try:
    r = redis.Redis(host=REDIS_HOST, port=6379, db=0)
except:
    pass

ATTACK_PATTERNS = {
    "SQL Injection": [r"UNION", r"SELECT", r"SLEEP\(", r"extractvalue", r"updatexml", r"OR.*1=1"],
    "XSS Attack": [r"<script>", r"alert\(", r"onerror", r"onload", r"javascript:"],
    "Command Inj": [r"/etc/passwd", r"cat ", r"whoami", r";ls", r"\.\./"]
}

def packet_callback(packet):
    if packet.haslayer(TCP) and packet.haslayer(Raw):
        try:
            # === 1. 核心降噪：只关心 Web 端口 (5000) ===
            dst_port = packet[TCP].dport
            src_port = packet[TCP].sport
            
            # 如果是 Redis(6379) 或 MySQL(3306) 的流量，直接丢弃，看都不要看
            if dst_port in [6379, 3306] or src_port in [6379, 3306]:
                return

            # 如果不是发往 5000 的包（比如 SSH 或者其他杂音），也丢弃
            # 我们只关心: 攻击者 -> Service (5000)
            if dst_port != 5000:
                return

            raw_data = packet[Raw].load
            payload = raw_data.decode('utf-8', errors='ignore')

            # 忽略 HTTP 响应包 (只看请求)
            if payload.startswith("HTTP"): return

            decoded_payload = urllib.parse.unquote(payload)
            src_ip = packet[IP].src
            
            detected_type = "Normal"
            
            # 2. 攻击检测
            for type_name, keywords in ATTACK_PATTERNS.items():
                for keyword in keywords:
                    if re.search(keyword, decoded_payload, re.IGNORECASE):
                        detected_type = type_name
                        print(f"🔥 DETECTED {type_name} from {src_ip}")
                        break
                if detected_type != "Normal": break

            # 3. 智能上报策略
            # 只有当它是攻击，或者是正常的 HTTP 请求时才记录
            # 过滤掉空的 TCP 握手包等杂音
            if detected_type != "Normal" or "GET " in payload or "POST " in payload:
                
                # === 4. 时间格式化 (在这里直接转好) ===
                # 将 17699... 转为 "16:20:30" 格式
                readable_time = datetime.fromtimestamp(float(packet.time)).strftime('%H:%M:%S')

                data = {
                    "src_ip": src_ip,
                    "dst_port": dst_port,
                    "timestamp": readable_time, # 发送可读时间
                    "attack_type": detected_type,
                    "payload": decoded_payload[:200]
                }
                if r:
                    r.lpush('traffic_queue', json.dumps(data))

        except Exception as e:
            pass

print("🕵️ Sniffer V4.6 (Noise Filtered) Started...")
sniff(filter="tcp", prn=packet_callback, store=0) 
# 注意：filter改为了 "tcp"，具体的端口过滤我们在 Python 代码里做，这样更灵活
