# 🧠 AIMA Toolkit — Artificial Intelligence Algorithms in Python

The **AIMA Toolkit** is a **personal project** that re-implements and extends the algorithms described in *Artificial Intelligence: A Modern Approach (4th Edition)* by Russell & Norvig — written entirely from scratch in Python.  

It serves as a **modular foundation for AI experimentation**, algorithm benchmarking, and educational purposes.  
The package is now published on PyPI and will continue to expand over time with detailed documentation and advanced examples.

> 📘 **Note:** As of now, there is no documentation available since this is a solo projects. But I will make one as I continue to make progress in the development of this repository

---

## 📦 Installation

Available on [PyPI](https://pypi.org/project/aima-toolkit/):

```bash
pip install aima-toolkit
```
---

## 🧩 Current Capabilities

The **AIMA Toolkit** currently supports a growing suite of intelligent agents, search algorithms, and problem-solving paradigms.

### 🤖 Search Agents

Supports the creation of both **simple** and **advanced agents**, including:

- **Sensorless Search Agents**
- **Partially Observable Agents**
- **Fully Observable Agents**
- **Deterministic and Non-Deterministic Agents**
- **Online and Offline Agents**
- **Informed & Uninformed Search Variants**

Each agent type can be combined with search strategies such as A*, BFS, DFS, Uniform-Cost, Greedy Best-First, Iterative Deepening, and much more.

---

### 🔢 Constraint Satisfaction Problems (CSP)

The toolkit includes a fully modular **CSP framework**, allowing easy definition and solving of different constraint types:

- **Variable and domain registration**
- **AllDiff, Binary, and Custom constraints**

---

### 🧮 Local Search

Implements a wide range of **local search algorithms**, including:
- Hill Climbing (with and without random restarts)
- Simulated Annealing
- Stochastic Beam Search
- Genetic Algorithms (planned extension)

These algorithms are designed for optimization, learning, and CSP problems where global solutions are infeasible to compute directly.

---

## 🧠 Demonstration Projects

To showcase the toolkit’s power, I’ve developed two full-featured projects based entirely on this framework:

| Project | Description | Repository |
|----------|--------------|-------------|
| 🧩 **N-Puzzle Solver** | A Disjoint Pattern Database (PDB) enhanced N-Puzzle solver built on top of the AIMA Toolkit’s A* infrastructure. | [🔗 View on GitHub](https://github.com/EmreArapcicUevak/N-puzzle-Solver) |
| 🔢 **Sudoku All-in-One** | A comprehensive Sudoku CSP solver supporting Classic, Diagonal, Kropki, and German Whispers variants — using advanced constraint propagation from AIMA Toolkit. | [🔗 View on GitHub](https://github.com/EmreArapcicUevak/sudoku-all-in-one) |

These serve as **live examples** of the toolkit’s modularity and its use in building powerful AI applications.

---

## 🧬 Project Philosophy

This project aims to create a **comprehensive, modular, and educational AI framework** that remains close to theoretical foundations while being practical for modern Python environments.

Core principles:
- 🧩 Readable and modular implementations  
- 🧠 Faithful to algorithmic definitions from *AIMA (4th Ed.)*  
- ⚙️ Designed for learning, experimentation, and scalability  

---


## 💬 Author

**Emre Arapčić-Uevak**  
📍 Bosnia & Herzegovina  
🎓 Computer Science & Engineering — International University of Sarajevo  
🔗 [GitHub Profile](https://github.com/EmreArapcicUevak)

---

## 🪶 License

This project is licensed under the **MIT License**.  
See [LICENSE](LICENSE) for details.