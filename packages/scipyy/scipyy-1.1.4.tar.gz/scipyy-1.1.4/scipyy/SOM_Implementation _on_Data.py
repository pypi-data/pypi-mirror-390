#P.10.A
#1D SOM Implementation on 2D Data
import numpy as np
import matplotlib.pyplot as plt

# Generate simple 2D dataset (two clusters)
np.random.seed(0)  # for reproducibility
data = np.vstack([
    np.random.randn(50, 2) + np.array([2, 2]),
    np.random.randn(50, 2) + np.array([-2, -2])
])

# SOM parameters
n_neurons = 10
n_epochs = 50
learning_rate = 0.3
sigma = 2.0  # neighbourhood width

# Initialize neuron weights randomly in 2D space
weights = np.random.rand(n_neurons, 2) * 4 - 2  # values in range [-2, 2]

# Training loop
for epoch in range(n_epochs):
    for x in data:
        # Find Best Matching Unit (BMU)
        bmu_index = np.argmin(np.linalg.norm(weights - x, axis=1))
        
        # Update BMU and its neighbours
        for i in range(n_neurons):
            dist = abs(i - bmu_index)
            h = np.exp(-dist**2 / (2 * sigma**2))
            weights[i] += learning_rate * h * (x - weights[i])

# Plot final weights and data
plt.scatter(data[:, 0], data[:, 1], c='gray', alpha=0.5, label="Data")
plt.plot(weights[:, 0], weights[:, 1], 'ro-', label="SOM Neurons")
plt.legend()
plt.title("1D SOM on 2D Data")
plt.grid(True)
plt.show()



#OP WILLL BE A GRAPH
