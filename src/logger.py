"""
Tanner Wendland
CS5401
11/3/18
"""

"""
Parameters: Config Object
Return: None
This functions is called once to write to a new log file
"""
def log_start(config_values):
    file = open(config_values.LOG, "w")
    file.write("Results Log\nWidth: {}\nHeight: {}\n".format(config_values.WIDTH, config_values.HEIGHT))
    file.write("Pill Density: {}\n".format(config_values.PILL_DENSITY))
    file.write("Wall Density: {}\n".format(config_values.WALL_DENSITY))
    file.write("Fruit Chance: {}\n".format(config_values.FRUIT_CHANCE))
    file.write("Fruit Score: {}\n".format(config_values.FRUIT_SCORE))
    file.write("Seed: {}\n".format(config_values.SEED))
    file.write("Runs: {}\n".format(config_values.RUNS))
    file.write("Evals: {}\n".format(config_values.EVALS))
    file.write("Best Game File: {}\n".format(config_values.BEST_GAME))
    file.write("Log File: {}\n".format(config_values.LOG))
    file.write("Pacman Controller: {}\n".format(config_values.PAC))
    file.write("Pacman Mu: {}\n".format(config_values.pac_population_size))
    file.write("Ghost Mu: {}\n".format(config_values.ghost_population_size))
    file.write("Pac Lambda: {}\n".format(config_values.pac_generation_step))
    file.write("Ghost Lambda: {}\n".format(config_values.ghost_generation_step))
    file.write("Parent Selection: {}\n".format(config_values.parent_selection))
    file.write("Survival Selection: {}\n".format(config_values.survival_selection))
    file.write("Termination: {}\n".format(config_values.termination))
    file.write("Pacman Survival k: {}\n".format(config_values.pac_survival_k))
    file.write("Ghost Survival k: {}\n".format(config_values.ghost_survival_k))
    file.write("Pacman Parsimony Coefficent p: {}\n".format(config_values.pac_parsimony))
    file.write("Ghost Parsimony Coefficent p: {}\n".format(config_values.ghost_parsimony))
    file.write("Evaluations until termination: {}\n".format(config_values.term_evals))
    file.write("Convergence n: {}\n".format(config_values.convergence))
    file.write("Over Selection top x%: {}\n".format(config_values.over_sel))
    file.write("Mutation Probability: {}\n".format(config_values.mutation_rate))
    file.write("Parsimony Upper Limit: {}\n".format(config_values.p_upper))

"""
Parameters: Config Object, integer
Return: None
Write new run number to log file
"""
def log_new_run(PATH, run):
    file = open(PATH, "a")
    file.write("\n\n\nRun {}\n".format(run+1))
    file.close()

"""
Parameters: Config Object, integer, integer
Return: None
Write new fitness eval to log for current run
"""
def log_new_entry(PATH, eval, best_fitness, average_fitness):
    file = open(PATH, "a")
    file.write("{} \t {} \t {}\n".format(eval, average_fitness, best_fitness))
