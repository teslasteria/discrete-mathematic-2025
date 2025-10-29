import networkx as nx
import matplotlib.pyplot as plt

def read_graphs(filename):
    with open(filename, 'r') as f:
        n = int(f.readline().strip())
        m1 = int(f.readline().strip())
        G1 = nx.Graph()
        G1.add_nodes_from(range(n))
        for _ in range(m1):
            u, v = map(int, f.readline().split())
            G1.add_edge(u, v)
        
        m2 = int(f.readline().strip())
        G2 = nx.Graph()
        G2.add_nodes_from(range(n))
        for _ in range(m2):
            u, v = map(int, f.readline().split())
            G2.add_edge(u, v)
        
        return G1, G2

def plot_graphs(G1, G2):
    plt.figure(figsize=(12, 6))
    
    plt.subplot(1, 2, 1)
    pos1 = nx.spring_layout(G1, seed=42)
    nx.draw(G1, pos1, with_labels=True, node_color='skyblue', 
            node_size=500, edge_color='gray', font_size=12)
    plt.title("Graph 1", fontsize=14)
    
    plt.subplot(1, 2, 2)
    pos2 = nx.spring_layout(G2, seed=42)
    nx.draw(G2, pos2, with_labels=True, node_color='lightgreen', 
            node_size=500, edge_color='gray', font_size=12)
    plt.title("Graph 2", fontsize=14)
    
    plt.tight_layout()
    plt.savefig("graph_visualization.png", dpi=300, bbox_inches='tight')
    plt.show()

if __name__ == "__main__":
    G1, G2 = read_graphs("input.txt")
    plot_graphs(G1, G2)