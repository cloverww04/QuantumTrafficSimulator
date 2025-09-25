import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from quantum_algorithms import quantum_optimize

# Define network
G = nx.DiGraph()
edges = [("A", "B", 1), ("A", "C", 2), ("B", "D", 2), ("C", "D", 1)]
G.add_weighted_edges_from(edges)

# Run quantum optimization
best_path, quantum_counts = quantum_optimize(G, "A", "D")
print("Quantum optimized path:", best_path)

# Visualization setup
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
pos = nx.spring_layout(G)
vehicle_positions = [0]

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

    # Animate vehicle along the best path
    path_nodes = best_path
    total_edges = len(path_nodes) - 1
    current_edge_index = int(vehicle_positions[0] * total_edges)
    if current_edge_index >= total_edges:
        vehicle_positions[0] = 0
        current_edge_index = 0
    start = pos[path_nodes[current_edge_index]]
    end = pos[path_nodes[current_edge_index + 1]]
    t = vehicle_positions[0] * total_edges - current_edge_index
    x = start[0] + (end[0] - start[0]) * t
    y = start[1] + (end[1] - start[1]) * t
    ax1.plot(x, y, 'ro', markersize=12)
    vehicle_positions[0] += 0.01  # vehicle speed

    # Draw quantum histogram on the side
    ax2.bar(quantum_counts.keys(), quantum_counts.values(), color='purple')
    ax2.set_title("Quantum Path Probabilities")
    ax2.set_xlabel("Path index")
    ax2.set_ylabel("Counts")

ani = animation.FuncAnimation(fig, animate, frames=100, interval=200)
plt.show()
