import numpy as np

A = np.array([0.1, 0.4, 0.7])
B = np.array([0.2, 0.5, 0.9])

fuzzy_and = np.minimum(A, B)

fuzzy_or = np.maximum(A, B)

fuzzy_not = 1 - A

print("A =", A)
print("B =", B)
print("Fuzzy AND =", fuzzy_and)
print("Fuzzy OR =", fuzzy_or)
print("Fuzzy NOT (of A) =", fuzzy_not)
