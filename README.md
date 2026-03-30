# Kakurasu-Puzzle-Solver
A Python-based graphical application designed to solve Kakurasu puzzles using Constraint Satisfaction Problem (CSP) techniques.

## Features
Interactive GUI: Built with tkinter for loading puzzles and visualizing solutions.

Dual Solving Algorithms:

Backtracking: Standard exhaustive search.

AC3 (Arc Consistency): Advanced solver with domain pruning.

Performance Metrics: Real-time tracking of Runtime and Nodes Visited.

Heuristics: Implementation of MRV (Minimum Remaining Values) and LCV (Least Constraining Value) to optimize the search process.

## How to Use
1. Requirements
Python 3.x

tkinter (standard Python library)

2. Input File Format
The solver requires a .txt file with the following structure:

Plaintext
3
1,2,3
3,2,1
(Line 1: Grid Size | Line 2: Row Targets | Line 3: Column Targets)

3. Running the App
Run the script: python COSC_4117EL_A1_G16.py

Click "Open" to load your puzzle file.

Select an algorithm (Backtracking or AC3) from the dropdown.

Click "Solve" to see the results on the grid.

## Core Components
KakurasuCSP: Handles the mathematical logic, sum constraints, and AI search algorithms.

KakurasuGUI: Manages the window interface, grid rendering, and file handling.
