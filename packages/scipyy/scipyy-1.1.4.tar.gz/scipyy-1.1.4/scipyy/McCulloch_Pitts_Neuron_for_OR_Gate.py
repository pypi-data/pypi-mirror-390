#3B
# McCulloch-Pitts Neuron for OR Gate


# Inputs and expected output
inputs = [(0, 0), (0, 1), (1, 0), (1, 1)]

# Weights and threshold for OR gate
weights = [1, 1]
threshold = 1

print("OR Gate using McCulloch-Pitts Neuron:")

for x1, x2 in inputs:
    # Weighted sum
    net_input = x1 * weights[0] + x2 * weights[1]
    
    # Activation function (step function)
    output = 1 if net_input >= threshold else 0
    
    print(f"Input: ({x1}, {x2}) → Output: {output}")
