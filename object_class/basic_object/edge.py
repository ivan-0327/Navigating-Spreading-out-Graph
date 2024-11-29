import math
import random
import numpy as np
import heapq
# we need a class of node and edge for our K-nearest neighbor graph algorithm .
# Our data type is text for NLP task.
class Edge :
  #Edge is used to record situation about connecting each node and the distance between the two nodes .
  def __init__(self , from_node :int , to_node:int , distance : float  , flag:bool = True) :
    self.from_node = from_node
    self.to_node  = to_node
    self.distance  = distance
    self.flag    = flag
  def __repr__(self ):

    return f"from:{self.from_node} to : {self.to_node} and distance :{self.distance} and flag :{self.flag}"

  def __lt__(self , other):
    return self.distance < other.distance