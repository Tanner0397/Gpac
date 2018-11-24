"""
Tanner Wendland
10/22/18

CS5401 - Gpac
"""

import game
import sys
import configparser
import copy
from config_builder import config_builder
import logger
sys.path.insert(0, 'build')
from fast_tree import tree
from evolution import Evolution

#For testing
from population_member import member

config = configparser.ConfigParser()

if(len(sys.argv) >= 2):
    config.read(sys.argv[1]) #Use another config file
else:
    config.read("config/default.cfg")

#Determine reuns and evals

config_values = config_builder()

#------------------------------------------


"""
Paremters: String
Returns: None
Write string to best game file.
"""
def print_game(world_string):
    BEST_GAME = config_values.BEST_GAME
    file = open(BEST_GAME, "w")
    file.write(world_string)
    file.close()

def worst_game(world_string):
    WORST = config_values.WORST_GAME
    file = open(WORST, "w")
    file.write(world_string)
    file.close()

def main():

    #Create config builder values
    #Game Parameters
    HEIGHT = config_values.HEIGHT
    WIDTH = config_values.WIDTH
    WALL_DENSITY = config_values.WALL_DENSITY
    PILL_DENSITY = config_values.WALL_DENSITY
    FRUIT_CHANCE = config_values.FRUIT_CHANCE
    FRUIT_SCORE = config_values.FRUIT_SCORE
    TIME_MULT = config_values.TIME_MULT

    #Paramters
    RUNS = config_values.RUNS
    EVALS = config_values.EVALS

    #EA Parameters
    MAX_DEPTH = config_values.MAX_DEPTH
    PAC_POP_SIZE = config_values.pac_population_size
    GHOST_POP_SIZE = config_values.ghost_population_size
    PAC_GEN_STEP = config_values.pac_generation_step
    GHOST_GEN_STEP = config_values.ghost_generation_step
    P_SELECT = config_values.parent_selection
    OVER_S = config_values.over_sel
    S_SELECT = config_values.survival_selection
    T_SELECT = config_values.termination
    PAC_SUR_K = config_values.pac_survival_k
    GHOST_SUR_K = config_values.ghost_survival_k
    PAC_P_COEFF = config_values.pac_parsimony
    GHOST_P_COEFF = config_values.ghost_parsimony
    TERM_EVALS = config_values.term_evals
    CONVERGE = config_values.convergence
    MUT_RATE = config_values.mutation_rate
    P_UPPER = config_values.p_upper

    #Paths
    LOG = config_values.LOG
    GAME = config_values.BEST_GAME
    PAC_CONTROLLER = config_values.PAC
    GHOST_CONTOLLER = config_values.GHOST


    best_pac_fitness_all_runs = -1
    best_ghost_fitness_all_runs = 1

    #Starting logging
    logger.log_start(config_values)

    #Create the Game dictinary. Add 2 to compensate for border.
    game_dict = {
                "height" : HEIGHT+2,
                "width" : WIDTH+2,
                "wall_density" : WALL_DENSITY,
                "pill_density" : PILL_DENSITY,
                "fruit_chance" : FRUIT_CHANCE,
                "fruit_score" : FRUIT_SCORE,
                "time_mult" : TIME_MULT,
                }

    for i in range(RUNS):
        #Starting this Run
        print("Starting run {}".format(i+1))
        #Insert now log block...
        logger.log_new_run(LOG, i)

        #Create the EA instance
        EA = Evolution(PAC_POP_SIZE, GHOST_POP_SIZE, PAC_GEN_STEP, GHOST_GEN_STEP, P_SELECT, S_SELECT, T_SELECT, PAC_SUR_K, GHOST_SUR_K, PAC_P_COEFF, GHOST_P_COEFF, OVER_S, TERM_EVALS, CONVERGE, MUT_RATE, game_dict, MAX_DEPTH, P_UPPER)

        best_pac_this_run = EA.get_best_fitness()
        best_ghost_this_run = EA.get_best_ghost_fitness()

        #Better fitnesses may have emerged this run's inital population
        if best_pac_this_run > best_pac_fitness_all_runs:
            #print the game and assign
            print_game(EA.best_world_string())
            #Game contoller
            EA.get_best_member().print_controller(PAC_CONTROLLER)
            best_pac_fitness_all_runs = best_pac_this_run

        #Now for chost
        if best_ghost_this_run < best_ghost_fitness_all_runs:
            #Just print contoller and assign
            worst_game(EA.worst_world_string())
            EA.get_best_ghost().print_controller(GHOST_CONTOLLER)
            best_ghost_fitness_all_runes = best_ghost_this_run

        #Start this runs log
        logger.log_new_entry(LOG, max(PAC_POP_SIZE, GHOST_POP_SIZE), best_pac_this_run, EA.get_average_fitness())

        #Since a fitness evaluation is new defined as a game being player, when creating generations the number of
        #games played is max(pacman_lambda, ghost_lambda)
        for j in range((max(PAC_POP_SIZE, GHOST_POP_SIZE)+max(PAC_GEN_STEP, GHOST_GEN_STEP)), EVALS+1, max(PAC_GEN_STEP, GHOST_GEN_STEP)):
            #Main evolution loop

            print(EA.ghost_population)

            #Create the next generation
            EA.create_generation()

            #Dump pools into their poplation
            EA.pac_dump_pool()
            EA.ghost_dump_pool()

            #Do the survival selection for both populations
            EA.do_pac_survival_selection()
            EA.do_ghost_survival_selection()

            #Log entry
            best_pac_this_run = EA.get_best_fitness()
            best_ghost_this_run = EA.get_best_ghost_fitness()

            #Check to see if any better controllers have emerged from the next generation
            #log entry
            logger.log_new_entry(LOG, j, best_pac_this_run, EA.get_average_fitness())

            if best_pac_this_run > best_pac_fitness_all_runs:
                #print the game and assign
                print_game(EA.best_world_string())
                #Game contoller
                EA.get_best_member().print_controller(PAC_CONTROLLER)
                best_pac_fitness_all_runs = best_pac_this_run

            if best_ghost_this_run < best_ghost_fitness_all_runs:
                #Just print contoller and assign
                worst_game(EA.worst_world_string())
                EA.get_best_ghost().print_controller(GHOST_CONTOLLER)
                best_ghost_fitness_all_runes = best_ghost_this_run

            if EA.determine_termination():
                break

        # #Check to see if a better game has emerged from this inital population
        # if best_fitness_current_run > best_fitness_all_runs:
        #     #print game
        #     print_game(EA.best_world_string())
        #     #Print Controller
        #     EA.get_best_member().print_controller(PAC_CONTROLLER)
        #     best_fitness_all_runs = best_fitness_current_run
        #
        # #initial Log
        # logger.log_new_entry(LOG, POP_SIZE, best_fitness_current_run, EA.get_average_fitness())
        # for j in range(POP_SIZE+GEN_STEP, EVALS+1, GEN_STEP):
        #     #The main Evolution loop
        #     #Create the next generation
        #     for k in range(GEN_STEP):
        #         EA.create_offspring()
        #
        #     #Dump the pool of children into the main population
        #     EA.dump_pool()
        #
        #     #Perform Survival
        #     EA.do_survival_selection()
        #
        #     current_best = EA.get_best_fitness()
        #
        #     #Log entry
        #     logger.log_new_entry(LOG, j, current_best, EA.get_average_fitness())
        #
        #     #If the best game has changed, log it
        #     if current_best > best_fitness_all_runs:
        #         #Print game
        #         print_game(EA.best_world_string())
        #         #Print Controller
        #         EA.get_best_member().print_controller(PAC_CONTROLLER)
        #         best_fitness_all_runs = current_best
        #
        #
        #     #Determine if we can terminate
        #     if EA.determine_termination():
        #         break



if __name__ == "__main__":
    main()
