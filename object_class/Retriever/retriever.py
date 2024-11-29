import heapq
import numpy as np
import random
class Retriever():
  def __init__(self , B  , embedding_model , pool_max:int ):
    # Firstly , We obtain a K-Nearest Neighbors Graph .
    self.B        = B
    self.embedding_model = embedding_model
    self.l        = pool_max

  def __Cosine_Similarity__( self , vec1 , vec2 ) -> float:
    #we utilize cosine similarity to calculate the distance for two nodes of NLP task .
    #because we use the minimum heap , we need to add a minus symbol for distance.
    dot_product = np.dot(vec1 , vec2 )
    norm_1   = np.linalg.norm(vec1)
    norm_2   = np.linalg.norm(vec2)
    similarity = dot_product / (norm_1 * norm_2)
    return similarity *(-1)
  
  def __get_start_node__(self):
    return random.sample( [n for n in self.B.values()  ], 1 )[0]

  def __check_visited_node_distance__(self,candidates ,visited_distance ,  p = 0.1) -> bool:
    count = 0

    for item in candidates :# ( distance , node )
      if item[0]  < visited_distance :
        count += 1

    if (count/ len(candidates)) > p :
      return True
    else :
      return False

  def InVoke( self , query:str , k:int = 1 , Is_a_vector = False )->list:
    """
    query : The object you want to compare against other nodes in the graph. The goal is to find the k-nearest neighbors of this object on a defined similarity metric .
    k     : number of nearest neighnbors.
    """
    if Is_a_vector == False :
      query_vector = self.embedding_model.embed_query( query )
    else :
      query_vector = query

    candidates  = []
    visited    = set()
    l       = self.l

    #sampling start point p .
    start_node = self.__get_start_node__()

    #Initialize heap queue
    #because we use the minimum heap , we need to add a minus symbol for distance.
    distance = self.__Cosine_Similarity__( query_vector ,start_node.vector )
    heapq.heappush(candidates , ( distance ,start_node ) ) # ( distance , node )

    # if len(candidates) + len(visited) > l => return top k node
    while (len(candidates) > 0 ) and ( ( len(visited)+len(candidates) ) < l ):
      # 1. get node from cindidates
      distance , node = heapq.heappop( candidates )

      if ( distance ,node ) in visited :
        continue

      visited.add((distance, node)) # ( distance , node )
      visited_distance = distance

      # Access node 's neighbor .
      for edge in node.out_edge:
        neighbor_node = self.B[ edge.to_node ]
        distance = self.__Cosine_Similarity__( query_vector ,neighbor_node.vector )

        if (distance ,neighbor_node) in candidates :
          continue

        heapq.heappush( candidates , ( distance , neighbor_node))# ( distance , node )

      # if there are len(neighbor_node) *p of length of nodes which are greater than visited node distance .
      if( ( len(visited)+len(candidates) ) >= l ):
        add_l_flag = self.__check_visited_node_distance__(candidates ,visited_distance )

        if add_l_flag :
          l *=2

      # we need to truncate candidates
      candidates = heapq.nsmallest( l , candidates )

    # return top k nodes .
    combined = list(visited) + candidates
    combined = heapq.nsmallest(k, combined)

    return [(distance , node) for distance, node in combined] ,list(visited)

  def Compare_with_all( self , query:str , k:int = 1 )->list:
    query_vector = self.embedding_model.embed_query( query )
    candidates  = []

    for node in self.B.values() :
      distance = self.__Cosine_Similarity__( query_vector ,node.vector )
      heapq.heappush( candidates , ( distance , node))# ( distance , node )

    candidates = heapq.nsmallest(k, candidates)

    return [(distance , node) for distance, node in candidates]
  
  def recall( self, KNNG_result , truth_result ,k:int ):

    KNNG  = set()
    truth = set()

    for item in KNNG_result:
      KNNG.add(item[1].id)

    for item  in truth_result :
      truth.add(item[1].id)
      
    combine = KNNG & truth

    print(f"Using Algorithm 1  :{KNNG}")
    print(f"ground truth :{truth}")
    print(f"len(combine) :{len(combine)}")
    return len(combine)/ k




