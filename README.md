# AI Assignment 2 - Dynamic Pathfinding Agent

## Requirements
- Python 3.10+
- pygame

## Installation

Install dependencies:

pip install pygame

## How to Run

1. Clone the repository
2. Navigate to project folder
3. Run:

python main.py

## Controls

G - Generate random map
A - Toggle between A* and GBFS
H - Toggle heuristic (Manhattan / Euclidean)
D - Toggle dynamic obstacle mode
E - Toggle edit mode (click to add/remove walls)
S - Start search
Q - Quit

## Test Cases

Best Case:
- Start: (0,0)
- Goal: (19,19)
- Low obstacle density

Worst Case:
- Start: (0,0)
- Goal: (19,19)
- High obstacle density (45%+)
