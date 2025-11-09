import random

def fitness(x):
    return x ** 2

def create_population(size, lower, upper):
    return [random.randint(lower, upper) for _ in range(size)]

def select(population):
    a, b = random.sample(population, 2)
    return a if fitness(a) > fitness(b) else b

def crossover(parent1, parent2, crossover_rate):
    if random.random() < crossover_rate:
        return (parent1 + parent2) // 2
    return parent1

def mutate(x, lower, upper, mutation_rate):
    if random.random() < mutation_rate:
        return random.randint(lower, upper)
    return x

def genetic_algorithm(crossover_rate, mutation_rate, generations=20, pop_size=6, lower=-10, upper=10):
    population = create_population(pop_size, lower, upper)
    print(f"\nRunning GA with crossover_rate={crossover_rate}, mutation_rate={mutation_rate}")
    
    for gen in range(generations):
        new_population = []
        for _ in range(pop_size):
            p1 = select(population)
            p2 = select(population)
            child = crossover(p1, p2, crossover_rate)
            child = mutate(child, lower, upper, mutation_rate)
            new_population.append(child)
        
        population = new_population
        best = max(population, key=fitness)
        print(f"Gen {gen+1}: Best = {best}, Fitness = {fitness(best)}")

genetic_algorithm(0.9, 0.05)
genetic_algorithm(0.6, 0.2)

