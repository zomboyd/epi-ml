import random
import operator
import numpy as np
import matplotlib.pyplot as plt
plt.style.use('seaborn-whitegrid')


NB_HOUSES = 1000
NB_POPULATIONS = 20
NB_GENERATION = 100
ELITE_RATIO = 0.2
NB_PARENTS = int(NB_POPULATIONS * ELITE_RATIO)
MUTATION_RATE = 0.6
TOURNAMENT_SELECTION_SIZE = 1
NB_QUESTIONS = 8
NB_QUESTIONS_PER_TURN = 3

def generate_random_pop(nb_turns=15):
    pop = []
    turns = list(range(0, nb_turns)) * NB_QUESTIONS_PER_TURN
    for turn in turns:
        rand_q = np.random.randint(0, NB_QUESTIONS)
        thresold = 2 if rand_q == 2 else NB_QUESTIONS
        rand_r = np.random.randint(0, thresold)
        sub_pop = [turn, rand_q, rand_r]
        pop.append(sub_pop)
    pop.sort(key=operator.itemgetter(0))
    return np.array(pop)


def init_population(nb_population=NB_POPULATIONS):
    return np.array([generate_random_pop() for _ in range(0, nb_population)])


def mutate_ind(individual, rate=MUTATION_RATE):
    for k, point in enumerate(individual):
        rand = int(np.random.rand() * 100)
        mutant = np.array(individual, copy=True)
        if rate * 100 > rand:
            first, second = mutant[k], mutant[rand]
            mutant[rand], mutant[k] = second, first
    return np.array(mutant)


def mutation(population):
    new_pop = []
    for i, individual in enumerate(population):
        mutant = mutate_ind(individual, rate=1)
        new_pop.append(mutant)
    return np.array(new_pop)


def rank_population(population):
    return np.random.randint(3, 30, size=population.shape[0])


def fitness_function(population):
    scored_pop = rank_population(population)
    return scored_pop / sum(scored_pop)


def selection(scored_pop):
    scored_ids = list(zip(scored_pop, range(0, len(scored_pop))))
    sorted_ids = sorted(scored_ids, key=operator.itemgetter(0))
    return np.array(sorted_ids[:NB_PARENTS])[:, 1]


def cross_over(parent1, parent2):
    offspring_size = np.random.randint(0, high=len(parent1), size=2)
    start_x, end_x = min(offspring_size), max(offspring_size)
    child_1 = list(parent1[start_x:end_x])
    import pdb; pdb.set_trace()
    child_2 = [gen for gen in parent2 if gen not in child_1]
    return child_1 + child_2


def cross_over_population(population):
    new_pop = []
    for i in range(len(population) - 1):
        child = cross_over(population[i], population[len(population) - i - 1])
        assert len(child) == NB_HOUSES
        new_pop.append(child)
    return np.array(new_pop)


def create_next_generation(pool=None):
    if pool is None:
        return init_population()
    size = NB_POPULATIONS - pool.shape[0]
    if size <= 0:
        return pool
    import pdb; pdb.set_trace()
    # pop = generate_random_population(pool[0], size=(size, NB_HOUSES))
    # return np.concatenate((pop, pool))


def check_population(population):
    error = []
    for pop in population:
        error.append(len(list(set(pop))) == len(pop))
    return error


def parcours(nb_generations=NB_GENERATION, dev=False):
    result = {'errors': []}
    population = init_population()

    for i in range(0, nb_generations):
        scored_pop = fitness_function(population)
        selected_ids = np.array(list(set(selection(scored_pop))))
        best_population = population[np.argmin(scored_pop)]
        # error = np.mean(compute_cumulative_distance(best_population))
        # result['errors'].append(error)
        mating_pool = np.array([population[int(selected_id)]
                                for selected_id in list(selected_ids)])
        children = cross_over_population(mating_pool)
        mutate_population = mutation(mating_pool)
        new_gen = np.concatenate((mutate_population, children))
        size = NB_POPULATIONS - new_gen.shape[0]
        rand_pop = init_population()
        population = np.concatenate((rand_pop, new_gen))
    result['best'] = best_population
    if dev:
        plt.plot(result['errors'], c='r')
        return result
    return best_population


result = parcours(nb_generations=20, dev=True)
