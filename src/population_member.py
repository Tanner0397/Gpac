"""
Tanner Wendland
CS5401

11/9/18
"""

import sys
sys.path.insert(0, 'build')
from fast_tree import tree
from game import game_map
from random import randint

#Class for member of population. Population emmber has a tree for genome
#Optinal Tree paramter is used to determine to to see if this partiular
#instance is an inital member or is a offspring

#tree = None if this is an intial member. Game-dict is a dictonary that holds the game paratmers to generate game with
class member:
    def __init__(self, game_dict, max_depth, p_upper, p_coeff, pass_tree = None):
        #inital member
        self.p_upper = p_upper
        self.p_coeff = p_coeff
        if pass_tree == None:
            #Generate a tree uing ramped half and half.
            #Grow and Full are all already generated
            self.tree = tree(max_depth)

            #Randomly choose grow or full
            if randint(0, 1) == 0:
                self.tree.grow_wrapper()
            else:
                self.tree.full_wrapper()
        else:
            self.tree = pass_tree

        #Create game paramters to pass
        WIDTH = game_dict["width"]
        HEIGHT = game_dict["height"]
        WALL_DENSITY = game_dict["wall_density"]
        PILL_DENSITY = game_dict["pill_density"]
        FRUIT_CHANCE = game_dict["fruit_chance"]
        FRUIT_SCORE = game_dict["fruit_score"]
        TIME_MULT = game_dict["time_mult"]

        #Tree Created. Create a game of pacman
        temp_game = game_map(HEIGHT, WIDTH, WALL_DENSITY, PILL_DENSITY, FRUIT_CHANCE, FRUIT_SCORE, TIME_MULT)
        temp_game.set_pacman_tree(self.tree)

        #Ghost also use a tree, so instead of using evolved trees, lets generate a random one one
        #for them to use with grow. This will however change in the next assignment.

        ghost_trees=[]
        for g in temp_game.ghost:
            ghost_trees.append(tree(max_depth))
            ghost_trees[-1].grow_wrapper()
        temp_game.set_ghost_trees(ghost_trees)

        #We can now play the game
        temp_game.start_game()
        self.pacman_fitness = temp_game.pacman_fitness()
        self.world_string = temp_game.get_world_string()

        #We must determine if we need to penalize this member
        #for going over the limit
        count = self.tree.count_wrapper()
        if count > self.p_upper:
            penalty = (count - self.p_upper)*self.p_coeff
            self.pacman_fitness = int(self.pacman_fitness-penalty) if self.pacman_fitness > penalty else 0
        #Done evaluating fitness. Delete Game.
        del temp_game

    """
    Parameters: None
    Returns: Int
    Returns the fitness of the member
    """
    def get_fitness(self):
        return self.pacman_fitness

    """
    Parameters: None
    Returns: Tree
    Returns the gp tree of the member
    """
    def get_tree(self):
        return self.tree

    """
    Parameters: None
    Returns: String
    Returns string that holds the world file
    """
    def get_world_string(self):
        return self.world_string


    """
    Parameters: None
    Returns: None
    Print of the controller used
    """
    def print_controller(self, filename):
        self.tree.controller_wrapper(filename)

    #Operators for sorting popualtions
    def __eq__(self, other):
        return self.get_fitness() == other.get_fitness()

    def __ne__(self, other):
        return not self.get_fitness() == other.get_fitness()

    def __ge__(self, other):
        return self.get_fitness() >= other.get_fitness()

    def __gt__(self, other):
        return self.get_fitness() > other.get_fitness()

    def __le__(self, other):
        return self.get_fitness() <= other.get_fitness()

    def __lt__(self, other):
        return self.get_fitness() < other.get_fitness()

    #Dealloc the tree when this member is deleted
    def __del__(self):
        self.tree.delete_tree()

    #For testing
    def __repr__(self):
        return str(self.get_fitness())
