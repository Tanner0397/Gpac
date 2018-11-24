"""
Tanner Wendland
CS5401

11/19/18
"""

import sys
sys.path.insert(0, 'build')
from fast_tree import tree
from fast_tree import ghost_tree

class population_member:
    def __init__(self, tree, coefficent_p, p_upper, fitness=None, world_string=None):
        self.tree = tree
        self.fitness = fitness if fitness != None else -1
        self.coefficent_p = coefficent_p
        self.p_upper = p_upper
        self.world_string = world_string if world_string != None else ""
        #To be used when one population either has a larger inital population or generational step size
        self.games_played_score = []

    def get_tree(self):
        return self.tree

    def get_world_string(self):
        return self.world_string

    def get_fitness(self):
        return self.fitness

    def set_fitness(self, val):
        penalty = 0
        count = self.tree.count_wrapper()
        if count > self.p_upper:
            penalty = (count - self.p_upper)*self.coefficent_p
        if isinstance(self.tree, ghost_tree):
            #No need to check, ghost score can be any negative
            self.fitness = val - penalty
        else:
            #Pacman cannot have a negative score, so check for that
            self.fitness = val - penalty if val > penalty else 0
        return

    def set_world_string(self, string):
        self.world_string = string

    def insert_score(self, val):
        self.games_played_score.append(val)

    def set_fitness_to_average(self):
        if len(self.games_played_score) == 0:
            return
        else:
            self.set_fitness((sum(self.games_played_score)/(len(self.games_played_score))))


    """
    Parameters: None
    Returns: None
    Print of the controller used
    """
    def print_controller(self, filename):
        self.tree.controller_wrapper(filename)

    #Operators for sorting popualtions
    def __eq__(self, other):
        m, o = self.get_fitness(), other.get_fitness()
        return m == o

    def __ne__(self, other):
        m, o = self.get_fitness(), other.get_fitness()
        return not m == o

    def __ge__(self, other):
        m, o = self.get_fitness(), other.get_fitness()
        return m >= o

    def __gt__(self, other):
        m, o = self.get_fitness(), other.get_fitness()
        return m > o

    def __le__(self, other):
        m, o = self.get_fitness(), other.get_fitness()
        return m <= o

    def __lt__(self, other):
        m, o = self.get_fitness(), other.get_fitness()
        return m < o

    #Dealloc the tree when this member is deleted
    def __del__(self):
        self.tree.delete_tree()

    #For testing
    def __repr__(self):
        return str(self.get_fitness())
