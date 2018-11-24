"""
Tanner Wendland
10/22/18

CS5401 - Gpac
"""

from cell import cell
from pacman import pacman
from ghost import ghost
from random import randint
from random import choice
from random import uniform
import math
import sys

#Timer for testing
import time

#Import the modules created with Cython
sys.path.insert(0, 'build')
import generate


#RAND_MAX Constant to generate rnadom number from the seeded random number generator from here
RAND_MAX = 2147483647


def taxicab_distance(x1, x2, y1, y2):
    return abs(x2-x1) + abs(y2-y1)


"""
Map object for pacman
"""
class game_map:
    """
    parameters: Interger Rows, Interger Columns, wall density, pill density, fruit change , fruit score, time multiplier
    """
    def __init__(self, rows, cols, wall_density, pill_density, fruit_chance, fruit_score, time_mult):
        self.rows = rows
        self.cols = cols
        self.wall_density = wall_density
        self.pill_density = pill_density
        self.fruit_chance = fruit_chance
        self.fruit_score = fruit_score
        self.time_mult = time_mult
        self.time = int((rows-2)*(cols-2)*time_mult)
        self.score = 0
        self.pills_eaten = 0
        self.fruit_exist = False
        self.fruit_consumed = 0

        #String to be updated as the game progresses. Will be world file when game ends
        self.world_string = ""

        #The standard numner of ghost, will add to a config file later
        self.NUM_GHOST = 3

        #total number of pills in the game after generation
        self.total_pills = 0

        #Map of cells
        self.map = [[cell(i, j) for j in range(cols)] for i in range(rows)]

        #List of pellet coords to check for ditance
        self.pill_dict = {}

        #(y, x) pair for fruit location
        self.fruit_location = (-1, -1)

        #Member constants
        #Cells for pacman and chost
        self.PACMAN_START = self.map[1][1]
        self.GHOST_START = self.map[rows-2][cols-2]

        #Make sure the _CARVED is zero. When doing multiple runs this value needs to be reset
        self.fast_generate()

        #NBow place pacman epnices on board
        self.pac = pacman(self.PACMAN_START, self)
        self.PACMAN_START.place_occupents(self.pac)

        #create ghost
        self.ghost = []
        for i in range(0, self.NUM_GHOST):
            self.ghost.append(ghost(self.GHOST_START, self))
            self.GHOST_START.place_occupents(self.ghost[i])

        #Completed creating ghost
        self.world_string_start()

    def place_object(self, object):
        self.map[object.row][object.col].place_occupents(object)

    def remove_object(self, object):
        self.map[object.row][object.col].remove_occupent(object)

    """
    Parameters: GP Tree
    Return: None
    This function sets the GP tree to the pacman controller for this particular game instance
    """
    def set_pacman_tree(self, tree):
        self.pac.set_tree(tree)

    """
    Parameters: List of GP tree
    Return: None
    This takes a list of the GP trees for the ghost and applies them in the same order as they are passed
    """
    def set_ghost_tree(self, tree):
        # if len(trees) != len(self.ghost):
        #     print("Number of trees for ghost is not equal to number of ghost. Exit.")
        #     sys.exit()
        for i in range(len(self.ghost)):
            self.ghost[i].set_tree(tree)

    """
    Parameters: None
    Return: None
    When this funcstion is called the game starts
    """
    def start_game(self):
        while True:
            result = self.do_turn()
            if not result:
                #Clean up
                break

    """
    Paraeters: game cell
    Return: string
    This fuction returns the coordinals in an (x, y) pair. The rows must be translated to match specification
    """
    def coords_string(self, cell):
        row = (self.rows-cell.row-2)
        col = cell.col-1
        #Return as x y pair
        return "{} {}\n".format(col, row)

    """
    Parameters: None
    Returns: None
    This function simply updates the world string to update the positions of the ghost and pacman
    """
    def world_string_entities(self):
        self.world_string += "m {}".format(self.coords_string(self.pac.cell))
        for i in range(len(self.ghost)):
            self.world_string += "{} {}".format(i+1, self.coords_string(self.ghost[i].cell))

    """
    Parameters: None
    Return: None
    This function is called when we are ready fill out the world string, this is only called once
    since walls and pellets can be definined only once for the visualizer
    """
    def world_string_start(self):
        #height width
        self.world_string += str("{}\n{}\n".format(self.cols-2, self.rows-2))
        #pacman and ghost placements, starting
        self.world_string_entities()

        #starting making walls

        for i in range(1, self.rows-1):
            for j in range(1, self.cols-1):
                if self.map[i][j].wall == True:
                    self.world_string += "w {}".format(self.coords_string(self.map[i][j]))
                elif self.map[i][j].pellet == True:
                    self.world_string += "p {}".format(self.coords_string(self.map[i][j]))

        self.world_string += "t {} {}\n".format(self.time, self.score)

    def get_world_string(self):
        return self.world_string



    """
    Parameters: None
    Return: None
    This function calculates the score based on the numerb of pellets consumed and fruit consumed
    """
    def calc_score(self):
        self.score = int(int((self.pills_eaten/self.total_pills)*100) + int(self.fruit_consumed*self.fruit_score))


    """
    Parameters: None
    Return: None

    This function used a module written in Cython for a speed up

    This function generates a map as close to the wall density as possible, while keeping all cells connected
    This used a series of spawners and builders. Spawners spawn between 1 and 4 builders and buildes will carve out walls
    until they enter a cell which has already been carved out. 1 Spawner is placed where pacman is, to guaretee no walls
    exist where pacman starts. One is also placed where the ghost are to share a similar result. Spawners are added
    until the map is connected and the desired wall density is achived.
    """
    def fast_generate(self):
        seed = randint(0, RAND_MAX)
        fast_generator = generate.GENERATOR_CLASS(self.rows, self.cols, self.pill_density, self.wall_density)
        chars = fast_generator.call_gen(seed)

        for i in range(self.rows):
            for j in range(self.cols):
                char = chr(chars[i][j])
                if char == '#':
                    self.map[i][j].wall = True
                if char == " ":
                    self.map[i][j].wall = False
                if char == '.':
                    self.pill_dict["{} {}".format(i, j)] = (i, j)
                    self.map[i][j].wall = False
                    self.map[i][j].pellet = True
                    self.total_pills+=1
        return
    #Turns

    """
    Parameters: None
    Return: Boolean

    This function will do the next turn in the game. First moving pacman and then moving all the ghost
    After moving these map entities, the score is changed based on pellets and fruit consumed
    by pacman for this particular turn. Game ending criterion are also checked here.
    """
    def do_turn(self):
        #We must check to see if pacman is in th same space as a ghost twice, because
        #only one member can move around at a time
        again = True
        ate = False


        #Pacman and the ghost choose their next movement without execution
        #This is so that the the opponets movements are not read by the other party
        self.pac.do_turn()
        for gst in self.ghost:
            gst.do_turn()

        #Now pacman and the ghost execute their movement they selected
        self.pac.confirm_move()

        #Check to see if pacman ran into ghost
        if any(isinstance(x, ghost) for x in self.pac.cell.occupents):
            self.world_string_entities()
            self.time -= 1
            self.world_string += "t {} {}\n".format(self.time, self.score)
            return False

        for gst in self.ghost:
            gst.confirm_move()

        #Check to see if ghost ran into pacman
        if any(isinstance(x, ghost) for x in self.pac.cell.occupents):
            self.world_string_entities()
            self.time -= 1
            self.world_string += "t {} {}\n".format(self.time, self.score)
            return False

        if self.pac.cell.pellet == True:
            #Remove the pill from the pill dictinary
            self.pill_dict.pop("{} {}".format(self.pac.cell.row, self.pac.cell.col))
            self.pac.cell.pellet = False
            self.pills_eaten += 1
        if self.pac.cell.fruit == True:
            self.fruit_exist = False
            self.pac.cell.fruit = False
            self.fruit_consumed += 1
            ate = True

        #After done with turn, check to see if we are done or to continue on
        self.time -= 1
        self.calc_score()
        self.world_string_entities()
        #Check time game over
        if self.time == 0:
            again = False
        elif self.pills_eaten >= self.total_pills:
            #Time Bonus. Calc Score is called before this so we can do this
            self.score += int(self.time / ((self.rows-2)*(self.cols-2)*self.time_mult))
            again = False

        #Update the fruit lcoation after logging the movment to the world file
        #Because otherwizse the visualizer thinks that a fruit can spawn on top of
        #pacman and breaks, a while it is correct in the program
        if self.fruit_exist == False:
            chance = uniform(0, 1)
            if chance < self.fruit_chance and again and not ate:
                #Create a random fruit
                while not self.fruit_exist:
                    row = randint(1, self.rows-2)
                    col = randint(1, self.cols-2)
                    #If the random cell isnt a wall, not where pacman is, and not where a pellet is
                    if self.map[row][col].wall == False and self.map[row][col] != self.pac.cell and self.map[row][col].pellet == False:
                        self.map[row][col].fruit = True
                        self.world_string += "f {}".format(self.coords_string(self.map[row][col]))
                        self.fruit_exist = True
                        self.fruit_location = (row, col)
        self.world_string += "t {} {}\n".format(self.time, self.score)
        return again

    """
    Parameters: None
    Return: Score integer
    The fitness of this game is simply the score. The bigger the better.
    """
    def pacman_fitness(self):
        return int(self.score)

    """
    Paramters: None
    Return Score Integer
    The fitness for the ghost is the negation of pacmans score. The ghost want to minimize this
    """
    def ghost_fitness(self):
        return -int(self.score)

    """
    Parameters: cell from map
    Returns: int
    Returns the taxiba distance between the cell passed and the closest_pill
    """
    def closest_pill(self, cell):
        #Set min to the largest distance possible
        min = taxicab_distance(1, self.rows-2, 1, self.cols-2)
        y = cell.row
        x = cell.col
        for key, value in self.pill_dict.items():
            dist = taxicab_distance(x, value[1], y, value[0])
            if dist < min:
                min = dist
        return min

    """
    Parameters: cell in map
    Returns: Int
    Returns number of walls directly adjacent to the cell passed
    """
    def adjacent_walls(self, cell):
        row = cell.row
        col = cell.col
        count = 0

        #Do we count the outside wall? I think so.
        if self.map[row-1][col].wall == True:
            count+=1
        if self.map[row+1][col].wall == True:
            count+=1
        if self.map[row][col-1].wall == True:
            count+=1
        if self.map[row][col+1].wall == True:
            count+=1

        return count


    """
    Parameters: cell in map
    Returns: Int
    Returns distance from cell to fruit on map. Returns 0 if the fruit does not exist
    """
    def distance_to_fruit(self, cell):
        y = cell.row
        x = cell.col
        if self.fruit_location == (-1, -1):
            return 0
        return taxicab_distance(x, self.fruit_location[1], y, self.fruit_location[0])


    """
    parameters: cell in map
    Returns: Int
    Returns distance from cell to the closed ghost
    """
    def closest_ghost(self, cell):
        x = cell.col
        y = cell.row
        min = taxicab_distance(1, self.rows-2, 1, self.cols-2)
        for ght in self.ghost:
            #Prevent a ghost from saying the min distance to a ghost it 0 (itself)
            if ght.cell != cell:
                dist = taxicab_distance(x, ght.cell.col, y, ght.cell.row)
                if dist < min:
                    min = dist
        return min

    """
    Parameters: cell in map
    Returns: Int
    Returns the distance form to cell to pacman's position
    """
    def distance_to_pac(self, cell):
        x1 = cell.col
        y1 = cell.row

        x2 = self.pac.cell.col
        y2 = self.pac.cell.row
        return taxicab_distance(x1, x2, y1, y2)


    #For testing
    def map_string(self):
        string = "Score : {}\n Time: {}\n".format(self.score, self.time)
        for i in range(self.rows):
            for j in range(self.cols):
                if self.map[i][j].wall == True:
                    string += "#"
                elif any(isinstance(x, pacman) for x in self.map[i][j].occupents):
                    string += 'C'
                elif any(isinstance(x, ghost) for x in self.map[i][j].occupents):
                    string += 'G'
                elif self.map[i][j].fruit == True:
                    string += 'F'
                elif self.map[i][j].pellet == True:
                    string += '.'
                elif self.map[i][j].wall == False:
                    string += " "
            string += "\n"
        return string
