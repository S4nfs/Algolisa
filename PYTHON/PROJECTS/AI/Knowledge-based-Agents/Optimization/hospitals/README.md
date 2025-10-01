Hospitals — Local Search (Hill Climbing)

Goal

- Place k hospitals on a grid to minimize the total Manhattan distance from each house to its nearest hospital.

Idea (Hill Climbing)

- Start with k random hospital locations on empty cells.
- Repeatedly move one hospital to a neighboring empty cell if it reduces the total cost.
- Stop when no neighbor improves the cost (local optimum). Optional: run multiple random restarts.

ASCII sketch
Grid cells, H = house, + = hospital

```
  0 1 2 3 4 5

0 . H . . . .
1 . . . + . .
2 . . . . . H
3 . H . . . .
4 . . . . + .

```

Cost = sum over houses of |r_house - r_nearest+| + |c_house - c_nearest+|

Key files

- hospitals.py: Space class, cost function, hill_climb, random_restart, image rendering.
- assets/images/House.png and Hospital.png for visualization.
- assets/fonts/OpenSans-Regular.ttf for cost label.

Dependencies

- Python 3.9+
- Pillow (PIL fork) for image rendering

Install dependency (PowerShell)

```powershell
pip install pillow
```

Run

- Generates step images: hospitals000.png, hospitals001.png, ...
- Prints cost improvements when log=True.

```powershell
cd "z:\🍵\MyPROJECTS\PYTHON\PROJECTS\AI\Knowledge-based-Agents\Optimization\hospitals"
python hospitals.py
```

Notes

- Images are saved alongside the script (hospitals000.png ...).
- For reproducibility, you can seed Python’s RNG (e.g., random.seed(0)).
- random_restart(maximum) will run multiple hill climbs and keep the best.
