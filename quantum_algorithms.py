import math
import networkx as nx
from itertools import islice
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import AerSimulator

def quantum_optimize(G, start, end, shots=1024, k=10):
    """
    Quantum-assisted shortest path selection using Grover's Algorithm (simulated).
    Limits to top-k candidate paths for scalability.
    Returns:
        shortest: list of nodes in the shortest path (classical shortest)
        counts: dict mapping integer path-index -> measured counts
        shots: number of measurement shots used
    """

    # 1) Generate at most k candidate paths using NetworkX's shortest_simple_paths
    try:
        all_paths = list(islice(nx.shortest_simple_paths(G, start, end, weight='weight'), k))
    except nx.NetworkXNoPath:
        return [], {}, shots

    N_paths = len(all_paths)
    if N_paths == 0:
        return [], {}, shots

    # 2) Classical weights
    def path_weight(path):
        return sum(G[path[i]][path[i+1]]['weight'] for i in range(len(path)-1))

    weights = [path_weight(p) for p in all_paths]
    min_weight = min(weights)
    marked_indexes = [i for i, w in enumerate(weights) if w == min_weight]
    shortest = all_paths[marked_indexes[0]]

    # 3) Number of qubits needed
    n_qubits = max(1, (N_paths - 1).bit_length())
    qc = QuantumCircuit(n_qubits, n_qubits)

    # 4) Initialize in uniform superposition
    qc.h(range(n_qubits))

    # ---- Grover Oracle (simplified: mark all shortest indexes) ----
    def apply_oracle():
        for idx in marked_indexes:
            bits = format(idx, f'0{n_qubits}b')
            for i, b in enumerate(bits):
                if b == '0':
                    qc.x(i)
            if n_qubits == 1:
                qc.z(0)
            else:
                qc.h(n_qubits-1)
                qc.mcx(list(range(n_qubits-1)), n_qubits-1)
                qc.h(n_qubits-1)
            for i, b in enumerate(bits):
                if b == '0':
                    qc.x(i)

    # ---- Diffuser ----
    def apply_diffuser():
        qc.h(range(n_qubits))
        qc.x(range(n_qubits))
        if n_qubits == 1:
            qc.z(0)
        else:
            qc.h(n_qubits-1)
            qc.mcx(list(range(n_qubits-1)), n_qubits-1)
            qc.h(n_qubits-1)
        qc.x(range(n_qubits))
        qc.h(range(n_qubits))

    # 5) Number of Grover iterations
    M = max(1, len(marked_indexes))
    N = 2 ** n_qubits
    r = int(math.floor((math.pi/4) * math.sqrt(N / M)))
    r = max(1, r)

    for _ in range(r):
        apply_oracle()
        apply_diffuser()

    # 6) Measurement
    qc.measure(range(n_qubits), range(n_qubits))

    simulator = AerSimulator()
    job = simulator.run(qc, shots=shots)
    result = job.result()
    raw_counts = result.get_counts(qc)

    # Convert bitstrings to indices
    counts_by_index = {}
    for bitstr, c in raw_counts.items():
        idx = int(bitstr, 2)
        if idx < N_paths:
            counts_by_index[idx] = counts_by_index.get(idx, 0) + c
    for i in range(N_paths):
        counts_by_index.setdefault(i, 0)

    return shortest, counts_by_index, shots
