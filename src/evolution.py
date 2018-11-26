"""
Tanner Wendland

CS 5401

11/9/2018
"""

import sys
sys.path.insert(0, 'build')
from fast_tree import tree
from fast_tree import ghost_tree
from random import uniform
from random import random
from random import choice
from random import sample
from random import randint
from fast_tree import crossover_wrapper
from fast_tree import mutation_wrapper
from game import game_map
from game import RAND_MAX

from population_member import member
from pop_member import population_member as memb

_OVER_SELECTION_TOP = 0.8

class Evolution:
    def __init__(self, pac_mu, ghost_mu, pac_lmda, ghost_lmda, parent_selection, survival_selection, termination, pac_k, ghost_k, pac_p, ghost_p, over_sel, term_evals, n, mutation_rate, game_dict, max_depth, p_upper):
        self.pac_generation_step = pac_lmda
        self.ghost_generation_step = ghost_lmda
        self.pac_population_size = pac_mu
        self.ghost_population_size = ghost_mu
        self.parent_selection = parent_selection
        self.survival_selection = survival_selection
        self.termination = termination
        self.pac_survival_k = pac_k
        self.ghost_survival_k = ghost_k
        self.pac_coefficent_p = pac_p
        self.ghost_coefficent_p = ghost_p
        self.term_evals = term_evals
        self.evals_no_change = n
        self.mutation_rate = mutation_rate
        self.game_dict = game_dict
        self.over_sel = over_sel
        self.p_upper = p_upper

        #max depth of inital tree
        self.max_depth = max_depth

        self.pac_population = []
        self.ghost_population = []

        self.pac_pool = []
        self.ghost_pool = []

        # #Create inital population
        # for i in range(self.population_size):
        #     self.population.append(member(self.game_dict, self.max_depth, self.p_upper, self.coefficent_p))

        #We are not creating trees before creating any games at all, so in order to not create the same tree very time
        #When we create trees with the tree wrapper we must seed the C random number generator used to generate trees

        #Create the initial population of tree members, pacman population
        for i in range(self.pac_population_size):
            temp_tree = tree(self.max_depth)
            #Determine the seed used for intialization
            temp_seed = randint(0, RAND_MAX)
            #Ramped hald and half, choose to either grow or full
            if randint(0, 1) == 0:
                temp_tree.grow_wrapper(temp_seed)
            else:
                temp_tree.full_wrapper(temp_seed)

            self.pac_population.append(memb(temp_tree, self.pac_coefficent_p, self.p_upper))


        #Now create the inital ghost population
        for i in range(self.ghost_population_size):
            temp_tree = ghost_tree(self.max_depth)
            temp_seed = randint(0, RAND_MAX)
            #ramped half and half
            if randint(0, 1) == 0:
                temp_tree.grow_wrapper(temp_seed)
            else:
                temp_tree.full_wrapper(temp_seed)

            self.ghost_population.append(memb(temp_tree, self.ghost_coefficent_p, self.p_upper))

        #Create game paramters to pass
        WIDTH = self.game_dict["width"]
        HEIGHT = self.game_dict["height"]
        WALL_DENSITY = self.game_dict["wall_density"]
        PILL_DENSITY = self.game_dict["pill_density"]
        FRUIT_CHANCE = self.game_dict["fruit_chance"]
        FRUIT_SCORE = self.game_dict["fruit_score"]
        TIME_MULT = self.game_dict["time_mult"]

        #Now create the games and evaluate the fitnesses
        for i in range(max(self.pac_population_size, self.ghost_population_size)):
            temp_game = game_map(HEIGHT, WIDTH, WALL_DENSITY, PILL_DENSITY, FRUIT_CHANCE, FRUIT_SCORE, TIME_MULT)
            temp_game.set_pacman_tree(self.pac_population[i % self.pac_population_size].get_tree())
            temp_game.set_ghost_tree(self.ghost_population[i % self.ghost_population_size].get_tree())
            #Run games
            temp_game.start_game()
            #Set fitnesses. Parasomny is done when setting fitness
            pac_fit = temp_game.pacman_fitness()
            gst_fit = temp_game.ghost_fitness()
            self.pac_population[i % self.pac_population_size].insert_score(pac_fit)
            self.ghost_population[i % self.ghost_population_size].insert_score(gst_fit)
            #Set the score, if the score is used more than one, it will take the average
            self.pac_population[i % self.pac_population_size].set_fitness_to_average()
            self.ghost_population[i % self.ghost_population_size].set_fitness_to_average()

            #We only need to set the world string for the pacman game since this is the game with the score that will appear in the log
            self.pac_population[i % self.pac_population_size].set_world_string(temp_game.get_world_string())
            self.ghost_population[i % self.ghost_population_size].set_world_string(temp_game.get_world_string())



        #self.last_best_fitness = self.get_best_fitness()
        self.current_evals_no_change = 0

        self.current_evals = 0



    #Functions to get the best population member
    """
    Parameters: None
    Returns: Integer
    Returns an integer that is the best fitness
    """
    def get_best_fitness(self):
        return sorted(self.pac_population)[-1].get_fitness()

    """
    Parameters: None
    Returns Member
    Returns athe best member of the population
    """
    def get_best_member(self):
        return sorted(self.pac_population)[-1]

    """
    Parameters: None
    Returns: Ghost populaiton member
    Returns the best controller from the ghost population
    """
    def get_best_ghost(self):
        return sorted(self.ghost_population)[-1]

    """
    Parameters: None
    Returns Float
    Returns fitness of the best ghost populaiotn member
    """
    def get_best_ghost_fitness(self):
        return sorted(self.ghost_population)[-1].get_fitness()

    """
    Parameters: None
    Returns Float
    Returns a float that is the average fitness of the population
    """
    def get_average_fitness(self):
        total = sum([member.get_fitness() for member in self.pac_population])
        return (total / len(self.pac_population))



    #Wrapper functions for parent and survival selection

    """
    Parameters: None
    Returns: Member from pacman population
    Returns a member based on parent selection defined in config file
    """
    def do_pac_parent_selection(self):
        if self.parent_selection == "fitness":
            return self.pac_fitness_proportional()
        elif self.parent_selection == "over":
            return self.pac_over_selection()
        else:
            print("Error: Parent Selection not a defined operator. Exiting.")
            sys.exit()


    """
    Paramters: None
    Returns: Member from ghost population
    Choose what parent selection to do based on config file
    """
    def do_ghost_parent_selection(self):
        if self.parent_selection == "fitness":
            return self.ghost_fitness_proportional()
        elif self.parent_selection == "over":
            return self.ghost_over_selection()
        else:
            print("Error: Parent Selection not a defined operator. Exiting.")
            sys.exit()

    """
    Parameters: None
    Returns: None
    Performs survival based on config file
    """
    def do_pac_survival_selection(self):
        if self.survival_selection == "truncation":
            self.pac_truncation()
            return
        elif self.survival_selection == "k-tourn":
            self.pac_survival_k_tourament()
            return
        else:
            print("Error: Survival selciton not a defined operator. Exiting. ")
            sys.exit()

    """
    Parameters: None
    Returns: None
    Performs survival based on config file
    """
    def do_ghost_survival_selection(self):
        if self.survival_selection == "truncation":
            self.ghost_truncation()
            return
        elif self.survival_selection == "k-tourn":
            self.ghost_survival_k_tourament()
            return
        else:
            print("Error: Survival selciton not a defined operator. Exiting. ")
            sys.exit()

    #Parent Selection Operators
    """
    Parameters: None
    Returns: Member from population
    Returns member based on fitness proportional selection
    """
    def pac_fitness_proportional(self):
        max = sum([member.get_fitness() for member in self.pac_population])
        #Choose a fixed point
        choose_point = uniform(0, max)
        current = 0
        #Scramble population in case all of the fitnesses are 0
        self.pac_population = sorted(self.pac_population, key = lambda x: random())
        for memb in self.pac_population:
            current += memb.get_fitness()
            if current >= choose_point:
                return memb

    """
    Parameters: None
    Returns: Member from population
    Returns memebr based on over selection
    """
    def pac_over_selection(self):
        #Find number of the top x percent
        best_group_num = int(self.pac_population_size*(self.over_sel/100))

        #Sort the population in descending order
        sorted_pop = sorted(self.pac_population)[::-1]

        top_membs = sorted_pop[:best_group_num]
        bottom_membs = sorted_pop[best_group_num:]

        chance = uniform(0, 1)
        if chance <= _OVER_SELECTION_TOP:
            #We choose from the best members
            return choice(top_membs)
        else:
            #Choose someone from, the bottom 100-x%
            return  choice(bottom_membs)

    """
    Parameters: None
    Returns: None
    Perform survival k tournament on population until popualtion size is back to mu
    """
    def pac_survival_k_tourament(self):
        if self.pac_survival_k > len(self.pac_population):
            print("Error: Survival k is larger than current population. Exiting. ")
            sys.exit()
        if self.pac_population_size > len(self.pac_population):
            print("Error: The current population size is less than mu. Exiting. ")
            sys.exit()

        #While mu is not the current population size, do a k tourn until it is
        while self.pac_population_size != len(self.pac_population):
            tourny_list = sample(self.pac_population, self.pac_survival_k)
            sorted_tourn = sorted(tourny_list)
            loser = sorted_tourn[0]
            #We kill the loser of the tournament
            self.pac_population.remove(loser)


    """
    Parameters: None
    Returns: None
    Performs truncation and makes population size back to mu
    """
    def pac_truncation(self):
        if len(self.pac_population) < self.pac_population_size:
            print("Error: Population size less than mu. Exiting.")
            sys.exit()
        members_to_remove = len(self.pac_population) - self.pac_population_size
        sorted_population = sorted(self.pac_population)
        keep = sorted_population[members_to_remove:]
        self.pac_population = keep
        #Scramble population
        self.pac_population = sorted(self.pac_population, key = lambda x: random())

    """
    """
    def ghost_fitness_proportional(self):
        #Since the values are negative, take the minimim of all the fitnesses and then adjust the fitness based on this minimum
        shift_factor = abs(min([member.get_fitness() for member in self.ghost_population]))
        max = sum([(member.get_fitness()+shift_factor) for member in self.ghost_population])
        #Choose a fixed point
        choose_point = uniform(0, max)
        current = 0
        #Scramble population in case all of the fitnesses are 0
        self.ghost_population = sorted(self.ghost_population, key = lambda x: random())
        for memb in self.ghost_population:
            current += memb.get_fitness()+shift_factor
            if current >= choose_point:
                return memb

    """
    """
    def ghost_over_selection(self):
        #Find number of the top x percent
        best_group_num = int(self.ghost_population_size*(self.over_sel/100))

        #Sort the population in descending order
        sorted_pop = sorted(self.ghost_population)[::-1]

        top_membs = sorted_pop[:best_group_num]
        bottom_membs = sorted_pop[best_group_num:]

        chance = uniform(0, 1)
        if chance <= _OVER_SELECTION_TOP:
            #We choose from the best members
            return choice(top_membs)
        else:
            #Choose someone from, the bottom 100-x%
            return  choice(bottom_membs)


    """
    """
    def ghost_survival_k_tourament(self):
        if self.ghost_survival_k > len(self.ghost_population):
            print("Error: Survival k is larger than current population. Exiting. ")
            sys.exit()
        if self.ghost_population_size > len(self.ghost_population):
            print("Error: The current population size is less than mu. Exiting. ")
            sys.exit()

        #While mu is not the current population size, do a k tourn until it is
        while self.ghost_population_size != len(self.ghost_population):
            tourny_list = sample(self.ghost_population, self.ghost_survival_k)
            sorted_tourn = sorted(tourny_list)
            loser = sorted_tourn[0]
            #We kill the loser of the tournament
            self.ghost_population.remove(loser)

    """
    """
    def ghost_truncation(self):
        if len(self.ghost_population) < self.ghost_population_size:
            print("Error: Population size less than mu. Exiting.")
            sys.exit()
        members_to_remove = len(self.ghost_population) - self.ghost_population_size
        sorted_population = sorted(self.ghost_population)
        keep = sorted_population[members_to_remove:]
        self.ghost_population = keep
        #Scramble population
        self.ghost_population = sorted(self.ghost_population, key = lambda x: random())

    """
    Parameters: None
    Returns: None
    This function creates the next generation of population members for both the ghost and the pacmen 
    """
    def create_generation(self):

        #Create the paramters used for the game instance
        WIDTH = self.game_dict["width"]
        HEIGHT = self.game_dict["height"]
        WALL_DENSITY = self.game_dict["wall_density"]
        PILL_DENSITY = self.game_dict["pill_density"]
        FRUIT_CHANCE = self.game_dict["fruit_chance"]
        FRUIT_SCORE = self.game_dict["fruit_score"]
        TIME_MULT = self.game_dict["time_mult"]

        for i in range(max(self.pac_generation_step, self.ghost_generation_step)):
            #calcualte mut_chance for both pacman and ghost
            mut_chance_pac = uniform(0, 1)
            mut_chance_ghost = uniform(0, 1)
            #Determine what children we can create
            if i < self.pac_generation_step:
                #Create pacman tree first
                new_pac_tree = tree(self.max_depth)
                if mut_chance_pac <= self.mutation_rate:
                    parent = self.do_pac_parent_selection()
                    parent_tree = parent.get_tree()
                    new_pac_tree = mutation_wrapper(parent_tree)
                else:
                    #perform crossover
                    base_parent = self.do_pac_parent_selection()
                    doner_parent = self.do_pac_parent_selection()
                    base_tree = base_parent.get_tree()
                    doner_tree = doner_parent.get_tree()
                    new_pac_tree = crossover_wrapper(base_tree, doner_tree)
                #Append members to intermidate pool
                self.pac_pool.append(memb(new_pac_tree, self.pac_coefficent_p, self.p_upper))

            if i < self.ghost_generation_step:
                #Now create the new tree for the ghost contoller
                new_ghost_tree = ghost_tree(self.max_depth)
                if mut_chance_ghost <= self.mutation_rate:
                    parent = self.do_ghost_parent_selection()
                    parent_tree = parent.get_tree()
                    new_ghost_tree = mutation_wrapper(parent_tree)
                else:
                    base_parent = self.do_ghost_parent_selection()
                    doner_parent = self.do_ghost_parent_selection()
                    base_tree = base_parent.get_tree()
                    doner_tree = doner_parent.get_tree()
                    new_ghost_tree = crossover_wrapper(base_tree, doner_tree)
                #append to intermidate pool
                self.ghost_pool.append(memb(new_ghost_tree, self.ghost_coefficent_p, self.p_upper))

        #Usse another for loop with the same upper limits, used to avoid some nasty if structures
        for i in range(max(self.pac_generation_step, self.ghost_generation_step)):
            temp_game = game_map(HEIGHT, WIDTH, WALL_DENSITY, PILL_DENSITY, FRUIT_CHANCE, FRUIT_SCORE, TIME_MULT)
            temp_game.set_pacman_tree(self.pac_pool[i % self.pac_generation_step].get_tree())
            temp_game.set_ghost_tree(self.ghost_pool[i % self.ghost_generation_step].get_tree())
            #Run games
            temp_game.start_game()
            #Set fitnesses. Parasomny is done when setting fitness
            pac_fit = temp_game.pacman_fitness()
            gst_fit = temp_game.ghost_fitness()
            self.pac_pool[i % self.pac_generation_step].insert_score(pac_fit)
            self.ghost_pool[i % self.ghost_generation_step].insert_score(gst_fit)
            #Set the score, if the score is used more than one, it will take the average
            self.pac_pool[i % self.pac_generation_step].set_fitness_to_average()
            self.ghost_pool[i % self.ghost_generation_step].set_fitness_to_average()

            #We only need to set the world string for the pacman game since this is the game with the score that will appear in the log
            self.pac_pool[i % self.pac_generation_step].set_world_string(temp_game.get_world_string())
            self.ghost_pool[i % self.ghost_generation_step].set_world_string(temp_game.get_world_string())

        return

    """
    Parameters: None
    Returns: None
    This function takes all the members in the intermidate children pool and puts them into the population
    """
    def pac_dump_pool(self):
        #Dump the pool of children into the main population
        for x in self.pac_pool:
            self.pac_population.append(x)
        self.pac_pool.clear()
        return

    def ghost_dump_pool(self):
        for x in self.ghost_pool:
            self.ghost_population.append(x)
        self.ghost_pool.clear()
        return

    """
    Paramters: None
    Returns: String
    Returns the world map file of the best member of the population
    """
    def best_world_string(self):
        return self.get_best_member().get_world_string()

    def worst_world_string(self):
        return self.get_best_ghost().get_world_string()


    """
    Parameters: None
    Returns: Boolean
    Returns True if we are to stop the run
    """
    def determine_termination(self):
        if self.termination == "change":
            return self.determine_covergence()
        elif self.termination == "evals":
            return self.determine_evals_term()
        else:
            print("Error: termination not property defined. Exiting.")


    """
    Parameters: None
    Returns: Boolean
    Determine if we have exceeded to number of evaluations. True if to stop
    """
    def determine_evals_term(self):
        self.current_evals += max(self.pac_generation_step, self.ghost_generation_step)
        if self.current_evals >= self.term_evals:
            return True
        return False

    """
    Parameters: None
    Returns: Boolean
    Determines if we have converged. True if we are to stop
    """
    def determine_covergence(self):
        current_best = self.get_best_fitness()
        if current_best != self.last_best_fitness:
            #Ths best fitness changed. Update
            self.current_evals_no_change = 0
            self.last_best_fitness = current_best
        else:
            self.current_evals_no_change += self.generation_step

        if self.current_evals_no_change >= self.evals_no_change:
            return True
        return False
