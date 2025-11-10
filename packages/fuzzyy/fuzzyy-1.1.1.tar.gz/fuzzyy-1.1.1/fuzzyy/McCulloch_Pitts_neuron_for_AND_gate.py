print("AND Gate using McCulloch-Pitts Neuron:")
for x1, x2 in [(0, 0), (0, 1), (1, 0), (1, 1)]:
    print(f"Input: ({x1}, {x2}) → Output: {1 if x1 + x2 >= 2 else 0}")
