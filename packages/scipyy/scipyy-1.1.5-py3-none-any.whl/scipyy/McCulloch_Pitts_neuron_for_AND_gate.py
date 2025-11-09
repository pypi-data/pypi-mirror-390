inputs = [(0, 0), (0, 1), (1, 0), (1, 1)]

weights = [1, 1]
threshold = 2

print("AND Gate using McCulloch-Pitts Neuron:")
for x1, x2 in inputs:
    net_input = x1 * weights[0] + x2 * weights[1]
    
    output = 1 if net_input >= threshold else 0
    
    print(f"Input: ({x1}, {x2}) → Output: {output}")
