import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import TextBox, RadioButtons
from quantum_algorithms import quantum_optimize
from graph_data import get_demo_graph, get_large_graph, get_city_graph

# --- Initial setup ---
G, pos = get_demo_graph()
start_node, end_node = "A", "D"
k_candidates = 10  # default number of candidate paths for Grover
best_path, quantum_counts, quantum_shots = quantum_optimize(G, start_node, end_node, k=k_candidates)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 9))
plt.subplots_adjust(left=0.05, right=0.95, bottom=0.25)  # space for widgets

# --- Traffic-aware vehicles ---
# nodes = intersections, edges = roads, weights = travel time
traffic_penalty = 1
traffic = {}  # edge -> number of vehicles on it
vehicles = []

def select_path():
    """Select path based on quantum counts and traffic congestion"""
    all_paths = list(nx.all_simple_paths(G, start_node, end_node))
    path_weights = []
    # safe epsilon for zero-count paths
    eps = 1e-6
    for idx, path in enumerate(all_paths):
        cost = 0
        for u, v in zip(path[:-1], path[1:]):
            w = G[u][v]['weight']
            t = traffic.get((u, v), 0)
            cost += w + t * traffic_penalty
        # use measured probability (counts / shots). if quantum_shots not available, fallback to 1
        if 'quantum_shots' in globals() and quantum_shots:
            qcount = quantum_counts.get(idx, 0)
            qprob = max(qcount / quantum_shots, eps)
        else:
            qprob = 1.0
        # bias toward higher quantum probability by reducing effective cost
        cost /= qprob
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

    # Reset traffic counts
    for edge in G.edges():
        traffic[edge] = 0

    # Update vehicle positions
    for v in vehicles:
        path_nodes = v["path"]
        total_edges = len(path_nodes) - 1

        if v["pos"] >= 1.0:
            v["pos"] = 0.0
            v["path"] = select_path()
            path_nodes = v["path"]
            total_edges = len(path_nodes) - 1

        edge_idx = int(max(0, v["pos"]) * total_edges)
        if edge_idx >= total_edges:
            edge_idx = total_edges - 1

        edge = (path_nodes[edge_idx], path_nodes[edge_idx + 1])
        traffic[edge] = traffic.get(edge, 0) + 1

        start = pos[path_nodes[edge_idx]]
        end = pos[path_nodes[edge_idx + 1]]
        t = max(0, v["pos"]) * total_edges - edge_idx
        x = start[0] + (end[0] - start[0]) * t
        y = start[1] + (end[1] - start[1]) * t
        ax1.plot(x, y, 'o', color=v["color"], markersize=12)
        v["pos"] += 0.01

    # Draw graph
    edge_colors, edge_widths = [], []
    for u, v in G.edges():
        if traffic.get((u, v), 0) > 0:
            edge_colors.append("orange")
            edge_widths.append(3)
        elif u in best_path and v in best_path:
            edge_colors.append("red")
            edge_widths.append(2)
        else:
            edge_colors.append("gray")
            edge_widths.append(1)

    nx.draw(G, pos, with_labels=True, node_color='lightblue', node_size=1500,
            arrows=True, ax=ax1, edge_color=edge_colors, width=edge_widths)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=nx.get_edge_attributes(G, 'weight'), ax=ax1)

   # --- Classical vs Quantum side-by-side histogram ---
    all_paths = list(nx.all_simple_paths(G, start_node, end_node))
    num_candidates = len(quantum_counts)

    # Classical costs
    classical_costs = [
        sum(G[path[i]][path[i+1]]['weight'] for i in range(len(path)-1))
        for path in all_paths[:num_candidates]
    ]

    # Normalize classical costs (lower cost = higher score)
    max_cost = max(classical_costs)
    classical_scores = [1 - (c / max_cost) for c in classical_costs]

    # Convert quantum counts to probabilities
    total_shots = sum(quantum_counts.values())
    quantum_probs = [quantum_counts[i] / total_shots for i in range(num_candidates)]

    # Plot side by side
    x = range(num_candidates)
    ax2.bar([i - 0.2 for i in x], classical_scores, width=0.4,
            color='gray', alpha=0.6, label="Classical (score)")
    ax2.bar([i + 0.2 for i in x], quantum_probs, width=0.4,
            color='purple', alpha=0.7, label="Quantum (probability)")

    ax2.set_title("Classical vs Quantum Path Selection")
    ax2.set_xlabel("Path index")
    ax2.set_ylabel("Score / Probability (0–1)")
    ax2.set_ylim(0, 1)
    ax2.legend()

# --- TextBox for vehicle count ---
axbox = plt.axes([0.35, 0.05, 0.5, 0.05])
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

# --- TextBox for candidate paths (k) ---
axkbox = plt.axes([0.35, 0.12, 0.5, 0.05])
k_box = TextBox(axkbox, 'Num of Paths (k): ', initial=str(k_candidates))

def submit_k(text):
    global k_candidates, best_path, quantum_counts, quantum_shots, vehicles
    try:
        k = int(text)
        if k > 0:
            k_candidates = k
            best_path, quantum_counts, quantum_shots = quantum_optimize(G, start_node, end_node, k=k_candidates)
            vehicles[:] = init_vehicles(len(vehicles))
            print(f"Updated to top-{k} candidate paths")
    except ValueError:
        print("Invalid k entered")

k_box.on_submit(submit_k)


# --- RadioButtons for graph selection ---
axradio = plt.axes([0.05, 0.05, 0.15, 0.15])
radio = RadioButtons(axradio, ('Demo Graph', 'Large Graph', 'City Graph'))

def graph_selector(label):
    global G, pos, best_path, quantum_counts, quantum_shots, start_node, end_node, vehicles
    if label == 'Demo Graph':
        G, pos = get_demo_graph()
        start_node, end_node = "A", "D"
    elif label == 'Large Graph':
        G, pos = get_large_graph()
        start_node, end_node = "A", "G"
    else:
        G, pos = get_city_graph()
        start_node, end_node = "A", "H"

    best_path, quantum_counts, quantum_shots = quantum_optimize(G, start_node, end_node)
    vehicles[:] = init_vehicles(len(vehicles))
    print(f"Switched to {label}")


radio.on_clicked(graph_selector)

# --- Run animation ---
ani = animation.FuncAnimation(fig, animate, frames=200, interval=100)
plt.show()
