import numpy as np
import matplotlib.pyplot as plt
import networkx as nx

class KNNG_Visualizer:
    def __init__(self, nodes, navigating_node_id=None):
        """
        初始化視覺化工具。
        :param nodes: 節點集合
        :param navigating_node_id: 可選，導航節點的 ID，用紅色標記
        """
        self.nodes = nodes
        self.navigating_node_id = navigating_node_id  # 可選的導航節點 ID，若為 None 則不標記

    def create_graph(self):
        G = nx.DiGraph()  # 使用 DiGraph 表示有向圖

        # 添加節點
        for node in self.nodes.values():
            G.add_node(node.id, label=node.content)

        # 添加邊
        for node in self.nodes.values():
            for edge in node.out_edge:
                G.add_edge(edge.from_node, edge.to_node, weight=edge.distance)

        return G

    def draw_graph(self, G , file_name):
        plt.figure(figsize=(15, 15))  # 調整圖形大小，這裡設定為 15x15 英寸
        pos = nx.spring_layout(G)  # 使用 spring layout 佈局節點

        # 如果有導航節點，將其標記為紅色
        node_colors = ['red' if node == self.navigating_node_id else 'skyblue' for node in G.nodes()] if self.navigating_node_id else ['skyblue'] * len(G.nodes())

        # 繪製節點
        nx.draw_networkx_nodes(G, pos, node_size=80, node_color=node_colors, alpha=0.5)

        # 繪製有向邊
        nx.draw_networkx_edges(G, pos, width=0.2, alpha=0.2, edge_color='black', arrows=True, arrowstyle='-|>', arrowsize=10)

        # 標籤
        nx.draw_networkx_labels(G, pos, font_size=6, font_family="sans-serif")

        # 顯示圖形
        plt.title("")
        plt.axis("off")
        #plt.show()
        plt.savefig(file_name)



