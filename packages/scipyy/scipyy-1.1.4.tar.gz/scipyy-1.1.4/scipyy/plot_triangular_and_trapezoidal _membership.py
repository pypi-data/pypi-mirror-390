#1B plot triangular and trapezoidal membership 
import numpy as np
import matplotlib.pyplot as plt

x = np.linspace(0, 10, 100)

# Triangular membership function
def triangular(x, a, b, c):
    return np.maximum(np.minimum((x - a) / (b - a), (c - x) / (c - b)), 0)

# Trapezoidal membership function
def trapezoidal(x, a, b, c, d):
    return np.maximum(np.minimum(np.minimum((x - a) / (b - a), 1), (d - x) / (d - c)), 0)

# Compute membership values
tri = triangular(x, 2, 5, 8)
trap = trapezoidal(x, 2, 4, 6, 8)

# Plotting
plt.plot(x, tri, label='Triangular')
plt.plot(x, trap, label='Trapezoidal')
plt.title('Membership Functions')
plt.xlabel('x')
plt.ylabel('Membership')
plt.legend()
plt.grid(True)
plt.show()


#OP will be a graph
