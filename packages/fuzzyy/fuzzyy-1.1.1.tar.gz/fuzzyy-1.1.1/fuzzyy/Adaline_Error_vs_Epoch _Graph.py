import numpy as np
import matplotlib.pyplot as plt

X = np.c_[np.ones(5), [[1], [2], [3], [4], [5]]]
y = np.array([-1, -1, 1, 1, 1])

weights = np.zeros(X.shape[1])
errors = []

for epoch in range(20):
    error = y - X @ weights
    weights += 0.01 * X.T @ error
    errors.append((error**2).mean())

plt.plot(range(1, 21), errors, marker='o')
plt.xlabel('Epochs')
plt.ylabel('Mean Squared Error')
plt.title('Adaline - Error vs Epoch')
plt.grid(True)
plt.show()
