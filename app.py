from flask import Flask, render_template_string, jsonify
import psutil
import requests
import subprocess

app = Flask(__name__)

OLLAMA_URL = "http://localhost:11434/api/generate"

# ---------------- SYSTEM STATS ----------------
def get_stats():
    temps = psutil.sensors_temperatures()
    temp = 0

    if temps:
        for key in ["cpu_thermal", "cpu-thermal", "thermal_zone0"]:
            if key in temps and len(temps[key]) > 0:
                temp = temps[key][0].current
                break

    return {
        "cpu": psutil.cpu_percent(interval=0.2),
        "ram": psutil.virtual_memory().percent,
        "disk": psutil.disk_usage('/').percent,
        "temp": temp
    }

# ---------------- VOICE ALERT ----------------
def speak(text):
    try:
        subprocess.Popen(["espeak", text])
    except Exception as e:
        print("Voice error:", e)

# ---------------- AI ----------------
def ai_insight(stats):
    prompt = f"""
You are a system monitoring AI.

Return STRICT format:

STATUS: GOOD / WARNING / CRITICAL

SYSTEM STATS:
CPU: {stats['cpu']}%
RAM: {stats['ram']}%
DISK: {stats['disk']}%
TEMP: {stats['temp']}°C

ANALYSIS:
- brief explanation

RISK:
- should user worry?

ACTION:
- one recommendation
"""

    try:
        r = requests.post(
            OLLAMA_URL,
            json={
                "model": "llama3.2:1b",
                "prompt": prompt,
                "stream": False
            },
            timeout=120
        )

        data = r.json()
        return data.get("response", str(data)).strip()

    except Exception as e:
        return f"AI error: {e}"

# ---------------- ROUTES ----------------
@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/stats")
def stats():
    return jsonify(get_stats())

@app.route("/ai")
def ai():
    stats = get_stats()
    result = ai_insight(stats)

    # extract status
    status_line = "UNKNOWN"
    for line in result.split("\n"):
        if "STATUS:" in line:
            status_line = line.replace("STATUS:", "").strip()

    # 🔊 VOICE ALERT LOGIC
    if "CRITICAL" in status_line:
        speak("Critical system warning detected")
    elif "WARNING" in status_line:
        speak("System warning detected")

    return jsonify({"insight": result})

# ---------------- UI ----------------
HTML = """
<!DOCTYPE html>
<html>
<head>
<title>AI System Control Center</title>

<style>
body {
    margin: 0;
    font-family: Arial;
    background: #0b0f19;
    color: white;
    display: flex;
}

.sidebar {
    width: 220px;
    background: #111827;
    height: 100vh;
    padding: 20px;
}

.sidebar h2 {
    color: #00c6ff;
}

.nav-btn {
    width: 100%;
    margin: 10px 0;
    padding: 10px;
    border: none;
    background: #1f2937;
    color: white;
    border-radius: 8px;
    cursor: pointer;
}

.nav-btn:hover {
    background: #00c6ff;
    color: black;
}

.main {
    flex: 1;
    padding: 20px;
}

.grid {
    display: flex;
    gap: 15px;
    flex-wrap: wrap;
}

.card {
    flex: 1;
    min-width: 150px;
    background: rgba(255,255,255,0.06);
    padding: 15px;
    border-radius: 12px;
    text-align: center;
}

.value {
    font-size: 26px;
    margin-top: 10px;
}

#ai-box {
    margin-top: 20px;
    background: rgba(0,0,0,0.4);
    padding: 15px;
    border-radius: 12px;
    white-space: pre-line;
}

button {
    margin-top: 10px;
    padding: 10px;
    border-radius: 8px;
    border: none;
    background: #00c6ff;
    cursor: pointer;
}
</style>
</head>

<body>

<div class="sidebar">
    <h2>System</h2>
    <button class="nav-btn">Dashboard</button>
</div>

<div class="main">

<h1>AI System Dashboard</h1>

<div class="grid">
    <div class="card">CPU <div id="cpu" class="value">--</div></div>
    <div class="card">RAM <div id="ram" class="value">--</div></div>
    <div class="card">Disk <div id="disk" class="value">--</div></div>
    <div class="card">Temp <div id="temp" class="value">--</div></div>
</div>

<div id="ai-box">
    <h3>🧠 AI Analysis</h3>
    <pre id="ai-text">Click to analyze system</pre>

    <button onclick="refreshAI()">🔄 Run AI Analysis</button>
</div>

</div>

<script>

async function updateStats() {
    const r = await fetch("/stats");
    const d = await r.json();

    document.getElementById("cpu").innerText = d.cpu;
    document.getElementById("ram").innerText = d.ram;
    document.getElementById("disk").innerText = d.disk;
    document.getElementById("temp").innerText = d.temp;
}

async function refreshAI() {
    document.getElementById("ai-text").innerText = "Analyzing system...";

    const r = await fetch("/ai");
    const d = await r.json();

    document.getElementById("ai-text").innerText = d.insight;
}

window.onload = function() {
    updateStats();
    setInterval(updateStats, 4000);
};

</script>

</body>
</html>
"""

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
