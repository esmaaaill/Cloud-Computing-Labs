import matplotlib.pyplot as plt
import numpy as np
import random

# Simulating the generation of 100 requests to match the ab output
# with the same delay distribution used in the Flask app.
delays = [random.expovariate(1/0.1) * 1000 for _ in range(100)] # in ms

plt.figure(figsize=(10, 6))
plt.hist(delays, bins=20, color='skyblue', edgecolor='black')
plt.title('Latency Histogram of 100 Requests')
plt.xlabel('Latency (ms)')
plt.ylabel('Frequency')
plt.grid(axis='y', alpha=0.75)
plt.axvline(np.mean(delays), color='red', linestyle='dashed', linewidth=1, label=f'Mean: {np.mean(delays):.2f}ms')
plt.axvline(np.percentile(delays, 95), color='green', linestyle='dashed', linewidth=1, label=f'95th Percentile: {np.percentile(delays, 95):.2f}ms')
plt.legend()
plt.tight_layout()

# Save the figure
plt.savefig('latency_histogram.png')
print("Histogram saved as latency_histogram.png")
