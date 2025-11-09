#6.A
#XOR Problem with Backpropagation
import numpy as np

# Activation and its derivative
def sigmoid(x): return 1 / (1 + np.exp(-x))
def sigmoid_derivative(x): return x * (1 - x)

# Input/Output data
X = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])
y = np.array([[0], [1], [1], [0]])

np.random.seed(1)

# Initialize weights and biases
w_h = np.random.random((2, 4)) - 1  # Weights, hidden layer
bh = np.random.random((1, 4)) - 1   # Bias, hidden layer
w_o = np.random.random((4, 1)) - 1  # Weights, output layer
bo = np.random.random((1, 1)) - 1   # Bias, output layer

lr = 0.1  # Learning rate
epochs = 10000

print("Training on XOR problem...")
for i in range(epochs):
    # Forward propagation
    h_in = np.dot(X, w_h) + bh
    h_out = sigmoid(h_in)
    o_in = np.dot(h_out, w_o) + bo
    o_out = sigmoid(o_in)

    # Backpropagation
    err_out = y - o_out
    err_out = err_out * sigmoid_derivative(o_out)
    err_h = err_out.dot(w_o.T) * sigmoid_derivative(h_out)

    # Update weights and biases
    w_h += X.T.dot(err_h) * lr
    w_o += h_out.T.dot(err_out) * lr
    bh += np.sum(err_h, axis=0, keepdims=True) * lr
    bo += np.sum(err_out, axis=0, keepdims=True) * lr

print("Training complete.")
print("Final predictions:\n", o_out)

