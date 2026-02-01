import requests
import time
import random
import threading

# 目标地址 (注意是 NodePort 端口)
# 如果 minikube ip 不是 127.0.0.1，请自行修改，比如 http://192.168.49.2:30007
TARGET_URL = "http://192.168.49.2:30007"
# 攻击载荷库
PAYLOADS = [
    "/?id=1' UNION SELECT user,password FROM users --",  # SQL 注入
    "/?q=<script>alert('pwned')</script>",             # XSS 攻击
    "/?file=../../../../etc/passwd",                    # 路径遍历
    "/?cmd=; cat /flag"                                 # 命令注入
]

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Chrome/91.0.4472.114",
    "Python-urllib/3.9",
    "Kali-Linux/2026.1"
]

def attack():
    while True:
        try:
            # 随机选择一种攻击方式
            payload = random.choice(PAYLOADS)
            url = TARGET_URL + payload
            headers = {'User-Agent': random.choice(USER_AGENTS)}

            print(f"🔫 发送攻击: {payload[:40]}...")
            response = requests.get(url, headers=headers, timeout=2)

            # 检查结果
            if response.status_code == 200:
                print(f"✅ 攻击发送成功 (HTTP 200)")
            elif response.status_code == 403:
                print(f"🚫 被 WAF 拦截! (HTTP 403) - 防御生效中")
                # 如果被封了，就停止线程，不然刷屏
                print("🛑 IP 已被封禁，停止攻击。")
                break
            else:
                print(f"⚠️ 状态码: {response.status_code}")

        except Exception as e:
            print(f"❌ 连接失败: {e}")
            break

        time.sleep(0.5) # 控制语速，别打太快

if __name__ == "__main__":
    print(f"🚀 开始从虚拟机攻击目标: {TARGET_URL}")
    # 启动 2 个线程模拟并发
    for i in range(2):
        t = threading.Thread(target=attack)
        t.start()
