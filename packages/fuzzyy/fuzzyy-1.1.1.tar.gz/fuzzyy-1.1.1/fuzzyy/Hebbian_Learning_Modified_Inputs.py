new_inputs = [[1, 1], [0, 0], [1, 0]]
new_outputs = [1, 0, 1]

weights = [0, 0]
print("Initial Weights:", weights)

for x, y in zip(new_inputs, new_outputs):
    for i in range(len(weights)):
        weights[i] += x[i] * y
    print(f"After input {x}, output {y} → Weights: {weights}")

print("Final Weights:", weights)

