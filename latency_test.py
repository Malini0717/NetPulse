import subprocess
import time

def ping_google():
    start = time.time()

    # send one ping
    subprocess.run(
        ["ping", "-n", "1", "google.com"],
        stdout=subprocess.DEVNULL
    )

    end = time.time()
    latency_ms = (end - start) * 1000
    return latency_ms

latencies = []

for i in range(20):
    latency = ping_google()
    latencies.append(latency)
    print(f"Latency: {latency:.2f} ms")

# calculate jitter
differences = []
for i in range(1, len(latencies)):
    diff = abs(latencies[i] - latencies[i-1])
    differences.append(diff)

jitter = sum(differences) / len(differences)
print(f"\nAverage Jitter: {jitter:.2f} ms")

