import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import TextBox, RadioButtons
from quantum_algorithms import quantum_optimize
from graph_data import get_demo_graph, get_large_graph, get_city_graph

# --- Initial setup ---
G, pos = get_demo_graph()
start_node, end_node = "A", "D"
best_path, quantum_counts = quantum_optimize(G, start_node, end_node)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 9))
plt.subplots_adjust(left=0.05, right=0.95, bottom=0.25)  # space for widgets

# --- Traffic-aware vehicles ---
traffic_penalty = 1
traffic = {}  # edge -> number of vehicles on it
vehicles = []

def select_path():
    """Select path based on quantum counts and traffic congestion"""
    all_paths = list(nx.all_simple_paths(G, start_node, end_node))
    path_weights = []
    for idx, path in enumerate(all_paths):
        cost = 0
        for u, v in zip(path[:-1], path[1:]):
            w = G[u][v]['weight']
            t = traffic.get((u, v), 0)
            cost += w + t * traffic_penalty
        quantum_prob = quantum_counts.get(idx, 1)
        cost /= quantum_prob  # bias towards higher quantum counts
        path_weights.append(cost)
    min_idx = path_weights.index(min(path_weights))
    return all_paths[min_idx]

def init_vehicles(n):
    """Initialize vehicles with unique colors and assigned paths"""
    veh_list = []
    for i in range(n):
        path = select_path()
        veh_list.append({
            "pos": -i * 0.2,  # staggered start
            "color": plt.cm.tab10(i % 10),
            "path": path
        })
    return veh_list

# Start with 3 vehicles
vehicles = init_vehicles(3)

# --- Animation function ---
def animate(frame):
    ax1.clear()
    ax2.clear()

    # Draw network with quantum-selected path highlighted
    edge_colors = ['red' if u in best_path and v in best_path else 'gray' for u, v in G.edges()]
    edge_widths = [3 if u in best_path and v in best_path else 1 for u, v in G.edges()]
    nx.draw(G, pos, with_labels=True, node_color='lightblue', node_size=1500,
            arrows=True, ax=ax1, edge_color=edge_colors, width=edge_widths)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=nx.get_edge_attributes(G, 'weight'), ax=ax1)

    # Reset traffic counts
    for edge in G.edges():
        traffic[edge] = 0

    # Animate each vehicle
    for v in vehicles:
        path_nodes = v["path"]
        total_edges = len(path_nodes) - 1

        if v["pos"] >= 1.0:  # reached destination, pick a new path
            v["pos"] = 0.0
            v["path"] = select_path()
            path_nodes = v["path"]
            total_edges = len(path_nodes) - 1

        edge_idx = int(max(0, v["pos"]) * total_edges)
        if edge_idx >= total_edges:
            edge_idx = total_edges - 1

        start = pos[path_nodes[edge_idx]]
        end = pos[path_nodes[edge_idx + 1]]
        t = max(0, v["pos"]) * total_edges - edge_idx
        x = start[0] + (end[0] - start[0]) * t
        y = start[1] + (end[1] - start[1]) * t
        ax1.plot(x, y, 'o', color=v["color"], markersize=12)

        # Update traffic
        edge = (path_nodes[edge_idx], path_nodes[edge_idx + 1])
        traffic[edge] = traffic.get(edge, 0) + 1

        v["pos"] += 0.01  # vehicle speed

    # Quantum histogram
    ax2.bar(quantum_counts.keys(), quantum_counts.values(), color='purple')
    ax2.set_title("Quantum Path Probabilities")
    ax2.set_xlabel("Path index")
    ax2.set_ylabel("Counts")

# --- TextBox for vehicle count ---
axbox = plt.axes([0.25, 0.05, 0.5, 0.05])
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

# --- RadioButtons for graph selection ---
axradio = plt.axes([0.05, 0.05, 0.15, 0.15])
radio = RadioButtons(axradio, ('Demo Graph', 'Large Graph', 'City Graph'))

def graph_selector(label):
    global G, pos, best_path, quantum_counts, start_node, end_node, vehicles
    if label == 'Demo Graph':
        G, pos = get_demo_graph()
        start_node, end_node = "A", "D"
    elif label == 'Large Graph':
        G, pos = get_large_graph()
        start_node, end_node = "A", "G"
    else:
        G, pos = get_city_graph()
        start_node, end_node = "A", "H"

    best_path, quantum_counts = quantum_optimize(G, start_node, end_node)
    vehicles[:] = init_vehicles(len(vehicles))
    print(f"Switched to {label}")

radio.on_clicked(graph_selector)

# --- Run animation ---
ani = animation.FuncAnimation(fig, animate, frames=200, interval=100)
plt.show()
