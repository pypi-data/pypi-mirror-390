import numpy as np
import matplotlib.pyplot as plt

np.random.seed(42)
data = np.random.rand(100, 2) * 2 - 1

n_neurons = 8
epochs = 30
Ir = 0.2
sigma = 1.5

weights = np.linspace([-1, -1], [1, 1], n_neurons)

plt.ion()

for epoch in range(epochs):
    for x in data:
        bmu_index = np.argmin(np.linalg.norm(weights - x, axis=1))

        for i in range(n_neurons):
            dist = abs(i - bmu_index)
            h = np.exp(-dist**2 / (2 * sigma**2))
            weights[i] += Ir * h * (x - weights[i])

    plt.clf()
    plt.scatter(data[:, 0], data[:, 1], c='lightgray', label="Data")
    plt.plot(weights[:, 0], weights[:, 1], 'ro-', linewidth=2, label="SOM Neurons")
    plt.title(f"Epoch {epoch+1}")
    plt.legend()
    plt.pause(0.3)

plt.ioff()
plt.show()
