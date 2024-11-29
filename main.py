from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from object_class.Graph.KNNG import KNNG_Builder 
from object_class.Graph.NSG import NSG_Builder 
from object_class.Retriever.NSG_Retriever import NSG_Retriever
from object_class.Retriever.retriever import Retriever
from object_class.visualization import KNNG_Visualizer

if __name__ == "__main__" :
    # loading embedding model
    model_name = "mixedbread-ai/mxbai-embed-large-v1"
    hf_embeddings = HuggingFaceEmbeddings( model_name=model_name )

    # load document
    loader   = PyPDFLoader("Fast Approximate Nearest Neighbor Search With The.pdf")
    documrnt  = loader.load()

    #splitter
    text_splitter = RecursiveCharacterTextSplitter( chunk_size = 250 , chunk_overlap = 20 )

    # do split
    document = text_splitter.split_documents(documrnt)

    # build KNNG Graph
    KNNG = KNNG_Builder( document = document , embedding_model = hf_embeddings )
    KNNG.build_KNNG()

    # 如果不希望標記導航節點
    visualizer_without_navigating_node = KNNG_Visualizer(KNNG.B)
    G = visualizer_without_navigating_node.create_graph()  # 創建圖
    visualizer_without_navigating_node.draw_graph(G , 'KNNG.png')  # 繪製圖
    
    #bulild NSG Graph
    nsg_Builder = NSG_Builder( knng_Builder = KNNG ,  max_out_degree = 8 , hf_embeddings = hf_embeddings , pool_max =20 )
    nsg_Builder.nsg_build()
    
    # test NSG
    pool_max = 20
    k=15
    retriever = NSG_Retriever(nsg_Builder.B , hf_embeddings , int(pool_max) *2 )
    retriever.set_start_node_strategy( randomly = False ,search_start_node =  nsg_Builder.navigating_node)
    result , _ = retriever.InVoke( nsg_Builder.B , "What is NSG ?" , k = k )

    # iterate all nodes 
    result_all = retriever.Compare_with_all( "What is NSG ?" , k = k )
    #calculate the recall
    retriever.recall( KNNG_result = result , truth_result = result_all ,k = k )

    # 如果希望標記導航節點
    visualizer_with_navigating_node = KNNG_Visualizer(nsg_Builder.B, nsg_Builder.navigating_node.id)
    G = visualizer_with_navigating_node.create_graph()  # 創建圖
    visualizer_with_navigating_node.draw_graph(G , "NSG.png")  # 繪製圖

    