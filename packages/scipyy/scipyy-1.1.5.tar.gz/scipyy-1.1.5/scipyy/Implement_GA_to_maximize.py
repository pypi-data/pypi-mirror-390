import random

def fitness(x):
    return x**2

def create_population(size, lower, upper):
    return [random.randint(lower, upper) for _ in range(size)]

def select(population):
    a, b = random.sample(population, 2)
    return a if fitness(a) > fitness(b) else b

def crossover(parent1, parent2):
    return (parent1 + parent2) // 2

def mutate(x, lower, upper, mutation_rate=0.1):
    if random.random() < mutation_rate:
        return random.randint(lower, upper)
    return x

def genetic_algorithm(generations=20, pop_size=6, lower=-10, upper=10):
    population = create_population(pop_size, lower, upper)
    for gen in range(generations):
        new_population = [ ]
        for _ in range(pop_size):
            p1 = select(population)
            p2 = select(population)
            child = crossover(p1, p2)
            child = mutate(child, lower, upper)
            new_population.append(child)
        population = new_population
        best = max(population, key=fitness)
        print(f"Gen {gen+1}: Best = {best}, Fitness = {fitness(best)}")

genetic_algorithm()

