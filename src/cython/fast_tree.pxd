"""
Tanner Wendland
CS5401
11/12/18
"""

from libcpp.vector cimport vector
from libcpp.string cimport string

cdef enum:
    #Base
    _EMPTY = 0
    _TERMINAL = 1

    #Terminal types for pacman
    _CONSTANT = 2
    _GHOST = 3
    _PILL = 4
    _WALLS = 4
    _FRUIT = 5


    _FUNCITON = 6

    #Function Types
    _ADDITION = 7
    _MULTIPLICATION = 8
    _SUBTRACTION = 9
    _DIVISION = 10
    _RANDOM = 11

    #Terminals for ghost tree
    _PACMAN = 12

    #Constants maximum
    _CONST_MAX = 20

cdef struct node:
    float value
    node* left_child
    node* right_child
    node* parent
    int type

cdef node* create_node(float val, int type)
cdef void add_children(node* parent, node* left, node* right)
cdef node* recursive_copy(node* nd)
cdef void delete_nodes(node* nd)
cdef void print_tree(node* nd, int spaces)
cdef float get_value(node* nd)
cdef tree subtree_crossover(tree first, tree second)
cdef tree subtree_mutation(tree the_tree)
cdef void print_controller(node* nd, int spaces, file)

cdef class tree:
    cdef int max_depth
    cdef node* root
    cdef int[2] FUNCTION_OR_TERMINAL
    cdef int[5] TYPE_OF_TERMINAL
    cdef int[5] TYPE_OF_FUNCTION
    cdef int _TOTAL_TERMINALS
    cdef int _TOTAL_FUNCTIONS
    cdef int num_term_types
    cdef int num_func_types
    #Vector of terminals
    cdef vector[node*] terminals

    cdef int depth(self, node* nd, int depth)
    cdef void grow(self, node* nd)
    cdef void full(self, node* nd)
    cdef void copy_tree(self, tree copy_from)
    cdef load_terminals(self, float ghost, float fruit, float pill, float walls)
    cdef node* random_node(self, node* nd)
    cdef generate_terminal_vector(self, node* nd)
    cdef int count_nodes(self, node* nd, sum)
    # def delete_tree(self)
    # def grow_wrapper(self)
    # def full_wrapper(self)
    # def evaluate_tree(self)
    # def testing_wrapper(self)
    # def print_wrapper(self)
