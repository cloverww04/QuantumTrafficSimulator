# 🚀 Project Overview

Quantum Traffic Simulator demonstrates how quantum computing can optimize real-world problems. This project combines a quantum algorithm simulation (Grover’s algorithm) with a visual traffic network, animating vehicles along paths selected by quantum probabilities and showing a side histogram of quantum measurement counts.

## Features

- Quantum Optimization: Uses a simplified Grover’s algorithm simulation to determine the “shortest” or most optimal path in the network. Returns both the path and the quantum counts.

- Vehicle Animation: Animates a vehicle moving along the quantum-selected path.

- Quantum Probabilities: A side histogram displays the quantum “counts” from the simulation integrated with the animation.

- Edge Highlighting: Quantum-optimized paths are shown with thicker/red edges to indicate higher probability selection.

## Current Behavior

- The vehicle moves along the optimized path from start to end.

- Once it reaches the final node (destination), the vehicle loops back to the start automatically, allowing continuous animation.

- The histogram is displayed alongside the network and updates dynamically with the animation.

- Supports multiple vehicles moving simultaneously.

- Allows for selection between different nodes/edges for complex traffic simulations.


## Future Improvements

- Use real quantum counts from Grover’s algorithm for more realistic path probabilities.

- Add interactive visualization to dynamically update edge colors and widths based on quantum results.

## Activate Virtual Environment and Install Dependencies
1. ```python -m venv venv```
2. ```pip install -r requirements.txt```

## Run
1. ```python main.py```


## Example

 <img src="https://github.com/user-attachments/assets/1a5d2929-8c09-48e7-b0c9-d4f55fd5a92d" width="1100px" height="500px" />