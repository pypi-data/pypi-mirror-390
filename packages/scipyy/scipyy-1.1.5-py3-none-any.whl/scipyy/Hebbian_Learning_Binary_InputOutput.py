inputs = [[1, 0], [0, 1], [1, 1]]
outputs = [1, 1, 0]

weights = [0, 0]
print("Initial Weights:", weights)

for x, y in zip(inputs, outputs):
    for i in range(len(weights)):
        weights[i] += x[i] * y
    print(f"After input {x}, output {y} → Weights: {weights}")

print("Final Weights:", weights)
