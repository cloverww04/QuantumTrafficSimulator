import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import TextBox
from quantum_algorithms import quantum_optimize
import random

# Define network
G = nx.DiGraph()
edges = [("A", "B", 1), ("A", "C", 2), ("B", "D", 2), ("C", "D", 1)]
G.add_weighted_edges_from(edges)

# Run quantum optimization
best_path, quantum_counts = quantum_optimize(G, "A", "D")
print("Quantum optimized path:", best_path)

# Visualization setup
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
plt.subplots_adjust(bottom=0.2)  # space for TextBox
pos = nx.spring_layout(G)

# Vehicle storage
vehicles = []

def init_vehicles(n):
    """Initialize vehicles with staggered start positions and unique colors"""
    return [
        {
            "pos": -i * 0.2,  # stagger start so they don’t overlap
            "color": plt.cm.tab10(i % 10)
        }
        for i in range(n)
    ]

# Start with 3 vehicles for demo
vehicles = init_vehicles(3)

def animate(i):
    ax1.clear()
    ax2.clear()

    # Draw network with quantum-selected path highlighted
    edge_colors = ['red' if u in best_path and v in best_path else 'gray' for u, v in G.edges()]
    edge_widths = [3 if u in best_path and v in best_path else 1 for u, v in G.edges()]
    nx.draw(G, pos, with_labels=True, node_color='lightblue', node_size=1500,
            arrows=True, ax=ax1, edge_color=edge_colors, width=edge_widths)
    edge_labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, ax=ax1)

    # Animate all vehicles
    path_nodes = best_path
    total_edges = len(path_nodes) - 1

    for v in vehicles:
        if v["pos"] >= 1.0:  # loop back after reaching destination
            v["pos"] = 0.0
        current_edge_index = int(max(0, v["pos"]) * total_edges)
        if current_edge_index >= total_edges:
            current_edge_index = total_edges - 1
        start = pos[path_nodes[current_edge_index]]
        end = pos[path_nodes[current_edge_index + 1]]
        t = max(0, v["pos"]) * total_edges - current_edge_index
        x = start[0] + (end[0] - start[0]) * t
        y = start[1] + (end[1] - start[1]) * t
        ax1.plot(x, y, 'o', color=v["color"], markersize=12)
        v["pos"] += 0.01  # vehicle speed

    # Draw quantum histogram on the side
    ax2.bar(quantum_counts.keys(), quantum_counts.values(), color='purple')
    ax2.set_title("Quantum Path Probabilities")
    ax2.set_xlabel("Path index")
    ax2.set_ylabel("Counts")

# TextBox for user input
axbox = plt.axes([0.25, 0.05, 0.5, 0.05])  # x, y, width, height
text_box = TextBox(axbox, 'Vehicles: ', initial="3")

def submit(text):
    global vehicles
    try:
        n = int(text)
        if n > 0:
            vehicles[:] = init_vehicles(n)
            print(f"Updated to {n} vehicles")
    except ValueError:
        print("Invalid number entered")

text_box.on_submit(submit)

# Run animation
ani = animation.FuncAnimation(fig, animate, frames=200, interval=100)
plt.show()
