"""
Tanner Wendland
10/27/18

CS5401 - Gpac
"""
from enum import Enum
from random import choice
from random import uniform


"""
A enumeration for the ghost, because the ghost cannot hold their position
"""
class Ghost_Direction(Enum):
    UP = 1
    RIGHT = 2
    DOWN = 3
    LEFT = 4

"""
Game object for ghost. The ghose move around trying to kill pacman. Unlike pacman, the ghost cannot choose to stay. He uses the same tree like structure as pacman
"""
class ghost:
    #Class ID, used to remove occupents from cell
    _ID = 0
    def __init__(self, cell, game):
        self.ID = ghost._ID
        ghost._ID += 1
        self.game = game
        self.gp_tree = None

        self.cell = cell

        #We know where the ghost start, so the direction will be either be up or left
        #this means we must also determine if those positions are actually avaliable
        directions = []

        if game.map[self.cell.row-1][self.cell.col].wall == False:
            directions.append(Ghost_Direction.UP)
        if game.map[self.cell.row][self.cell.col-1].wall == False:
            directions.append(Ghost_Direction.LEFT)

        #Finally set the direction
        self.direction = choice(directions)

    """
    Parameters: Direction Enumeration
    Return: None
    Set direction of ghost
    """
    def set_direction(self, direction):
        self.direction = direction

    """
    Parameter: Tree
    return: None
    Set ghost controller
    """
    def set_tree(self, tree):
        self.gp_tree = tree

    """
    Parameters: None
    Returns: None
    Set the terminals for the tree, using the ghost sensor inputs
    """
    def set_tree_values(self):
        ghost = self.game.closest_ghost(self.cell)
        pac = self.game.distance_to_pac(self.cell)
        self.gp_tree.load_ghost_wrapper(ghost, pac)


    """
    Paramters: None
    returns: None
    This function is called when it is time for a ghost to do his turn.
    """
    def do_turn(self):
        #Create a list of avaliable directions
        #We always have the choice to not move
        directions = []
        if self.cell.row > 1 and self.game.map[self.cell.row-1][self.cell.col].wall == False:
            directions.append(Ghost_Direction.UP)
        if self.cell.row < self.game.rows-2 and self.game.map[self.cell.row+1][self.cell.col].wall == False:
            directions.append(Ghost_Direction.DOWN)
        if self.cell.col > 1 and self.game.map[self.cell.row][self.cell.col-1].wall == False:
            directions.append(Ghost_Direction.LEFT)
        if self.cell.col < self.game.cols-2 and self.game.map[self.cell.row][self.cell.col+1].wall == False:
            directions.append(Ghost_Direction.RIGHT)

        #Now we need to create the state of game after each valid move
        #But for 2a this isn't needed, so i'll simply just set the values randomly
        # the same number of times as the number of directions there are.

        #Ordered pairs, value is index [0] and direction is [1]
        values = []
        for dir in directions:
            #Set tree values of the new inputs
            self.set_tree_values()
            values.append((self.gp_tree.evaluate_tree(), dir))

        #Do to the fact that there are more than one ghost, and the ghost could have the same controller (if not doing the bonus)
        #The ghost could move a one unit. So instead of just picming the first minimum of all the options,
        #If the minimum is not unique we pick one of the minimums at random
        
        minimum = min(values, key=lambda x:x[0])[0]
        indices = [i for i, v in enumerate(values) if v[0] == minimum]
        random_index = choice(indices)
        self.set_direction(values[random_index][1])

    """
    Parmeters: None
    Return: None
    This function is called when the move is confirmed to to be correct. A move is correct when the move when the attempted move is into a cell which is not a wall
    """
    def confirm_move(self):
        self.cell.remove_occupent(self)
        if self.direction == Ghost_Direction.UP:
            self.cell = self.game.map[self.cell.row-1][self.cell.col]
        if self.direction == Ghost_Direction.DOWN:
            self.cell = self.game.map[self.cell.row+1][self.cell.col]
        if self.direction == Ghost_Direction.RIGHT:
            self.cell = self.game.map[self.cell.row][self.cell.col+1]
        if self.direction == Ghost_Direction.LEFT:
            self.cell = self.game.map[self.cell.row][self.cell.col-1]
        self.cell.place_occupents(self)


    def __eq__(self, other):
        return self.ID == other.ID

    def __ne__(self, other):
        return not self.ID == other.ID
