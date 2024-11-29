import math
import random
import numpy as np
import heapq
import copy
from object_class.basic_object.node import Node
from object_class.basic_object.edge import Edge
class KNNG_Builder():
  def __init__(self , document : list , embedding_model , k = 20 , p = 1.0  , l = 0.001) :
    self.embedding_model = embedding_model
    self.documents   = document
    self.B      = None

    self.k      = k
    self.p      = p
    self.l      = l
    self.n      = None

  def __Build_Node_Dictionary__(self) -> list:
    # according to length of contents, we execute a for loop to process contents .

    contents = []
    for ( index , item ) in enumerate(self.documents)  :
      contents.append (item.page_content)

    #get vecter by embedding model
    vecters = self.embedding_model.embed_documents( contents )

    #build node
    B ={}
    for ( index , content ) in enumerate(contents)  :
      node   = Node( index, content , vecters[index] )
      #add key-value
      B[index] = node
      
    self.n      = len(B)
    return B


  def __Cosine_Similarity__( self , vec1 , vec2 ) -> float:
    #we utilize cosine similarity to calculate the distance for two nodes of NLP task .
    dot_product = np.dot(vec1 , vec2 )
    norm_1   = np.linalg.norm(vec1)
    norm_2   = np.linalg.norm(vec2)
    similarity = dot_product / (norm_1 * norm_2)
    return similarity

  def __Init_KNNG_BY_Sampling__( self  , k:int  ):
    #Initialize Node's Neighbor by sampling .
    for  node  in self.B.values() :
      #init of outedge
      node.out_edge = []

      #To Get k Neighbors By Sampling .
      neighbors = self.__safe_sample__( [n for n in self.B.values() if n.id != node.id ] , k )
      #print(f"len of  neighbors:{len(neighbors)}")

      # We get neighbors ,and then put edges in node's out_edge heap .
      for neighbor in neighbors :
        new_edge = Edge( from_node = node.id , to_node = neighbor.id , distance = self.__Cosine_Similarity__(node.vector , neighbor.vector ) )
        heapq.heappush(node.out_edge , new_edge )

  def __Reverse_Neighbors__(self , B , edge_name:str ="new_reverse_edge" ,flag = True ) -> list :
    # We want to get the reverse neighbors , which means identifying which nodes consider current v as a neighbor.
    for  node  in B.values() :
      #init of inedge
      edge_object = getattr(node, edge_name)
      edge_object = []
      for  check_node  in B.values() :
        if node.id != check_node.id :
          #check out_edge[i].to_node
          Is_exit ,Is_exit_edge = self.__Check_node_id_In_OutEdge__( check_node.out_edge , node.id )

          if Is_exit == True :
            if Is_exit_edge == flag:
              new_edge = Edge( from_node = check_node.id  , to_node = node.id , \
                        distance = self.__Cosine_Similarity__( check_node.vector , node.vector ) ,flag =check_node.flag )
              heapq.heappush(edge_object , new_edge )


  def __Check_node_id_In_OutEdge__(self , edges :Edge , Node_id : int )-> bool :
    #We check whether or not the node.id exist in OutEdge.
    for edge in edges :
      if edge.to_node == Node_id :
        return True , edge
    return False , None

  def __Get_Old_Edges__(self):
    for node in self.B.values():
      valid_edges = [copy.deepcopy(edge) for edge in node.out_edge if  edge.flag == False ]
      #Using heapify ()
      heapq.heapify(valid_edges)
      node.old_edge = valid_edges

  def __Get_New_Edges__(self):
    for node in self.B.values():
      #To Get ρK Neighbors By Sampling .
      sampled_edges     = self.__safe_sample__( [edge for edge in node.out_edge if edge.flag == True ] , int(self.p * self.k) )
      sampled_edges_copy = copy.deepcopy(sampled_edges)

      heapq.heapify(sampled_edges_copy)
      node.new_edge = sampled_edges_copy

      #tag sampled edges as False
      for edge in sampled_edges :
        edge.flag = False

  def __Union__(self , a:list , b:list ):
    final_list = list( set(a) | set(b))
    return final_list

  def __Update_NN__(self , node , check_node_id:int , similarity:float , flag = True) -> int:
    # if Out_Edges len is less than k ,then push node into Out_Edges  .
    # To avoid add existed edge.
    for edge in node.out_edge:
        if edge.to_node == check_node_id:
            return 0

    if len(node.out_edge) < self.k :
      new_edge = Edge( from_node = node.id ,
                to_node = check_node_id ,
                distance = similarity )

      heapq.heappush(node.out_edge , new_edge)
      return 1
    else:
      # if the length of Out_edges is greater than k ,
      # we compare the similarity of the current least similarity element with the new candidate's similarity.
      # Replace the least similarity element only if the new candidate has a higher similarity.
      if similarity > node.out_edge[0].distance :
         heapq.heappop(node.out_edge)  # 移除最小的元素
         new_edge = Edge( from_node = node.id ,
                to_node = check_node_id ,
                distance = similarity )
         heapq.heappush( node.out_edge , new_edge )
         return 1
    return 0

  def __safe_sample__(self ,population, sample_size):
    if sample_size > len(population):
        return population
    return random.sample(population, sample_size)

  def build_KNNG(self ) -> list :
    # Initialize the Node.
    self.B = self.__Build_Node_Dictionary__() # Node dictionary

    # we obtain a list of nodes , each of which stores its own edges .
    # step 1 : We need to obtain a heap of storing nodes of neighbor for each node by sampling .
    self.__Init_KNNG_BY_Sampling__( k = self.k )
    count = 0
    # step 2 : while loop
    while True :
      count += 1
      #Get old[v]
      self.__Get_Old_Edges__()
      #Get new[v]
      self.__Get_New_Edges__()

      #Get Reverse old and new
      self.__Reverse_Neighbors__(self.B , edge_name ="old_reverse_edge" ,flag = False)
      self.__Reverse_Neighbors__(self.B , edge_name ="new_reverse_edge" ,flag = True)

      #Update Neighbors by comparing similarity.
      c = int(0)
      for v in self.B.values() :
        # Combine  old and old_reverse
        final_old = self.__Union__( copy.deepcopy(v.old_edge)
                       ,copy.deepcopy( self.__safe_sample__( [edge for edge in v.old_reverse_edge] , int(self.p * self.k) ) ) )
        # Combine new and new_erverse
        final_new = self.__Union__( copy.deepcopy(v.new_edge)
                       ,copy.deepcopy( self.__safe_sample__( [edge for edge in v.new_reverse_edge] , int(self.p * self.k) ) ) )

        # Comparing u1 , u2 and Updating Neighbors . u1 and u2 are v's neighbors.
        # u1, u2 ∈ new[v], u1 < u2
        for i in range(len(final_new)):
          new_edge = final_new[i]
          u1    = self.B[new_edge.to_node]

          for j in range(i+1 , len(final_new)): #u1 < u2 to alleviate repetitive calculation.
            new_edge = final_new[j]
            u2     = self.B[new_edge.to_node]

            if u1.id != u2.id :
              similarity = self.__Cosine_Similarity__( u1.vector , u2.vector )

              c += self.__Update_NN__( u1 , u2.id , similarity)
              c += self.__Update_NN__( u2 , u1.id , similarity)

        # u1 ∈ new[v], u2 ∈ old[v]
        for edge1 in final_new:
          u1    = self.B[edge1.to_node]

          for edge2 in final_old:
            u2  = self.B[edge2.to_node]

            if u1.id != u2.id :
              similarity = self.__Cosine_Similarity__( u1.vector , u2.vector )
              c += self.__Update_NN__( u1 , u2.id , similarity)
              c += self.__Update_NN__( u2 , u1.id , similarity)
      # return B if c < δNK
      print(f"loop count :{count}")
      if c < self.l * self.n * self.k :
        print(f"Break while loop ! Finished !")
        break