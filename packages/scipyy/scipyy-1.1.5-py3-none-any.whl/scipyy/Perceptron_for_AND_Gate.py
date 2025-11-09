import numpy as np

X = np.array([[0, 0],
              [0, 1],
              [1, 0],
              [1, 1]])
y = np.array([0, 0, 0, 1])

weights = np.zeros(2)
bias = 0
learning_rate = 0.1
epochs = 10

def step(x):
    return 1 if x >= 0 else 0

for epoch in range(epochs):
    print(f"Epoch {epoch + 1}")
    for i in range(len(X)):
        linear_output = np.dot(X[i], weights) + bias
        y_pred = step(linear_output)
        error = y[i] - y_pred

        weights += learning_rate * error * X[i]
        bias += learning_rate * error

        print(f"Input: {X[i]}, Predicted: {y_pred}, Error: {error}")
    print("---")

print("Training complete.")
print("Final weights:", weights)
print("Final bias:", bias)

print("\nTesting Perceptron for AND gate:")
for i in range(len(X)):
    result = step(np.dot(X[i], weights) + bias)
    print(f"{X[i]} => {result}")

