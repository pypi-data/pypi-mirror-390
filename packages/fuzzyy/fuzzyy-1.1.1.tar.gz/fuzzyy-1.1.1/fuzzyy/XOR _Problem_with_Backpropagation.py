import numpy as np

def sigmoid(x): return 1 / (1 + np.exp(-x))
def sigmoid_derivative(x): return x * (1 - x)

X = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])
y = np.array([[0], [1], [1], [0]])

np.random.seed(1)
w_h, bh = np.random.random((2, 4)) - 1, np.random.random((1, 4)) - 1
w_o, bo = np.random.random((4, 1)) - 1, np.random.random((1, 1)) - 1

print("Training on XOR problem...")
for _ in range(10000):
    h_out = sigmoid(X @ w_h + bh)
    o_out = sigmoid(h_out @ w_o + bo)
    err_out = (y - o_out) * sigmoid_derivative(o_out)
    err_h = err_out @ w_o.T * sigmoid_derivative(h_out)
    w_h += X.T @ err_h * 0.1
    w_o += h_out.T @ err_out * 0.1
    bh += err_h.sum(0, keepdims=True) * 0.1
    bo += err_out.sum(0, keepdims=True) * 0.1

print("Training complete.")
print("Final predictions:\n", o_out)

