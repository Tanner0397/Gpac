"""
Tanner Wendland
10/27/18

CS5401 - Gpac
"""

from random import uniform
import sys
from enum import Enum
sys.path.insert(0, 'build')
import fast_tree

#Constatns for terminals


class Direction(Enum):
    NONE = 0
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4

"""
Object for pacman. Pacman has 5 moves. Up, down, left, right, and stay. Pacman uses a tree representation for his controller.
"""
class pacman:
    def __init__(self, cell, game):
        self.cell = cell
        self.direction = Direction.DOWN
        #Pacman needs to 'see' so that he can stop when he bumbs into walls
        self.game = game

        self.gp_tree = None

    """
    Parameters: Direction Enumeration
    Return: None
    Set direction of pacman
    """
    def set_direction(self, direction):
        self.direction = direction

    """
    Parameter: Tree
    return: None
    Set pacman controller
    """
    def set_tree(self, tree):
        self.gp_tree = tree

    """
    Parameters: None
    Returns: None
    This fucntion sets the value of the terminals for the tree. This is needed because the values of the terminals can be different because of sensor inputs
    in part b of this assignment series. But for now, I am generating a random number between 0.01 and 10 for random behavior.
    """
    def set_tree_values(self, cell):
        #tempvalues for wrapper
        pill = float(self.game.closest_pill(cell))
        walls = float(self.game.adjacent_walls(cell))
        fruit = float(self.game.distance_to_fruit(cell))
        ghost = float(self.game.closest_ghost(cell))
        self.gp_tree.load_wrapper(ghost, fruit, pill, walls)

    """
    Paramters: None
    returns: None
    This function is called when it is time for pacman to do his turn. He will generation and evalute the state of the Tree based on the the sensor inputs of any valid direction he can pick
    pacman will use a greedy approch and choose the one with the largest value, thinking it is the best choice for now.
    """
    def do_turn(self):
        #Create a list of avaliable directions
        #We always have the choice to not move
        directions = [Direction.NONE]
        if self.cell.row > 1 and self.game.map[self.cell.row-1][self.cell.col].wall == False:
            directions.append(Direction.UP)
        if self.cell.row < self.game.rows-2 and self.game.map[self.cell.row+1][self.cell.col].wall == False:
            directions.append(Direction.DOWN)
        if self.cell.col > 1 and self.game.map[self.cell.row][self.cell.col-1].wall == False:
            directions.append(Direction.LEFT)
        if self.cell.col < self.game.cols-2 and self.game.map[self.cell.row][self.cell.col+1].wall == False:
            directions.append(Direction.RIGHT)

        #Now we need to create the state of game after each valid move
        #But for 2a this isn't needed, so i'll simply just set the values randomly
        # the same number of times as the number of directions there are.

        #Ordered pairs, value is index [0] and direction is [1]
        values = []
        for dir in directions:
            #Set tree values of the new inputs
            if dir == Direction.NONE:
                self.set_tree_values(self.cell)
            elif dir == Direction.UP:
                self.set_tree_values(self.game.map[self.cell.row-1][self.cell.col])
            elif dir == Direction.DOWN:
                self.set_tree_values(self.game.map[self.cell.row+1][self.cell.col])
            elif dir == Direction.LEFT:
                self.set_tree_values(self.game.map[self.cell.row][self.cell.col-1])
            elif dir == Direction.RIGHT:
                self.set_tree_values(self.game.map[self.cell.row][self.cell.col+1])

            temp = self.gp_tree.evaluate_tree()
            values.append((temp, dir))

        new_dir = min(values, key=lambda x:x[0])[1]
        self.set_direction(new_dir)



    """
    Parmeters: None
    Return: None
    This function is called when the move is confirmed to to be correct. A move is correct when the move when the attempted move is into a cell which is not a wall
    """
    def confirm_move(self):
        self.cell.remove_occupent(self)
        if self.direction == Direction.UP:
            self.cell = self.game.map[self.cell.row-1][self.cell.col]
        if self.direction == Direction.DOWN:
            self.cell = self.game.map[self.cell.row+1][self.cell.col]
        if self.direction == Direction.RIGHT:
            self.cell = self.game.map[self.cell.row][self.cell.col+1]
        if self.direction == Direction.LEFT:
            self.cell = self.game.map[self.cell.row][self.cell.col-1]
        self.cell.place_occupents(self)
