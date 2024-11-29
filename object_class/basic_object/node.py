import math
import random
import numpy as np
import heapq
# we need a class of node and edge for our K-nearest neighbor graph algorithm .
# Our data type is text for NLP task.
class Node :
  def __init__(self , id  , content : str  , vector : np.ndarray ) :
    self.content       = content
    self.vector       = vector
    self.id         = id

    self.out_edge      = []  # neighbors .

    self.old_edge      = [] # old neighbors .
    self.old_reverse_edge  = [] # old reverse neighbors .

    self.new_edge      = [] # new neighbors .
    self.new_reverse_edge  = [] # new reverseneighbors .



  def add_edge(self , edge ):

    if edge.from_node == self.id:
      self.out_edge.append(edge)
    elif edge.to_node == self.id:
      self.in_edge.append(edge)
    else:
      print(f"node :{self.id} has an error for add_edge function . ")

  def __repr__(self):
    return f"id: {self.id} , content :{self.content} , vector len :{len(self.vector)}"