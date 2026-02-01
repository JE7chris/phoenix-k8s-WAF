# app/attacker.py
import time
import requests
import threading

# 目标地址 (在 K8s 里用 Service 名访问)
TARGET_URL = "http://phoenix-service:5000"

def attack():
    while True:
        try:
            # 发送请求
            response = requests.get(TARGET_URL, timeout=1)
            print(f"[*] Sent request, status: {response.status_code}")
        except Exception as e:
            print(f"[!] Request failed: {e}")
        # 极短的休眠，模拟高并发
        time.sleep(0.01)

# 开启 5 个线程并发攻击
if __name__ == "__main__":
    print(f"🚀 Starting attack on {TARGET_URL}...")
    threads = []
    for i in range(5):
        t = threading.Thread(target=attack)
        t.start()
        threads.append(t)
    
    for t in threads:
        t.join()
