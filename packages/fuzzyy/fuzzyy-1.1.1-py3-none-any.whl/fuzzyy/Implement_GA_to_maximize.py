import random

def fitness(x):
    return x**2

def select(population):
    a, b = random.sample(population, 2)
    return a if fitness(a) > fitness(b) else b

def genetic_algorithm(generations=20, pop_size=6, lower=-10, upper=10):
    population = [random.randint(lower, upper) for _ in range(pop_size)]
    for gen in range(generations):
        new_pop = []
        for _ in range(pop_size):
            child = (select(population) + select(population)) // 2
            if random.random() < 0.1:
                child = random.randint(lower, upper)
            new_pop.append(child)
        population = new_pop
        best = max(population, key=fitness)
        print(f"Gen {gen+1}: Best = {best}, Fitness = {fitness(best)}")

genetic_algorithm()

