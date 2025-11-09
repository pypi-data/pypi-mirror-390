import numpy as np

X = np.array([[1, 1],
              [2, 1],
              [1, 2],
              [2, 2],
              [3, 1],
              [3, 2],
              [3, 4],
              [4, 3],
              [4, 4]])

y = np.array([-1, -1, -1, -1, 1, 1, 1, 1, 1])

X_bias = np.c_[np.ones((X.shape[0], 1)), X]

def adaline_train(X, y, lr=0.01, epochs=20):
    weights = np.zeros(X.shape[1])
    for epoch in range(epochs):
        output = np.dot(X, weights)
        error = y - output
        weights += lr * X.T.dot(error)
    return weights

weights = adaline_train(X_bias, y)

def predict(X, weights):
    X_bias = np.c_[np.ones((X.shape[0], 1)), X]
    return np.where(np.dot(X_bias, weights) >= 0, 1, -1)

X_test = np.array([[1, 1], [4, 4], [2.5, 2.5]])
predictions = predict(X_test, weights)
print("Predictions:", predictions)

