import random

def fitness(x):
    return x**2

def select(population):
    a, b = random.sample(population, 2)
    return a if fitness(a) > fitness(b) else b

def genetic_algorithm(crossover_rate, mutation_rate, generations=20, pop_size=6, lower=-10, upper=10):
    population = [random.randint(lower, upper) for _ in range(pop_size)]
    print(f"\nRunning GA with crossover_rate={crossover_rate}, mutation_rate={mutation_rate}")
    
    for gen in range(generations):
        new_pop = []
        for _ in range(pop_size):
            p1, p2 = select(population), select(population)
            child = (p1 + p2) // 2 if random.random() < crossover_rate else p1
            if random.random() < mutation_rate:
                child = random.randint(lower, upper)
            new_pop.append(child)
        population = new_pop
        best = max(population, key=fitness)
        print(f"Gen {gen+1}: Best = {best}, Fitness = {fitness(best)}")

genetic_algorithm(0.9, 0.05)
genetic_algorithm(0.6, 0.2)

