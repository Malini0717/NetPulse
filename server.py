from flask import Flask, jsonify, render_template
import subprocess
import time

app = Flask(__name__)

# Data
latencies = []
jitters = []
packet_losses = []

sent_packets = 0
received_packets = 0

def ping():
    global sent_packets, received_packets
    sent_packets += 1

    start = time.time()
    result = subprocess.run(
        ["ping", "-n", "1", "-w", "1000", "google.com"],  # Windows
        stdout=subprocess.DEVNULL
    )

    if result.returncode == 0:
        received_packets += 1
        return (time.time() - start) * 1000
    else:
        return None

def stability_score(latency, jitter, loss):
    score = 100

    if latency is not None:
        score -= min(latency / 2, 35)

    score -= min(jitter * 2, 35)
    score -= min(loss * 2, 30)

    return max(0, int(score))

def stability_label(score):
    if score >= 80:
        return "GOOD"
    elif score >= 50:
        return "MODERATE"
    else:
        return "POOR"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/data")
def data():
    latency = ping()

    # latency handling
    if latency is not None:
        latencies.append(latency)
    else:
        latencies.append(latencies[-1] if latencies else 0)

    # jitter
    if len(latencies) > 1:
        jitter = abs(latencies[-1] - latencies[-2])
    else:
        jitter = 0
    jitters.append(jitter)

    # packet loss %
    loss = ((sent_packets - received_packets) / sent_packets) * 100
    packet_losses.append(loss)

    score = stability_score(latency, jitter, loss)
    label = stability_label(score)

    return jsonify({
        "latency": round(latencies[-1], 2),
        "jitter": round(jitter, 2),
        "packet_loss": round(loss, 2),
        "score": score,
        "status": label
    })

if __name__ == "__main__":
    app.run(debug=True)
