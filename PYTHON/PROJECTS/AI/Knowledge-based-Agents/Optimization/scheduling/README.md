Scheduling — CSP with Backtracking and Library Solver

Goal

- Assign each task {A..G} a day in {Monday, Tuesday, Wednesday} so that neighboring tasks are on different days.

Constraint graph (ASCII)
A -- B -- D
| \ | \  
C -- E -- F -- G
\
 (A-C, B-C, B-E, C-E, C-F, D-E, E-F, E-G, F-G)

Approaches

- schedule0.py: naive backtracking search
  - Picks next unassigned variable in order
  - Tries values in fixed order; backtracks on conflicts
- schedule1.py: python-constraint library
  - Adds variables and pairwise x != y constraints
  - Enumerates all solutions

Dependencies

- Python 3.9+
- For schedule1.py only: python-constraint

Install optional dependency (PowerShell)

```powershell
pip install python-constraint
```

Run (PowerShell)

- Naive backtracking (single solution):

```powershell
cd "z:\🍵\MyPROJECTS\PYTHON\PROJECTS\AI\Knowledge-based-Agents\Optimization\scheduling"
python .\schedule0.py
```

- Library solver (all solutions):

```powershell
python .\schedule1.py
```

Notes

- The domains are small enough to enumerate; with more variables, use heuristics (MRV, LCV) and inference (AC-3) for speed.
- To change the meeting days or graph, edit the VARIABLES list, domain values, and CONSTRAINTS pairs accordingly.
