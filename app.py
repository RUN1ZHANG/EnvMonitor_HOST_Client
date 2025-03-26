from flask import Flask, request, jsonify, send_from_directory
import os
import datetime

app = Flask(__name__)

# 存储最新的传感器数据
latest_data = {}

@app.route("/data", methods=["POST"])
def receive_data():
    global latest_data
    latest_data = request.json  # 解析 JSON 数据
    data = request.json
    data = {"temp":24.10,"hum":39.00,"sound":2.39,"light":2.47,"air_quality":20,"pir":1,"acc":[-1.20,5.29,8.10],"gyro":[0.03,-0.02,0.09]}
    data["timestamp"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # 添加数据更新时间
    latest_data = data
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
