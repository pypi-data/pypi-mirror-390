import numpy as np
import matplotlib.pyplot as plt

X = np.array([[1], [2], [3], [4], [5]])
y = np.array([-1, -1, 1, 1, 1])

X_bias = np.c_[np.ones((X.shape[0], 1)), X]

def adaline_train_error(X, y, lr=0.01, epochs=20):
    weights = np.zeros(X.shape[1])
    errors = []

    for epoch in range(epochs):
        output = np.dot(X, weights)
        error = y - output
        weights += lr * X.T.dot(error)
        mse = (error**2).mean()
        errors.append(mse)

    return weights, errors

weights, errors = adaline_train_error(X_bias, y)

plt.plot(range(1, len(errors)+1), errors, marker='o')
plt.xlabel('Epochs')
plt.ylabel('Mean Squared Error')
plt.title('Adaline - Error vs Epoch')
plt.grid(True)
plt.show()
