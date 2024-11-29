import heapq
import numpy
import random
from object_class.Retriever.retriever import Retriever
class NSG_Retriever(Retriever):
  def __init__(self , B  , embedding_model , pool_max:int ):
    super().__init__(B  , embedding_model , pool_max)
    self.get_start_node_fuuction = self.__random_get_start_node__
    self.search_start_node    = None

  def __random_get_start_node__(self):
    return random.sample( [n for n in self.B.values()  ], 1 )[0]

  def __particularly_get_start_node__(self):
    return self.search_start_node

  def __get_start_node__(self):
    return self.get_start_node_fuuction()

  def set_start_node_strategy(self , randomly = True , search_start_node =None ):
    if randomly :
      self.get_start_node_fuuction =self.__random_get_start_node__
    else:
      self.search_start_node    = search_start_node
      self.get_start_node_fuuction =self.__particularly_get_start_node__

  def InVoke( self ,B,  query:str , k:int = 1 , Is_a_vector = False   )->list:
    # reset the B
    if B != None:
      self.B = B
      
    return super().InVoke( query , k , Is_a_vector)
