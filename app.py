from flask import Flask, request, jsonify, send_from_directory
import os
import datetime
import sqlite3 as sql

app = Flask(__name__)
db_file = "sensor_data.db"
# 存储最新的传感器数据
latest_data = {}

def init_db():
    conn = sql.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS sensor_data (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        temp REAL, hum REAL, sound REAL, light REAL,
                        air_quality INTEGER, pir INTEGER,
                        acc_x REAL, acc_y REAL, acc_z REAL,
                        timestamp TEXT)""")
    conn.commit()
    conn.close()
    print("✅ sensor_data 表已创建")

init_db()
def save_to_db(data):
    conn = sql.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("""INSERT INTO sensor_data
                    (temp, hum, sound, light, air_quality, pir, acc_x, acc_y, acc_z, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (data["temp"], data["hum"], data["sound"], data["light"],
                    data["air_quality"], data["pir"], data["acc"][0], data["acc"][1], data["acc"][2], data["timestamp"]))
    conn.commit()
    conn.close()
db_file = os.path.abspath("sensor_data.db")  # 获取数据库的绝对路径
print("数据库路径:", db_file)
@app.route("/history", methods=["GET"])
def get_history():
    try:
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 10))
        offset = (page - 1) * per_page

        conn = sql.connect(db_file)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sensor_data ORDER BY id DESC LIMIT ? OFFSET ?", (per_page, offset))
        rows = cursor.fetchall()
        conn.close()

        data = [{"temp": r[0], "hum": r[1], "sound": r[2], "light": r[3], 
                 "air_quality": r[4], "pir": r[5], "acc": [r[6], r[7], r[8]], 
                 "timestamp": r[9]} for r in rows]
        return jsonify({"data": data,"page": page, "per_page": per_page})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/view_history")
def view_history():
    return send_from_directory(os.path.dirname(__file__), "history.html")
@app.route("/data", methods=["POST"])
def receive_data():
    global latest_data
    latest_data = request.json  # 解析 JSON 数据
    data = request.json
    #data = {"temp":24.10,"hum":39.00,"sound":2.39,"light":2.47,"air_quality":20,"pir":1,"acc":[-1.20,5.29,8.10],"gyro":[0.03,-0.02,0.09]}
    data["timestamp"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # 添加数据更新时间
    latest_data = data
    save_to_db(latest_data)
    print("收到数据:",latest_data)
    return jsonify({"status": "success"}), 200

@app.route("/latest", methods=["GET"])
def get_latest_data():
    return jsonify(latest_data)

@app.route("/")
def index():
    return send_from_directory(os.path.dirname(__file__), "index.html")

if __name__ == "__main__":
    app.run(host="::", port=3232, debug=True)
