"""
Tanner Wendland
CS5401
11/3/18
"""

import configparser
from random import random
import random
import time
import sys

config = configparser.ConfigParser()

if(len(sys.argv) >= 2):
    config.read(sys.argv[1]) #Use another config file
else:
    config.read("config/default.cfg")



class config_builder:
    def __init__(self):
        try:
            self.RUNS = int(config.get("PARAMETERS", "runs"))
        except :
            print("runs undefined under PARAMETERS")

        try:
            self.EVALS = int(config.get("PARAMETERS", "evals"))
        except:
            print("evals undefined under PARAMETERS")

        #Determine game paremeter

        try:
            self.WIDTH = int(config.get("GAME", "width"))
        except:
            print("width undefined under GAME")

        try:
            self.HEIGHT = int(config.get("GAME", "height"))
        except:
            print("height undefined under GAME")

        try:
            self.PILL_DENSITY = float(config.get("GAME", "pill_density"))
        except:
            print("pill_density undefined under GAME")

        try:
            self.WALL_DENSITY = float(config.get("GAME", "wall_density"))
        except:
            print("wall_density undefined under GAME")

        try:
            self.FRUIT_CHANCE = float(config.get("GAME", "fruit_chance"))
        except:
            print("fruit_chance undefined under GAME")

        try:
            self.FRUIT_SCORE = int(config.get("GAME", "fruit_score"))
        except:
            print("height undefined under GAME")

        try:
            self.TIME_MULT = float(config.get("GAME", "time_mult"))
        except:
            print("time_mult undefined under GAME")

        try:
            if config.get("GAME", "seed") != "":
                self.SEED = int(config.get("GAME", "seed"))
                random.seed(self.SEED)
            else:
                sd = int(time.time())
                random.seed(sd)
                self.SEED = sd
        except:
            print("seed undefined under GAME")

        #------------ PARAMETERS FOR GP ---------------------

        try:
            self.MAX_DEPTH = int(config.get("PARAMETERS", "max_depth"))
        except:
            print("max_depth undefined under PARAMETERS")


        #---------------------- PATHING ---------------------

        try:
            self.BEST_GAME = config.get("PATH", "best_game")
        except:
            print("best_game undefined under PATH")

        try:
            self.WORST_GAME = config.get("PATH", "worst_game")
        except:
            print("worst_game undefined under PATH")

        try:
            self.LOG = config.get("PATH", "log_path")
        except:
            print("log undefined under PATH")

        try:
            self.PAC = config.get("PATH", "pac_controller")
        except:
            print("pac_controller undefined under PATH")

        try:
            self.GHOST = config.get("PATH", "ghost_controller")
        except:
            print("ghost_controller undefined under PATH")

        #---------------EA PARAMTERS

        try:
            self.pac_population_size = int(config.get("PARAMETERS", "pac_mu"))
        except:
            print("pac_mu undefined under PARAMETERS")

        try:
            self.ghost_population_size = int(config.get("PARAMETERS", "ghost_mu"))
        except:
            print("ghost_mu undefined under PARAMETERS")

        try:
            self.pac_generation_step = int(config.get("PARAMETERS", "pac_lambda"))
        except:
            print("pac_lambda undefined under PARAMETERS")

        try:
            self.ghost_generation_step = int(config.get("PARAMETERS", "ghost_lambda"))
        except:
            print("ghost_lambda undefined under PARAMETERS")

        try:
            self.parent_selection = config.get("PARAMETERS", "parent")
        except:
            print("parent undefined under PARAMETERS")

        try:
            self.survival_selection = config.get("PARAMETERS", "survival")
        except:
            print("survival undefined under PARAMETERS")

        try:
            self.termination = config.get("PARAMETERS", "termination")
        except:
            print("termination undefined under PARAMETERS")

        try:
            self.pac_survival_k = int(config.get("PARAMETERS", "pac_survival_k"))
        except:
            print("pac_survival_k undefined under PARAMETERS")

        try:
            self.ghost_survival_k = int(config.get("PARAMETERS", "ghost_survival_k"))
        except:
            print("ghost_survival_k undefined under PARAMETERS")

        try:
            self.pac_parsimony = float(config.get("PARAMETERS", "pac_p"))
        except:
            print("pac_p undefined under PARAMETERS")

        try:
            self.ghost_parsimony = float(config.get("PARAMETERS", "ghost_p"))
        except:
            print("ghost_p undefined under PARAMETERS")

        try:
            self.term_evals = int(config.get("PARAMETERS", "term_evals"))
        except:
            print("term_evals undefined under PARAMETERS")

        try:
            self.convergence = int(config.get("PARAMETERS", "n"))
        except:
            print("n undefined under PARAMETERS")

        try:
            self.over_sel = int(config.get("PARAMETERS", "x"))
        except:
            print("x undefined under PARAMETERS")

        try:
            self.mutation_rate = float(config.get("PARAMETERS", "mutation_rate"))
        except:
            print("mutation_rate undefined under PARAMETERS")

        try:
            self.p_upper = float(config.get("PARAMETERS", "p_upper"))
        except:
            print("p_upper undefined under PARAMETERS")
