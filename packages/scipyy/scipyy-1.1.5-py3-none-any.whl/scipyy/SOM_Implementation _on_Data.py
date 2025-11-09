import numpy as np
import matplotlib.pyplot as plt

np.random.seed(0)
data = np.vstack([
    np.random.randn(50, 2) + np.array([2, 2]),
    np.random.randn(50, 2) + np.array([-2, -2])
])

n_neurons = 10
n_epochs = 50
learning_rate = 0.3
sigma = 2.0

weights = np.random.rand(n_neurons, 2) * 4 - 2

for epoch in range(n_epochs):
    for x in data:
        bmu_index = np.argmin(np.linalg.norm(weights - x, axis=1))
        
        for i in range(n_neurons):
            dist = abs(i - bmu_index)
            h = np.exp(-dist**2 / (2 * sigma**2))
            weights[i] += learning_rate * h * (x - weights[i])

plt.scatter(data[:, 0], data[:, 1], c='gray', alpha=0.5, label="Data")
plt.plot(weights[:, 0], weights[:, 1], 'ro-', label="SOM Neurons")
plt.legend()
plt.title("1D SOM on 2D Data")
plt.grid(True)
plt.show()
