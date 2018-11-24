"""
Tanner Wendland
10/22/18

CS5401 - Gpac
"""

"""
Class for cell of pacman map cell. Can be empty, a wall or contain a pellet.
"""
class cell:
    """
    Constructor Parameters: Interger Row, Interger Column, boolean wall, boolean pellet
    """
    def __init__(self, row, col, wall=None, pellet=None):
        self.row = row
        self.col = col
        self.flood_visited = False
        self.wall = True
        self.pellet = False
        self.fruit = False
        self.occupents = []
        if wall != None:
            self.wall = wall
        if pellet != None:
            self.pellet = pellet

    """
    Parameters: object
    Return: None
    Place object into list that represents that the object is a member of that cell. This is mostly used for pacman and ghost entities
    """
    def place_occupents(self, object):
        self.occupents.append(object)

    """
    Parameters: object
    Return: None
    Remove object from this cell
    """
    def remove_occupent(self, object):
        self.occupents.remove(object)

    """
    Parameters: None
    Returns: String
    Returns a string that represent the rows and cols. Used for hashing
    """
    def __str__(self):
        return str(self.row) + str(self.col)

    """
    Parameters: cell
    Returns: boolean
    Cells are equal if they share the same row and column
    """
    def __eq__(self, other):
        if self.row == other.row and self.col == other.col:
            return True
        return False

    """
    Parameters: cell
    Returns: boolean
    Cells are unequal if they dont share the same row or column
    """
    def __ne__(self, other):
        if self.row != other.row or self.col != other.col:
            return True
        return False

    """
    Function used to hash a cell. Used for sets in an iterative flood fill algorithm.
    """
    def __hash__(self):
        return hash(str(self))
