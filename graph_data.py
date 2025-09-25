import networkx as nx

def get_demo_graph():
    """
    Simple demo graph: 4 nodes, forming a small 2x2 grid.
    """
    G = nx.DiGraph()
    edges = [("A", "B", 1), ("A", "C", 2), ("B", "D", 2), ("C", "D", 1)]
    G.add_weighted_edges_from(edges)
    
    # Fixed positions for clean visualization
    pos = {
        "A": (0, 0),
        "B": (2, 0),
        "C": (0, 2),
        "D": (2, 2)
    }
    return G, pos

def get_large_graph():
    """
    Layered city-style graph:
    8 nodes arranged in a 4x2 grid.
    Nodes A-D are top row, E-H bottom row.
    Multiple paths with weights for quantum optimization.
    """
    G = nx.DiGraph()
    edges = [
        # Horizontal streets
        ("A", "B", 1), ("B", "C", 1), ("C", "D", 1),
        ("E", "F", 1), ("F", "G", 1), ("G", "H", 1),
        # Vertical avenues
        ("A", "E", 1), ("B", "F", 1), ("C", "G", 1), ("D", "H", 1),
        # Diagonal shortcuts
        ("B", "G", 2), ("F", "H", 2)
    ]
    G.add_weighted_edges_from(edges)

    # Layered positions for “city grid” look
    pos = {
        "A": (0, 1),
        "B": (2, 1),
        "C": (4, 1),
        "D": (6, 1),
        "E": (0, 0),
        "F": (2, 0),
        "G": (4, 0),
        "H": (6, 0)
    }
    return G, pos

def get_city_graph():
    G = nx.DiGraph()
    edges = [
        ("A","B",1),("B","C",1),("C","D",1),
        ("E","F",1),("F","G",1),("G","H",1),
        ("A","E",2),("B","F",2),("C","G",2),("D","H",2),
        ("B","E",2),("C","F",2),("D","G",2)
    ]
    G.add_weighted_edges_from(edges)
    pos = {
        "A":(0,0),"B":(2,0),"C":(4,0),"D":(6,0),
        "E":(0,2),"F":(2,2),"G":(4,2),"H":(6,2)
    }
    return G,pos

