import numpy as np

X = np.array([[1, 1], [2, 1], [1, 2], [2, 2], [3, 1], [3, 2], [3, 4], [4, 3], [4, 4]])
y = np.array([-1, -1, -1, -1, 1, 1, 1, 1, 1])
X_bias = np.c_[np.ones(9), X]

weights = np.zeros(X_bias.shape[1])
for _ in range(20):
    error = y - X_bias @ weights
    weights += 0.01 * X_bias.T @ error

X_test = np.array([[1, 1], [4, 4], [2.5, 2.5]])
X_test_bias = np.c_[np.ones(3), X_test]
predictions = np.where(X_test_bias @ weights >= 0, 1, -1)
print("Predictions:", predictions)

