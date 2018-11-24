from libcpp.vector cimport vector
from libcpp.map cimport map
from libcpp.string cimport string

cdef enum:
    MAX_DIM = 100
    MAX_BUILDERS = 4
    NUM_DIRECTIONS = 4

cdef class GENERATOR_CLASS:
    cdef char map[MAX_DIM][MAX_DIM]
    cdef char flood_map[MAX_DIM][MAX_DIM]
    cdef int rows
    cdef int cols
    cdef int walls_desired
    cdef int start_walls
    cdef float pellet_density
    cdef float wall_density
    cdef int[2] pac_pair
    cdef int[2] ghost_pair
    cdef int flood_fill_filled

    cdef int active_builders
    cdef int[4][2] builders
    cdef int[4] builder_directions
    cdef int[4] builder_distance
    cdef int[4] builder_travel
    cdef bint[4]builder_status
    cdef map[string, vector[int]] walls

    cdef int carved

    cdef void flood_fill(self, int row, int col)
    cdef bint connected(self)
    cdef string random_wall_key(self)
    cdef void generate(self)
    cdef void change_direction(self, int index)
    cdef void reset_travel(self, int index)
    cdef bint can_travel(self, int index)
    cdef void move_builder(self, int index)
    cdef bint running_builders(self)
    cdef void step_builders(self)
    cdef void remove_wall(self, int row, int col)
    cdef string string_pair(self, int row, int col)
    cpdef call_gen(self, int seed)
