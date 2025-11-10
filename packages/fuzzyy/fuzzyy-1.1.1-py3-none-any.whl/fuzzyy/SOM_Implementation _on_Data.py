import numpy as np
import matplotlib.pyplot as plt

np.random.seed(0)
data = np.vstack([np.random.randn(50, 2) + [2, 2], np.random.randn(50, 2) + [-2, -2]])
weights = np.random.rand(10, 2) * 4 - 2

for _ in range(50):
    for x in data:
        bmu = np.argmin(np.sum((weights - x)**2, axis=1))
        for i in range(10):
            h = np.exp(-(i - bmu)**2 / 8)
            weights[i] += 0.3 * h * (x - weights[i])

plt.scatter(data[:, 0], data[:, 1], c='gray', alpha=0.5, label="Data")
plt.plot(weights[:, 0], weights[:, 1], 'ro-', label="SOM Neurons")
plt.legend()
plt.title("1D SOM on 2D Data")
plt.grid(True)
plt.show()
