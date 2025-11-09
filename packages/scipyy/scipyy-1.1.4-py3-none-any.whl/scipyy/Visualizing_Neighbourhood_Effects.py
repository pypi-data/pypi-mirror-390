#P.10.B
#Visualizing Neighbourhood Effects
import numpy as np
import matplotlib.pyplot as plt

# Create simple 2D dataset in [-1, 1] range
np.random.seed(42)
data = np.random.rand(100, 2) * 2 - 1  # shape: (100, 2)

# SOM parameters
n_neurons = 8
epochs = 30
Ir = 0.2  # initial learning rate
sigma = 1.5

# Initialize neurons in a straight line from [-1, -1] to [1, 1]
weights = np.linspace([-1, -1], [1, 1], n_neurons)

plt.ion()  # interactive mode on

# Training loop
for epoch in range(epochs):
    for x in data:
        # Find Best Matching Unit (BMU)
        bmu_index = np.argmin(np.linalg.norm(weights - x, axis=1))

        # Update BMU and its neighbors
        for i in range(n_neurons):
            dist = abs(i - bmu_index)
            h = np.exp(-dist**2 / (2 * sigma**2))  # neighborhood function
            weights[i] += Ir * h * (x - weights[i])

    # Live plot update
    plt.clf()
    plt.scatter(data[:, 0], data[:, 1], c='lightgray', label="Data")
    plt.plot(weights[:, 0], weights[:, 1], 'ro-', linewidth=2, label="SOM Neurons")
    plt.title(f"Epoch {epoch+1}")
    plt.legend()
    plt.pause(0.3)

plt.ioff()  # turn off interactive mode
plt.show()


#OP WILL BE 30 epoch
