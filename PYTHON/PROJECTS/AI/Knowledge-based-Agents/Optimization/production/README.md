Production — Linear Programming (SciPy)

Goal

- Minimize cost: 50·x1 + 80·x2 subject to linear constraints.

Formulation (ASCII)

- Objective: minimize 50*x1 + 80*x2
- Subject to:
  5*x1 + 2*x2 <= 20
  10*x1 + 12*x2 >= 90 (written in code as -10*x1 -12*x2 <= -90)
- Defaults: x1, x2 >= 0 (SciPy linprog default)

Key file

- production.py: calls scipy.optimize.linprog and prints optimal x1, x2 if feasible.

Dependencies

- Python 3.9+
- SciPy

Install (PowerShell)

```powershell
pip install scipy
```

Run

```powershell
cd "z:\🍵\MyPROJECTS\PYTHON\PROJECTS\AI\Knowledge-based-Agents\Optimization\production"
python production.py
```

Notes

- If the problem is infeasible, the script prints "No solution".
- You can add bounds or more constraints by editing the A_ub/b_ub matrices, c vector, and bounds parameter of linprog.
