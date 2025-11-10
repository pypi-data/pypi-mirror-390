import numpy as np
import matplotlib.pyplot as plt

np.random.seed(42)
data = np.random.rand(100, 2) * 2 - 1
weights = np.linspace([-1, -1], [1, 1], 8)

plt.ion()

for epoch in range(30):
    for x in data:
        bmu = np.argmin(np.sum((weights - x)**2, axis=1))
        for i in range(8):
            h = np.exp(-(i - bmu)**2 / 4.5)
            weights[i] += 0.2 * h * (x - weights[i])

    plt.clf()
    plt.scatter(data[:, 0], data[:, 1], c='lightgray', label="Data")
    plt.plot(weights[:, 0], weights[:, 1], 'ro-', linewidth=2, label="SOM Neurons")
    plt.title(f"Epoch {epoch+1}")
    plt.legend()
    plt.pause(0.3)

plt.ioff()
plt.show()
