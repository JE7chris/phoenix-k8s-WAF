import os
import logging
import redis
import pymysql
from flask import Flask, jsonify, render_template, request
from prometheus_flask_exporter import PrometheusMetrics

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
app = Flask(__name__)
metrics = PrometheusMetrics(app)

REDIS_HOST = os.getenv('REDIS_HOST', 'redis')
DB_HOST = 'mysql-service'
DB_USER = 'root'
DB_PASS = '123456'
DB_NAME = 'phoenix_db'

def get_redis_conn():
    try:
        return redis.Redis(host=REDIS_HOST, port=6379, db=0, decode_responses=True)
    except:
        return None

def get_db_conn():
    try:
        return pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASS, database=DB_NAME, charset='utf8mb4')
    except:
        return None

# === 🛡️ 智能门卫 (增加白名单) ===
@app.route('/') 
def home_check():
    return home()

@app.before_request
def block_bad_ips():
    # ⚠️ 永远放行 Dashboard 和 API 接口
    if request.path.startswith('/dashboard') or request.path.startswith('/api'):
        return None

    r = get_redis_conn()
    if r:
        # 获取客户端 IP (尝试获取真实 IP)
        src_ip = request.remote_addr
        
        # 检查 IP 是否在封禁列表
        if r.sismember('blocked_ips', src_ip) or r.exists(f"block:{src_ip}"):
            return render_template('403.html'), 403

# === 1. 首页 ===
@app.route('/')
def home():
    r = get_redis_conn()
    count = r.incr('hits') if r else "Err"
    container_id = os.getenv('HOSTNAME', 'local')
    
    return f"""
    <div style="font-family: sans-serif; text-align: center; margin-top: 100px;">
        <h1>👋 Hello, Phoenix!</h1>
        <p>Your IP: {request.remote_addr}</p>
        <p>Total Visits: <b>{count}</b></p>
        <p><small>Served by: {container_id}</small></p>
        <hr>
        <p>👇 Are you the Admin?</p>
        <a href="/dashboard" style="background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
            Go to Monitor Dashboard
        </a>
    </div>
    """

# === 2. 大屏路由 ===
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# === 3. 数据统计接口 (核心修改区) ===
@app.route('/api/stats')
def stats():
    response = {"total": 0, "blocked": 0, "logs": [], "trends": [], "types": []}
    
    # 1. 获取 Redis 数据 (封禁数)
    r = get_redis_conn()
    if r:
        temp_keys = r.keys('block:*')
        perm_ips = r.smembers('blocked_ips')
        blocked_set = set(perm_ips)
        for k in temp_keys:
            blocked_set.add(k.replace('block:', ''))
        response['blocked'] = len(blocked_set)

    # 2. 获取 MySQL 数据 (日志与图表)
    conn = get_db_conn()
    if conn:
        try:
            cur = conn.cursor()
            
            # A. 总告警数
            cur.execute("SELECT COUNT(*) FROM alerts")
            response['total'] = cur.fetchone()[0]
            
            # === 🔥 B. 核心修改：攻击日志优先展示 ===
            # 逻辑：先按 "是否是攻击" 排序 (True排前面)，再按 "ID倒序" (新发生的排前面)
            sql = """
                SELECT id, timestamp, src_ip, attack_type, dst_port 
                FROM alerts 
                ORDER BY (attack_type != 'Normal') DESC, id DESC 
                LIMIT 15
            """
            cur.execute(sql)
            
            for row in cur.fetchall():
                response['logs'].append({
                    "id": row[0], 
                    "time": str(row[1]), # 兼容时间格式
                    "ip": row[2], 
                    "type": row[3], 
                    "port": row[4]
                })
            
            # C. 趋势图数据 (简化)
            cur.execute("SELECT id FROM alerts ORDER BY id DESC LIMIT 20")
            rows = sorted(cur.fetchall())
            response['trends'] = [{"t": f"#{r[0]}", "v": i} for i, r in enumerate(rows)]
            
            # D. 攻击类型分布 (饼图)
            cur.execute("SELECT attack_type, COUNT(*) FROM alerts GROUP BY attack_type")
            response['types'] = [{"name": r[0], "value": r[1]} for r in cur.fetchall()]
            
            conn.close()
        except Exception as e:
            logging.error(f"DB Error: {e}")
            pass
            
    return jsonify(response)

# === IP 管理接口 ===
@app.route('/api/blocked_ips', methods=['GET'])
def get_blocked_list():
    r = get_redis_conn()
    if not r: return jsonify([])
    ips = []
    for ip in r.smembers('blocked_ips'):
        ips.append({"ip": ip, "type": "PERMANENT", "ttl": -1})
    for key in r.keys('block:*'):
        ip = key.replace('block:', '')
        ttl = r.ttl(key)
        if not any(x['ip'] == ip for x in ips):
            ips.append({"ip": ip, "type": "TEMPORARY", "ttl": ttl})
    return jsonify(ips)

@app.route('/api/block_ip', methods=['POST'])
def manual_block():
    ip = request.json.get('ip')
    if not ip: return jsonify({"error": "Missing IP"}), 400
    r = get_redis_conn()
    if r:
        r.sadd('blocked_ips', ip)
        return jsonify({"status": "blocked", "ip": ip})
    return jsonify({"error": "Redis error"}), 500

@app.route('/api/unblock_ip', methods=['POST'])
def manual_unblock():
    ip = request.json.get('ip')
    if not ip: return jsonify({"error": "Missing IP"}), 400
    r = get_redis_conn()
    if r:
        r.srem('blocked_ips', ip)
        r.delete(f"block:{ip}")
        return jsonify({"status": "unblocked", "ip": ip})
    return jsonify({"error": "Redis error"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
