import redis
import pymysql
import json
import time
import os

REDIS_HOST = os.getenv('REDIS_HOST', 'redis')
REDIS_KEY = 'traffic_queue'
DB_HOST = 'mysql-service'
DB_USER = 'root'
DB_PASS = '123456'
DB_NAME = 'phoenix_db'

# 封禁时长 (秒) - 设为 60 秒方便测试
BAN_TIME = 60 

print(f"🧠 Analyzer V4.1 (Smart Ban: {BAN_TIME}s) Starting...")

r = redis.Redis(host=REDIS_HOST, port=6379, db=0)

db = None
while db is None:
    try:
        db = pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASS, database=DB_NAME, charset='utf8mb4')
        print("✅ Connected to MySQL")
    except:
        time.sleep(5)
cursor = db.cursor()

while True:
    try:
        item = r.blpop(REDIS_KEY, timeout=0)
        if item:
            data = json.loads(item[1].decode('utf-8'))
            attack_type = data.get('attack_type', 'Normal')
            src_ip = data.get('src_ip')
            
            # === 🛡️ 智能防御逻辑 ===
            if attack_type != "Normal":
                # 使用 setex (Set with Expiration) 设置带过期时间的 Key
                # Key 格式: "block:1.2.3.4"
                # Value: 攻击类型
                r.setex(f"block:{src_ip}", BAN_TIME, attack_type)
                print(f"🚫 BAN: {src_ip} for {BAN_TIME}s due to {attack_type}")
            
            # 入库
            sql = "INSERT INTO alerts (src_ip, dst_port, attack_type, timestamp, details) VALUES (%s, %s, %s, %s, %s)"
            val = (src_ip, data['dst_port'], attack_type, str(data['timestamp']), data.get('payload', ''))
            cursor.execute(sql, val)
            db.commit()
            
    except Exception as e:
        print(f"Error: {e}")
        try:
            db.ping(reconnect=True)
        except:
            pass
