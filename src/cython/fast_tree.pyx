"""
Tanner Wendland
CS 5401

11/12/18
"""

import cython
from cython cimport cdivision, boundscheck
from cython.operator cimport dereference
from libcpp.vector cimport vector
from libc.stdlib cimport rand
from libc.stdlib cimport RAND_MAX
from libc.stdlib cimport srand
from libc.stdlib cimport malloc
from libc.stdlib cimport free
from libc.time cimport time
from libcpp.string cimport string
import sys

from libc.stdlib cimport srand

"""
Parameters: float int
Returns: node*
Create a new node*  and sets it type and value
"""
cdef node* create_node(float val, int type):
    cdef node* new_node = <node*>malloc(sizeof(node))

    dereference(new_node).value = val
    dereference(new_node).type = type
    #Make the parent NULL by default. If this is to have a parent, add_children is called
    dereference(new_node).parent = NULL
    dereference(new_node).left_child = NULL
    dereference(new_node).right_child = NULL
    return new_node

"""
Parameters: node*, node*, node*
Returns: none
Sets the children of parent to left and right, and sets the parent of left and right to parent
"""
cdef void add_children(node* parent, node* left, node* right):
    dereference(parent).left_child = left
    dereference(parent).right_child = right
    dereference(left).parent = parent
    dereference(right).parent = parent

"""
Parameters: Node*
Returns: Node*
Returns a copy of a node with copies of the children
"""
cdef node* recursive_copy(node* nd):
    cdef node* new_node
    cdef node* left
    cdef node* right

    if nd == NULL:
        return NULL
    new_node = create_node(dereference(nd).value, dereference(nd).type)

    #This node has children
    if dereference(nd).left_child != NULL or dereference(nd).right_child != NULL:
        left = recursive_copy(dereference(nd).left_child)
        right = recursive_copy(dereference(nd).right_child)
        add_children(new_node, left, right)

    return new_node

"""
Parameters: node*
Returns: None
Deletes node* from memoery using a tree traversal
"""
cdef void delete_nodes(node* nd):
    if nd == NULL:
        return

    delete_nodes(dereference(nd).left_child)
    delete_nodes(dereference(nd).right_child)
    free(nd)

#Print for testing
cdef void print_tree(node* nd, int spaces):
  ch = ""
  cdef int type
  my_str = ""

  if nd != NULL:
      type = dereference(nd).type
      if type == _ADDITION:
          ch = '+'
      if type == _MULTIPLICATION:
          ch = '*'
      if type == _SUBTRACTION:
          ch = '-'
      if type == _DIVISION:
          ch = '/'
      if type == _RANDOM:
          ch = 'R'
      if type == _GHOST:
          ch = 'g'
      if type == _WALLS:
          ch = 'w'
      if type == _PILL:
          ch = 'p'
      if type == _FRUIT:
          ch = 'f'
      if type == _CONSTANT:
          ch = str(dereference(nd).value)
      if type == _PACMAN:
        ch = 'pa'
      spaces += 10
      print_tree(dereference(nd).right_child, spaces)
      for i in range(10, spaces):
          sys.stdout.write(" ")
      print("   {}\n".format(ch))
      print_tree(dereference(nd).left_child, spaces)
      return


"""
Parameters: node*, int, file stream
Returns: none
Prints out controller tree to the file inputed
"""
cdef void print_controller(node* nd, int spaces, file):
    ch = ""
    cdef int type
    my_str = ""

    if nd != NULL:
        type = dereference(nd).type
        if type == _ADDITION:
            ch = '+'
        if type == _MULTIPLICATION:
            ch = '*'
        if type == _SUBTRACTION:
            ch = '-'
        if type == _DIVISION:
            ch = '/'
        if type == _RANDOM:
            ch = 'R'
        if type == _GHOST:
            ch = 'g'
        if type == _WALLS:
            ch = 'w'
        if type == _PILL:
            ch = 'p'
        if type == _FRUIT:
            ch = 'f'
        if type == _CONSTANT:
            ch = str(dereference(nd).value)
        if type == _PACMAN:
          ch = 'pa'
        spaces += 10
        print_controller(dereference(nd).right_child, spaces, file)
        for i in range(10, spaces):
            file.write(" ")
        file.write("   {}\n".format(ch))
        print_controller(dereference(nd).left_child, spaces, file)
        return


"""
Parameters: Node*
Returns: float
Returns the value of the node. Functions do their operations speficed by their names
if the node is not a function, it retuls the float value assigned to it
"""
@cdivision
@boundscheck(False)
cdef float get_value(node* nd):
    cdef int type = dereference(nd).type
    cdef node* left_child = dereference(nd).left_child
    cdef node* right_child = dereference(nd).right_child
    #Variables for the operators
    cdef float left
    cdef float right

    #For random number
    cdef float random
    cdef float diff
    cdef float r

    #If this node is a operator, create the left and right sides. All arities of the tree are 2
    if type == _ADDITION or type == _RANDOM or type == _MULTIPLICATION or type == _DIVISION or type == _SUBTRACTION:
        left = get_value(left_child)
        right = get_value(right_child)

    if type == _ADDITION:
        return left + right
    elif type == _MULTIPLICATION:
        return left*right
    elif type == _SUBTRACTION:
        return left-right
    elif type == _DIVISION:
        if right == 0:
            return 1
        return left / right
    elif type == _RANDOM:
        random  = float((float(rand()) / float(RAND_MAX)))
        diff = right - left
        r = random * diff
        return left + random

    #This wasn't a function node, just return its value
    return dereference(nd).value


"""
Parameters: tree, tree
Returns: tree
Creates a tree using subtree crossover, the first paramters is the base tree and the second paramter is the doner
"""
cdef tree subtree_crossover(tree first, tree second):
    cdef tree new_tree = tree(first.max_depth)
    cdef node* random_node_to_replace
    cdef node* random_node_replacing
    cdef node* parent_of_replaced_node
    cdef bint was_root = False

    new_tree.copy_tree(first)
    random_node_to_replace = new_tree.random_node(new_tree.root)
    random_node_replacing = recursive_copy(second.random_node(second.root))

    parent_of_replaced_node = dereference(random_node_to_replace).parent
    dereference(random_node_replacing).parent = parent_of_replaced_node

    #Replace the child of teh parent that is ebing replaced
    if parent_of_replaced_node != NULL:
        if dereference(parent_of_replaced_node).left_child == random_node_to_replace:
            dereference(parent_of_replaced_node).left_child = random_node_replacing
        elif dereference(parent_of_replaced_node).right_child == random_node_to_replace:
            dereference(parent_of_replaced_node).right_child = random_node_replacing
    else:
        was_root =True

    #Delete the old nodes no longer being used
    delete_nodes(random_node_to_replace)

    #finally set the new node
    random_node_to_replace = random_node_replacing
    #We replaced the root. Reset the Root
    if was_root:
        new_tree.root = random_node_to_replace

    #Reassign the terminal vector of new_tree
    new_tree.generate_terminal_vector(new_tree.root)
    return new_tree

cdef ghost_tree subtree_crossover_ghost(tree first, tree second):
    cdef tree new_tree = ghost_tree(first.max_depth)
    cdef node* random_node_to_replace
    cdef node* random_node_replacing
    cdef node* parent_of_replaced_node
    cdef bint was_root = False

    new_tree.copy_tree(first)
    random_node_to_replace = new_tree.random_node(new_tree.root)
    random_node_replacing = recursive_copy(second.random_node(second.root))

    parent_of_replaced_node = dereference(random_node_to_replace).parent
    dereference(random_node_replacing).parent = parent_of_replaced_node

    #Replace the child of teh parent that is ebing replaced
    if parent_of_replaced_node != NULL:
        if dereference(parent_of_replaced_node).left_child == random_node_to_replace:
            dereference(parent_of_replaced_node).left_child = random_node_replacing
        elif dereference(parent_of_replaced_node).right_child == random_node_to_replace:
            dereference(parent_of_replaced_node).right_child = random_node_replacing
    else:
        was_root =True

    #Delete the old nodes no longer being used
    delete_nodes(random_node_to_replace)

    #finally set the new node
    random_node_to_replace = random_node_replacing
    #We replaced the root. Reset the Root
    if was_root:
        new_tree.root = random_node_to_replace

    #Reassign the terminal vector of new_tree
    new_tree.generate_terminal_vector(new_tree.root)
    return new_tree

"""
Parameters: tree
Returns: Tree
Creates a tree that is a subtree mutation of the tree passed
"""
cdef tree subtree_mutation(tree the_tree):
    #Random Tree based of of either grow or full
    cdef int max_depth = the_tree.max_depth
    cdef tree new_tree = tree(max_depth)
    cdef tree tree_to_return = tree(max_depth)
    tree_to_return.copy_tree(the_tree)
    cdef node* random_node_to_mutate
    cdef node* replacement
    cdef node* parent
    cdef bint was_root = False

    #50% chance for full , 50% chance for grow
    if (rand() % 2) == 0:
        new_tree.grow(new_tree.root)
    else:
        new_tree.full(new_tree.root)

    replacement = recursive_copy(new_tree.root)

    random_node_to_mutate = tree_to_return.random_node(tree_to_return.root)
    parent = dereference(random_node_to_mutate).parent
    dereference(replacement).parent = parent

    if parent != NULL:
        if dereference(parent).left_child == random_node_to_mutate:
            dereference(parent).left_child = replacement
        else:
            dereference(parent).right_child = replacement
    else:
        was_root = True

    delete_nodes(random_node_to_mutate)
    new_tree.delete_tree()
    random_node_to_mutate = replacement

    if was_root:
        tree_to_return.root = random_node_to_mutate

    tree_to_return.generate_terminal_vector(tree_to_return.root)
    return tree_to_return

cdef ghost_tree subtree_mutation_ghost(tree the_tree):
  #Random Tree based of of either grow or full
  cdef int max_depth = the_tree.max_depth
  cdef tree new_tree = ghost_tree(max_depth)
  cdef tree tree_to_return = ghost_tree(max_depth)
  tree_to_return.copy_tree(the_tree)
  cdef node* random_node_to_mutate
  cdef node* replacement
  cdef node* parent
  cdef bint was_root = False

  #50% chance for full , 50% chance for grow
  if (rand() % 2) == 0:
      new_tree.grow(new_tree.root)
  else:
      new_tree.full(new_tree.root)

  replacement = recursive_copy(new_tree.root)

  random_node_to_mutate = tree_to_return.random_node(tree_to_return.root)
  parent = dereference(random_node_to_mutate).parent
  dereference(replacement).parent = parent

  if parent != NULL:
      if dereference(parent).left_child == random_node_to_mutate:
          dereference(parent).left_child = replacement
      else:
          dereference(parent).right_child = replacement
  else:
      was_root = True

  delete_nodes(random_node_to_mutate)
  new_tree.delete_tree()
  random_node_to_mutate = replacement

  if was_root:
      tree_to_return.root = random_node_to_mutate

  tree_to_return.generate_terminal_vector(tree_to_return.root)
  return tree_to_return


"""
Parameters: tree, tree
Returns: tree
Wrapper fucntion to perform subtree crossover between first and second
"""
def crossover_wrapper(first, second):
    if isinstance(first, ghost_tree):
      return subtree_crossover_ghost(first, second)
    return subtree_crossover(first, second)

"""
Parameters: tree
Returns: tree
Wrapper function to perform subtree mutation on first
"""
def mutation_wrapper(first):
    if isinstance(first, ghost_tree):
      return subtree_mutation_ghost(first)
    return subtree_mutation(first)



"""
Cpp class for GP tree
"""
cdef class tree:

    def __cinit__(self, int max_depth):
        self.FUNCTION_OR_TERMINAL[:] = [_TERMINAL, _FUNCITON]
        self.TYPE_OF_TERMINAL[:] = [_CONSTANT, _GHOST, _PILL, _WALLS, _FRUIT]
        self.TYPE_OF_FUNCTION[:] = [_ADDITION, _MULTIPLICATION, _SUBTRACTION, _DIVISION, _RANDOM]
        self.max_depth = max_depth
        self._TOTAL_TERMINALS = 5
        self._TOTAL_FUNCTIONS = 5


    """
    Parameters: node* int
    Returns: int
    Returns depth of the node passes
    """
    cdef int depth(self, node* nd, int depth):
        cdef node* parent = dereference(nd).parent
        if parent == NULL:
            return depth
        else:
            return self.depth(parent, depth+1)


    """
    Parameters: node*
    Returns: None
    Perfroms grow in the tree starting from the root
    """
    @cdivision
    @boundscheck(False)
    cdef void grow(self, node* nd):
        #This is the root
        cdef int root_type
        cdef int next_type
        cdef int function_type
        cdef int terminal_type
        cdef int current_type

        #int variable for choosing
        cdef int left_type
        cdef int right_type
        cdef int left_fun
        cdef int right_fun
        cdef int left_term
        cdef int right_term
        cdef node* new_left
        cdef node* new_right


        if nd == NULL:
            #Choose either a function or a terminal for this node
            root_type = self.FUNCTION_OR_TERMINAL[rand() % 2]
            if root_type == _FUNCITON:
                function_type = self.TYPE_OF_FUNCTION[rand() % self._TOTAL_FUNCTIONS]
                self.root = create_node(0, function_type)
            else:
                terminal_type = self.TYPE_OF_TERMINAL[rand() % self._TOTAL_TERMINALS]
                self.root = create_node(0, terminal_type)
                if terminal_type == _CONSTANT:
                    #Generatre a random floating point number
                    dereference(self.root).value = float(float(rand() / float(RAND_MAX) * _CONST_MAX))
                self.terminals.push_back(self.root)

        if nd == NULL:
            nd = self.root

        current_type = dereference(nd).type

        #If this is not a function, return
        for i in range(5):
            if current_type == self.TYPE_OF_TERMINAL[i]:
                return

        #We must now create the children for the function node

        left_type = self.FUNCTION_OR_TERMINAL[rand() % 2]
        right_type = self.FUNCTION_OR_TERMINAL[rand() % 2]

        #Both of these  nodes will be on the same depth, check to see if we are at max depth
        if self.depth(nd, 0)+1 >= self.max_depth:
            left_type = _TERMINAL
            right_type = _TERMINAL

        if left_type == _FUNCITON:
            left_fun = self.TYPE_OF_FUNCTION[rand() % self._TOTAL_FUNCTIONS]
            new_left = create_node(0, left_fun)
        else:
            left_term = self.TYPE_OF_TERMINAL[rand() % self._TOTAL_TERMINALS]
            new_left = create_node(0, left_term)
            if left_term == _CONSTANT:
                dereference(new_left).value = float(float(rand() / float(RAND_MAX) * _CONST_MAX))
            self.terminals.push_back(new_left)

        if right_type == _FUNCITON:
            right_fun = self.TYPE_OF_FUNCTION[rand() % self._TOTAL_FUNCTIONS]
            new_right = create_node(0, right_fun)
        else:
            right_term = self.TYPE_OF_TERMINAL[rand() % self._TOTAL_TERMINALS]
            new_right = create_node(0, right_term)
            if right_term == _CONSTANT:
                dereference(new_right).value = float(float(rand() / float(RAND_MAX) * _CONST_MAX))
            self.terminals.push_back(new_right)

        #Done creating the children.
        add_children(nd, new_left, new_right)
        #Grow the children

        self.grow(new_left)
        self.grow(new_right)


    """
    Parameters: node*
    Returns: None
    Performs full tree expantion starting form the root
    """
    @cdivision
    @boundscheck(False)
    cdef void full(self, node* nd):
        cdef int root_type
        cdef int next_type
        cdef int function_type
        cdef int terminal_type
        cdef int current_type

        #int variable for choosing
        cdef int left_fun
        cdef int right_fun
        cdef int left_term
        cdef int right_term
        cdef node* new_left
        cdef node* new_right

        if nd == NULL:
            if self.max_depth == 0:
                root_type = _TERMINAL
            else:
                root_type = _FUNCITON

            if root_type == _FUNCITON:
                function_type = self.TYPE_OF_FUNCTION[rand() % self._TOTAL_FUNCTIONS]
                self.root = create_node(0, function_type)
            else:
                terminal_type = self.TYPE_OF_TERMINAL[rand() % self._TOTAL_TERMINALS]
                self.root = create_node(0, terminal_type)
                if terminal_type == _CONSTANT:
                    dereference(self.root).value = float(float(rand() / float(RAND_MAX) * _CONST_MAX))
                self.terminals.push_back(self.root)

        if nd == NULL:
            nd = self.root

        current_type = dereference(nd).type

        #If this is not a function, return
        for i in range(5):
            if current_type == self.TYPE_OF_TERMINAL[i]:
                return

        if self.depth(nd, 0) < self.max_depth-1:
            left_fun = self.TYPE_OF_FUNCTION[rand() % self._TOTAL_FUNCTIONS]
            right_fun = self.TYPE_OF_FUNCTION[rand() % self._TOTAL_FUNCTIONS]
            new_left = create_node(0, left_fun)
            new_right = create_node(0, left_fun)
        else:
            left_term = self.TYPE_OF_TERMINAL[rand() % self._TOTAL_TERMINALS]
            right_term = self.TYPE_OF_TERMINAL[rand() % self._TOTAL_TERMINALS]
            new_left = create_node(0, left_term)
            new_right = create_node(0, right_term)
            if left_term == _CONSTANT:
                dereference(new_left).value = float(float(rand() / float(RAND_MAX) * _CONST_MAX))
            if right_term == _CONSTANT:
                dereference(new_right).value = float(float(rand() / float(RAND_MAX) * _CONST_MAX))
            self.terminals.push_back(new_left)
            self.terminals.push_back(new_right)

        #Done making children
        add_children(nd, new_left, new_right)
        self.full(new_left)
        self.full(new_right)

    """
    Parameters: float, float, float, float
    Return: None
    Loads the sensor inputs into the terminal nodes, with the exception of constants
    that are defined per tree isntance in grow and full
    """
    cdef load_terminals(self, float ghost, float fruit, float pill, float walls):
        cdef int type
        for i in range(self.terminals.size()):
            type = dereference(self.terminals[i]).type
            if type == _GHOST:
                dereference(self.terminals[i]).value = ghost
            if type == _FRUIT:
                dereference(self.terminals[i]).value = fruit
            if type == _PILL:
                dereference(self.terminals[i]).value = pill
            if type == _WALLS:
                dereference(self.terminals[i]).value = walls
            else:
                #This was a constant. Dont do anything
                continue


    """
    Parameters: float, float, float, float
    Returns: None
    Wrapper function for loading sensor inputs into the terminal
    """
    def load_wrapper(self, ghost, fruit, pill, walls):
        self.load_terminals(ghost, fruit, pill, walls)

    """
    Parameters: node*
    Returns: node*
    Returns a random node from the tree
    """
    cdef node* random_node(self, node* nd):
        #If this is a terminal, return this node
        cdef int chance
        if dereference(nd).left_child == NULL or dereference(nd).right_child == NULL:
            return nd

        #This node is a fucntion. We should eitehr choose this node, it's left child or the right child
        #So we give a 33% chance for each case
        chance = rand() % 3

        if chance == 0:
            return self.random_node(dereference(nd).left_child)
        elif chance == 1:
            return nd
        else:
            return self.random_node(dereference(nd).right_child)\


    """
    Parameters: node*
    Returns: None
    Creates the vector of terminals using a tree traversal
    """
    cdef generate_terminal_vector(self, node* nd):
        #We are just starting this function, remove all the nodes from the vector
        if nd == self.root:
            self.terminals.clear()
        if nd == NULL:
            return
        if dereference(nd).left_child == NULL and dereference(nd).right_child == NULL:
            self.terminals.push_back(nd)
        else:
            self.generate_terminal_vector(dereference(nd).left_child)
            self.generate_terminal_vector(dereference(nd).right_child)


    """
    Parameters: node* int
    Returns: int
    Returns number of nodes in the tree
    """
    cdef int count_nodes(self, node* nd, sum):
        cdef int count = 1
        if nd == NULL:
            return 0
        else:
            count += self.count_nodes(dereference(nd).left_child, sum)
            count += self.count_nodes(dereference(nd).right_child, sum)
            return count

    """
    Parameters: None
    Returns: Int
    Wrapper for counting nodes in a tree
    """
    def count_wrapper(self):
        return self.count_nodes(self.root, 0)

    """
    Parameters: tree
    Return: None
    Set this tree to be a copy of the tree passed
    """
    cdef void copy_tree(self, tree copy_from):
        self.root = recursive_copy(copy_from.root)
        self.generate_terminal_vector(self.root)


    """
    Parameters: None
    Returns: None
    Deletes the tree
    """
    def delete_tree(self):
        delete_nodes(self.root)

    """
    Parameters: none
    Returns: tree
    Wrapper for copy
    """
    def copy_wrapper(self, other):
        self.copy_tree(other)

    """
    Parameters: None
    Returns: None
    Wrapper for grow
    """
    def grow_wrapper(self, seed=None):
        if seed != None:
          srand(seed)
        self.grow(self.root)

    """
    Parameters: None
    Returns: None
    Wrapper for full
    """
    def full_wrapper(self, seed=None):
        if seed != None:
          srand(seed)
        self.full(self.root)


    """
    Parameters: None
    Returns: Float
    Returns the value of the root of the tree
    """
    def evaluate_tree(self):
        return get_value(self.root)


    """
    Parameters: string
    Returns: none
    Write to the file named by the string parameter and write the controller
    """
    def controller_wrapper(self, filename):
        file = open(filename, "w")
        print_controller(self.root, 0, file)
        file.close()

    #for testing
    def print_wrapper(self):
        print_tree(self.root, 0)
        print(self.terminals.size())



cdef class ghost_tree(tree):
  def __cinit__(self, int max_depth):
      self.FUNCTION_OR_TERMINAL[:] = [_TERMINAL, _FUNCITON]
      #Fill with 0's because those indivies will never be used since _TOTAL_TERMINALS is two
      self.TYPE_OF_TERMINAL[:] = [_PACMAN, _GHOST, 0, 0, 0]
      self.TYPE_OF_FUNCTION[:] = [_ADDITION, _MULTIPLICATION, _SUBTRACTION, _DIVISION, _RANDOM]
      self.max_depth = max_depth
      self._TOTAL_TERMINALS = 2
      self._TOTAL_FUNCTIONS = 5


  cdef load_ghost_terminals(self, float ghost, float pac):
      cdef int type
      for i in range(self.terminals.size()):
          type = dereference(self.terminals[i]).type
          if type == _GHOST:
              dereference(self.terminals[i]).value = ghost
          if type == _PACMAN:
              dereference(self.terminals[i]).value = pac
          else:
              #This was a constant. Dont do anything
              continue


  """
  Parameters: float, float
  Returns: None
  Wrapper function for loading sensor inputs into the terminal
  """
  def load_ghost_wrapper(self, ghost, pac):
      self.load_ghost_terminals(ghost, pac)
