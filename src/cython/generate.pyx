"""
Tanner Wendland
CS5401

Cython function for map generation
"""

# distutils: language = c++

cimport numpy as np
from libcpp cimport bool
import cython
from cython cimport cdivision, boundscheck
from libc.string cimport memset
from libcpp.vector cimport vector
from libcpp.map cimport map
from unordered_map cimport unordered_map
from stringstream cimport stringstream
from libcpp.string cimport string
from cython cimport tuple
from cpython.exc cimport PyErr_CheckSignals
from cython.operator cimport dereference
from cython.operator cimport postincrement
from libc.stdlib cimport RAND_MAX

import sys

#C rands
from libc.stdlib cimport rand
from libc.stdlib cimport srand


cdef int UP = 1
cdef int DOWN = 2
cdef int LEFT = 3
cdef int RIGHT = 4

cdef char WALL = '#'
cdef char EMPTY = ' '
cdef char PILL = '.'
cdef char GHOST = 'G'

cdef char UNMARKED = 'u'
cdef char MARKED = 'm'

cdef class GENERATOR_CLASS:

    def __cinit__(self, int rows, int cols, float pellet_density, float wall_density):
        cdef string key
        cdef vector[int] temp
        self.rows = rows
        self.cols = cols
        self.pellet_density = pellet_density
        self.wall_density = wall_density
        self.start_walls = (rows-2)*(cols-2)
        self.walls_desired = int(self.start_walls*self.wall_density)

        self.pac_pair[:] = [1, 1]
        self.ghost_pair[:] = [rows-2, cols-2]
        self.builder_travel[:] = [0, 0, 0, 0]
        self.builder_distance[:] = [0, 0, 0, 0]
        self.builder_status[:] = [False, False, False, False]

        memset(self.map, WALL, sizeof(self.map[0][0]) * MAX_DIM * MAX_DIM)
        memset(self.flood_map, UNMARKED, sizeof(self.flood_map[0][0]) * MAX_DIM * MAX_DIM)

        for i in range(1, self.rows-2):
            for j in range(1, self.cols-2):
                temp.clear()
                key = self.string_pair(i, j)
                temp.push_back(i)
                temp.push_back(j)
                self.walls[key] = temp

        #Pacman and ghost squares are always empty
        #self.map[self.pac_pair[0]][self.pac_pair[1]] = EMPTY
        #self.map[self.ghost_pair[0]][self.ghost_pair[1]] = EMPTY
        self.remove_wall(self.pac_pair[0], self.pac_pair[1])
        self.remove_wall(self.ghost_pair[0], self.ghost_pair[1])


        self.flood_fill_filled = 0


    """
    Parameters: int int
    Returns: none
    Counts the number of cells avaliable starting from the first call at (row, col)
    """
    cdef void flood_fill(self, int row, int col):
        if row == 0 or col == 0 or row == self.rows-1 or col == self.cols-1:
            return
        if self.map[row][col] == WALL:
            return
        if self.flood_map[row][col] == MARKED:
            return

        self.flood_fill_filled += 1
        self.flood_map[row][col] = MARKED
        self.flood_fill(row+1, col)
        self.flood_fill(row-1, col)
        self.flood_fill(row, col-1)
        self.flood_fill(row, col+1)


    """
    Parameters: None
    Returns: Boolean
    returns true if the map is connected, otherwise false
    """
    cdef bint connected(self):
        cdef bint result = False
        self.flood_fill(1, 1)
        result = self.flood_fill_filled == self.carved
        #We have our result, now lets reset the flood fill
        #print("{} {}".format(self.carved, self.flood_fill_filled))
        self.flood_fill_filled = 0
        memset(self.flood_map, UNMARKED, sizeof(self.flood_map[0][0]) * MAX_DIM * MAX_DIM)
        return result

    """
    Parameters: int int
    Returns: String
    This returns a string that represents the key for a wall located at (row, col)
    """
    cdef string string_pair(self, int row, int col):
        cdef stringstream string_key
        cdef string temp
        string_key.push(b'( ').push(row).push(b',').push(col).push(b')')
        #string_key.push(row)
        temp = string_key.to_string()
        return temp


    """
    Parameters: None
    Returns: String
    Returns random key from the wall map
    """
    @cdivision
    @boundscheck(False)
    cdef string random_wall_key(self):
        it = self.walls.begin()
        cdef string random_key
        cdef int step = rand() % self.walls.size()
        for i in range(step):
            postincrement(it)
        random_key = dereference(it).first
        return random_key


    """
    Parameters: None
    Returns: none
    Generate the map using up to four builders at a time. Initially between 2 and 4 builders
    is allocaed to the map. 1 is guarteed to spawn where the pacman would start and where
    all the ghost start. These builders will run until they meet a an empty cell. (Even if the cell was made by that builder)
    . After the intital builders are made for the pacman and ghost we check to see if the map is conneced and if we have meet the desired wall
    density. If neigher have been satisified we generate between 1 and 4 new spaners and place them around an adjacent wall
    and run those builders to completion. We do this until the map is connected and we have meet our wall requirment.
    Note that if the wall  density is high and the maps are large, it is possible that the true wall density
    could be below that it was specifed since builders can carve into them selves
    """
    @cdivision
    @boundscheck(False)
    cdef void generate(self):
        #We need to make some builders. For Pacman and the ghost
        #Choose between 2 and 4 of them

        #Used for after inital generation
        cdef int new_builders

        #Used for getting the random wall positions
        cdef int wall_index
        cdef vector[int] wall_v
        cdef vector[vector[int]] neighbors
        cdef int random_neighbor_index
        cdef vector[int] temp

        cdef float chance

        self.active_builders = rand() % 3 + 2


        if self.active_builders >= 2:
            self.builders[0][:] = self.pac_pair
            self.builder_directions[0] = DOWN if rand() % 2 == 0 else RIGHT
            self.builder_status[0] = True
            self.builders[1][:] = self.ghost_pair
            self.builder_directions[1] = UP if rand() % 2 == 0 else LEFT
            self.builder_status[1] = True
        #We made three, choose randomly who it does to
        if self.active_builders == 3:
            give_pac = rand() % 2
            if give_pac == 1:
                self.builders[2][:] = self.pac_pair
                self.builder_directions[2] = DOWN if self.builder_directions[0] == RIGHT else RIGHT
                self.builder_status[2] = True
            else:
                self.builders[2][:] = self.ghost_pair
                self.builder_directions[2] = UP if self.builder_directions[1] == LEFT else LEFT
                self.builder_status[2] = True
        elif self.active_builders == 4:
            self.builders[2][:] = self.pac_pair
            self.builder_directions[2] = DOWN if self.builder_directions[0] == RIGHT else RIGHT
            self.builder_status[2] = True
            self.builders[3][:] = self.ghost_pair
            self.builder_directions[3] = UP if self.builder_directions[1] == LEFT else LEFT
            self.builder_status[3] = True


        #Lets give the builders they're inital distance to travel
        for i in range(MAX_BUILDERS):
            if self.builder_status[i]:
                self.reset_travel(i)

        #intial builder stepper
        while self.running_builders():
            self.step_builders()

        #self.print_map()

        #While the map is not connected or we have too many walls
        while not self.connected() or (self.start_walls - self.carved) >= self.walls_desired:
            #Now we must create another group of builders, and run them to completion
            #Randomly create between 1 nd 4 spawners
            new_builders = rand() % MAX_BUILDERS + 1
            neighbors.clear()
            #I there are enough walls to work with, create these new builders
            if self.walls.size() >= new_builders:
                #Pick a rnadom wall and remove it from the board
                wall_key = self.random_wall_key()
                wall_it = self.walls.find(wall_key)
                wall_v = dereference(wall_it).second
                self.remove_wall(wall_v[0], wall_v[1])
                #Place builders to random adjacent cells of this cell that was carved
                #For some reason I cant push a vector into a vector like vector[int](i, j, k)...
                if wall_v[0] > 1 and self.map[wall_v[0]-1][wall_v[1]] == WALL:
                    temp.clear()
                    temp.push_back(wall_v[0]-1)
                    temp.push_back(wall_v[1])
                    temp.push_back(UP)
                    neighbors.push_back(temp)
                if wall_v[0] <= self.rows-2 and self.map[wall_v[0]+1][wall_v[1]] == WALL:
                    temp.clear()
                    temp.push_back(wall_v[0]+1)
                    temp.push_back(wall_v[1])
                    temp.push_back(DOWN)
                    neighbors.push_back(temp)
                if wall_v[1] > 1 and self.map[wall_v[0]][wall_v[1]-1] == WALL:
                    temp.clear()
                    temp.push_back(wall_v[0])
                    temp.push_back(wall_v[1]-1)
                    temp.push_back(LEFT)
                    neighbors.push_back(temp)
                if wall_v[1] < self.rows-2 and self.map[wall_v[0]][wall_v[1]+1] == WALL:
                    temp.clear()
                    temp.push_back(wall_v[0])
                    temp.push_back(wall_v[1]+1)
                    temp.push_back(RIGHT)
                    neighbors.push_back(temp)

                if neighbors.size() == 0:
                    #This wall was alone, do the next loop
                    continue

                #we have placed at least one builder
                for i in range(new_builders):
                    #Choose a neigthbors
                    if neighbors.size() != 0:
                        random_neighbor_index = rand() % neighbors.size()
                        #Now reactivate the builder
                        self.builders[i][:] = [neighbors[random_neighbor_index][0], neighbors[random_neighbor_index][1]]
                        self.builder_status[i] = True
                        self.builder_directions[i] = neighbors[random_neighbor_index][2]
                        self.reset_travel(i)
                        self.remove_wall(neighbors[random_neighbor_index][0], neighbors[random_neighbor_index][1])
                        neighbors[random_neighbor_index] = neighbors.back()
                        neighbors.pop_back()
                while self.running_builders():
                    self.step_builders()

            else:
                #There are more builders wanted than walls, so just these walls empty without creating builders.
                it = self.walls.begin()
                for i in range(self.walls.size()):
                    wall_v = dereference(it).second
                    self.map[wall_v[0]][wall_v[1]] = EMPTY
                    self.carved += 1
                    postincrement(it)

        #place pills now that the main generation is completed
        for i in range(1, self.rows-1):
            for j in range(1, self.cols-1):
                chance = float(float(rand()) / float(RAND_MAX))
                if (i != 1 and j != 1) and (i != self.rows-2 and j != self.cols-2) and self.map[i][j] != WALL and chance <= self.pellet_density:
                    self.map[i][j] = PILL



    """
    Parameters: index
    Returns: None
    Set the new direction of the builder at the index
    """
    cdef void change_direction(self, int index):
        cdef int dir = self.builder_directions[index]
        cdef int row = self.builders[index][0]
        cdef int col = self.builders[index][1]

        if dir == UP or dir == DOWN:
            if col > 1 and col < self.cols-2:
                self.builder_directions[index] = LEFT if rand() % 2 == 0 else RIGHT
            elif col > 1:
                self.builder_directions[index] = LEFT
            else:
                self.builder_directions[index] = RIGHT
        else:
            if row > 1 and row < self.rows-2:
                self.builder_directions[index] = UP if rand() % 2 == 0 else DOWN
            elif row > 1:
                self.builder_directions[index] = UP
            else:
                self.builder_directions[index] = DOWN

        self.reset_travel(index)
        return

    """
    Parameters: int index
    Returns: None
    Resets the distance and travel paramaters for the builder at the index
    """
    @cdivision
    @boundscheck(False)
    cdef void reset_travel(self, int index):
        cdef int dir  = self.builder_directions[index]
        self.builder_travel[index] = 0
        if dir == UP or dir == DOWN:
            self.builder_distance[index] = rand() % (self.rows-2) + 2
        else:
            self.builder_distance[index] = rand() % (self.cols-2) + 2
        return

    """
    Parameters: index
    Returns: boolean
    Returns True if the builder at the index can move, otherwise false
    """
    cdef bint can_travel(self, int index):
        if self.builder_travel[index] < self.builder_distance[index]:
            return True
        return False

    """
    Parameters: None
    Returns: None
    This function steps all the builders one time  if they are  active
    """
    cdef void step_builders(self):
        for i in range(MAX_BUILDERS):
            if self.builder_status[i]:
                self.move_builder(i)


    """
    Parameters: None
    Returns: index
    Move the builder at index i
    """
    cdef void move_builder(self, int index):
        cdef int* builder = self.builders[index]
        cdef bint result = self.can_travel(index)
        cdef int dir = self.builder_directions[index]
        cdef bint moved = False

        if result and dir == UP and builder[0] != 1:
            builder[0] = builder[0] - 1
            moved = True
        elif result and dir == DOWN and builder[0] != self.rows-2:
            builder[0] = builder[0] + 1
            moved = True
        elif result and dir == RIGHT and builder[1] != self.cols-2:
            builder[1] = builder[1] + 1
            moved = True
        elif result and dir == LEFT and builder[1] != 1:
            builder[1] = builder[1] - 1
            moved = True


        if moved:
            self.builder_travel[index] += 1
            #Before we set this to be a empty cell, we need to see if this cell we moved to
            #is an empty cell first.
            if self.map[builder[0]][builder[1]] != WALL:
                #Set inactive
                self.builder_status[index] = False
            else:
                self.builder_travel[index] += 1
                #self.map[builder[0]][builder[1]] = EMPTY
                self.remove_wall(builder[0], builder[1])
                #Lets check and see of the 90 degree neightbors are empty or not
                #If tehy are empty, then lets stop the builder
                if (dir == UP or dir == DOWN) and (self.map[builder[0]][builder[1]+1] != WALL or self.map[builder[0]][builder[1]-1] != WALL):
                    self.builder_status[index] = False
                elif (dir == LEFT or dir == RIGHT) and (self.map[builder[0]+1][builder[1]] != WALL or self.map[builder[0]+1][builder[1]] != WALL):
                    self.builder_status[index] = False
        else:
            #We didnt move, lets change direction
            self.change_direction(index)
        return


    """
    Parameters: int, int
    Returns: None
    Removes a wall if it esist
    """
    cdef void remove_wall(self, int row, int col):
        cdef string key = self.string_pair(row, col)
        if self.map[row][col] == EMPTY:
            return
        self.map[row][col] = EMPTY
        self.carved += 1
        #Remove wall from wall map
        self.walls.erase(key)

    """
    Parameters: None
    Returns: boolean
    Return true of the builders are still active, false otherwise
    """
    cdef bint running_builders(self):
        for i in range(MAX_BUILDERS):
            if self.builder_status[i]:
                return True
        return False

    """
    Paramters: Seed
    Returns: 2d list of chacters converted form 2s character array
    Generate the map
    """
    cpdef call_gen(self, int seed):
        srand(seed)
        self.generate()
        return self.map
