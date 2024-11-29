import math
import random
import numpy as np
import heapq
import copy
from object_class.basic_object.node import Node
from object_class.basic_object.edge import Edge
from object_class.Graph.KNNG  import KNNG_Builder
from object_class.Retriever.NSG_Retriever import NSG_Retriever

class NSG_Builder(KNNG_Builder):
  def __init__(self , knng_Builder:KNNG_Builder  ,   max_out_degree , hf_embeddings, pool_max = 20 ):
    self.max_out_degree = max_out_degree
    self.knng_Builder  = knng_Builder
    self.nsg_retrieve  = NSG_Retriever(knng_Builder.B , hf_embeddings , int(pool_max) *2 )
    self.navigating_node = None

  def __getattr__(self, name):
    # if the property you want is not in NSG, we will find the property in KNNG . 
    return getattr( self.knng_Builder , name )

  def __calculate_centroid__(self):
    all_vectors = [ np.array(vector.vector ) for vector in self.knng_Builder.B.values() ]
    return np.mean(all_vectors , axis = 0 )
  
  def __get_navigating_node__(self):
    centrial_node    = self.__calculate_centroid__()
    distance_node_list, _ = self.nsg_retrieve.InVoke( self.B , centrial_node , k = 1 , Is_a_vector = True )
    self.navigating_node   = distance_node_list[0][1]
    

  def __get_neighboes_with_minus_similarity__(self  , v ):
    result = []
    for edge in v.out_edge:
        neighbor_node = self.B[ edge.to_node ]
        distance = self.__Cosine_Similarity__( v.vector ,neighbor_node.vector ) * -1
        result.append( (distance , neighbor_node) ) # ( distance , node )

    return result

  def __Check_edges_conflict__(self , _v:tuple , _p:tuple , _r:tuple ):

    v    = _v  # v is a Node
    (_, p) = _p  # ( distance , node )
    (_, r) = _r  # ( distance , node )
    # MRNG selection strategy
    distance_v_p = self.__Cosine_Similarity__(  v.vector , p.vector )
    distance_v_r = self.__Cosine_Similarity__(  v.vector , r.vector )
    distance_p_r = self.__Cosine_Similarity__(  p.vector , r.vector )

    # if edge pr isn't the longest edge , there is a situation of conflicting .
    if distance_p_r >= max( distance_v_p , distance_v_r ) :
      # return False , there is no confliction.
      return False
    else :
      #return True , there is a confliction.
      return True

  def __remove_node_itself__ ( self , v ,Visited_nodes ):
    for distance, node in Visited_nodes :
      if v.id == node.id :
        Visited_nodes.remove((distance, node))

    return Visited_nodes

  def __update_NSG_Neighbors__(self , node , R:set  ):
    node.out_edge = []
    # We get neighbors ,and then put edges in node's out_edge heap .
    for (_ ,neighbor) in list(R) :
      new_edge = Edge( from_node = node.id , to_node = neighbor.id , distance = self.__Cosine_Similarity__(node.vector , neighbor.vector ) )
      heapq.heappush(node.out_edge , new_edge )

  def __DFS__(self ,B, DFS_start_node_id ):
    stack  = []
    visied = set()
    stack.append(DFS_start_node_id)

    #execute dfs algorithm
    while len(stack) >0 :
      current_node_id = stack.pop()
      visied.add(current_node_id)
      current_node  =B[current_node_id]

      for edge in current_node.out_edge:
        neighbor = B[edge.to_node]

        #if neighbor isn't visited, adding to stack
        if (neighbor.id not in visied) and (neighbor.id not in stack) :
          stack.append(neighbor.id)

    return visied

  def __get_set_visied_node__(self , visied_node_id_list):
    node_set = set()

    for id in visied_node_id_list:
      node = self.B[id]
      node_set.add(node)

    return node_set

  def __conect_isolation_node__(self ,isolation_node_list , visied_node):
    for node in isolation_node_list :
      distance_node_list, _ = self.nsg_retrieve.InVoke( self.B , node.vector , k = 1 , Is_a_vector = True )
      # find the cloest node in DFS , and ceonect it to isolation node.
      _ , conective_node = distance_node_list[0]


      #add new edge to node
      if (conective_node != None) and ( conective_node.id != node.id):

        new_edge = Edge( from_node = conective_node.id  , to_node = node.id , distance = self.__Cosine_Similarity__(node.vector , conective_node.vector ) )
        if new_edge not in conective_node.out_edge:
          print(f"node.id :{node.id} ,conective_node.id:{conective_node.id} is conected")
          heapq.heappush(conective_node.out_edge , new_edge )

          #add successfully and then break, because we just want to add a edge.
          break
        else:
          print(f"node.id :{node.id} ,conective_node.id:{conective_node.id} is repetitive .")

  def __ensuring_connectivity_with_DFS__(self ):
    DFS_start_node = self.navigating_node

    while True :
      visied_node_id_list   = self.__DFS__(self.B , DFS_start_node.id)
      visied_node       = self.__get_set_visied_node__(visied_node_id_list)
      B            = set(self.B.values() )
      isolation_node_list = B - visied_node

      self.__conect_isolation_node__(isolation_node_list , visied_node)
      if len(self.B) == len(visied_node):
        break


  def nsg_build( self ):
    # Get the Navigating Node.
    self.nsg_retrieve.set_start_node_strategy( randomly = True)
    self.__get_navigating_node__()
    # Set Search start node for Retriever.
    self.nsg_retrieve.set_start_node_strategy( randomly = False ,search_start_node =  self.navigating_node)

    # For each node v .
    #記得都要排除本身的node _未完成
    for v in self.B.values() :
      _ , Visited_nodes = self.nsg_retrieve.InVoke( None , v.vector , k = 1 , Is_a_vector = True )
      # remove the node itself.
      Visited_nodes = self.__remove_node_itself__( v , Visited_nodes)

      # order E and heappop p_0
      E      = self.__get_neighboes_with_minus_similarity__(v)
      E      = list(set( Visited_nodes + E )  )
      heapq.heapify( E )
      p_0 = heapq.heappop(E)

      # Set R as a set , and adding p_0 to R .
      R = set()
      R.add(p_0)

      # while loop
      while (len(E) >0 ) and (len(R) < self.max_out_degree ):
        p = heapq.heappop(E)
        conflict_flag = False

        # check edges with MRNG selection strategy .
        for r in R :
          conflict_flag = self.__Check_edges_conflict__( v , p , r )
          if conflict_flag :
            break
        # if there isn't conflict, to add p to R .
        if conflict_flag == False :
          R.add(p)

      # given each node a new set (R) of edges .
      self.__update_NSG_Neighbors__( v , R )

    # DFS
    self.__ensuring_connectivity_with_DFS__()



