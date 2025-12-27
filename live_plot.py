import subprocess
import time
import matplotlib.pyplot as plt

# Data storage
latencies = []
jitters = []
packet_losses = []

sent_packets = 0
received_packets = 0

# Live plotting
plt.ion()
fig, (ax1, ax2, ax3) = plt.subplots(3, 1)
fig.suptitle("Live Network Stability Monitor", fontsize=14)

def ping():
    """
    Sends one ping.
    Returns latency in ms if success, else None if packet lost.
    """
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
        return None  # packet lost

def stability_score(latency, jitter, loss_percent):
    score = 100

    if latency is not None:
        score -= min(latency / 2, 35)

    score -= min(jitter * 2, 35)
    score -= min(loss_percent * 2, 30)

    return max(0, int(score))

def stability_label(score):
    if score >= 80:
        return "GOOD"
    elif score >= 50:
        return "MODERATE"
    else:
        return "POOR"

try:
    while True:
        latency = ping()

        # Latency
        if latency is not None:
            latencies.append(latency)
        else:
            latencies.append(latencies[-1] if latencies else 0)

        # Jitter
        if len(latencies) > 1:
            jitter = abs(latencies[-1] - latencies[-2])
        else:
            jitter = 0
        jitters.append(jitter)

        # Packet loss %
        loss_percent = ((sent_packets - received_packets) / sent_packets) * 100
        packet_losses.append(loss_percent)

        # Stability
        score = stability_score(latency, jitter, loss_percent)
        label = stability_label(score)

        # Clear plots
        ax1.clear()
        ax2.clear()
        ax3.clear()

        # Latency plot
        ax1.plot(latencies, color="blue")
        ax1.set_ylabel("Latency (ms)")
        ax1.set_title("Latency")
        ax1.text(
            0.02, 0.75,
            f"Stability: {label}\nScore: {score}",
            transform=ax1.transAxes,
            fontsize=12,
            bbox=dict(facecolor="white", alpha=0.9)
        )

        # Jitter plot
        ax2.plot(jitters, color="red")
        ax2.set_ylabel("Jitter (ms)")
        ax2.set_title("Jitter")

        # Packet loss plot
        ax3.plot(packet_losses, color="black")
        ax3.set_ylabel("Packet Loss (%)")
        ax3.set_xlabel("Time")
        ax3.set_title("Packet Loss")

        plt.pause(0.7)

except KeyboardInterrupt:
    print("\nNetwork monitoring stopped.")
