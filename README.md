# PathPilot: Campus Shortest Path Finder (Blocks A & B)

A Design and Analysis of Algorithms project that finds the shortest walking route between two places (rooms, toilets, stairs) in Blocks A and B of the School of Computer Engineering, KIIT, using **Dijkstra's algorithm**.

Every place is a **node** and every walkable connection is an **edge** weighted by the number of **steps counted on campus**. The result is shown in steps, with an approximate conversion to metres and walking time.

---

## Features

- Shortest route between any two places on all four floors (ground to 3rd floor)
- Distance in **counted steps**, plus approximate metres and time
- Floor changes by **stairs only** (lifts are excluded, as instructed)
- Rooms, labs and toilets are only start or end points. A route never walks through a classroom.
- Two ways to use it:
  - **Terminal program** (`algorithim.py`)
  - **Web page with Streamlit** (`app_simple.py` for a plain version, `app.py` with route drawn on the floor plans)

---

## Project structure

```
PathPilot/
├── algo.py        # Dijkstra + terminal program (the core algorithm)
├── Maps.json            # The campus graph: places and counted steps between them
├── app.py               # Streamlit page with route drawn on diagram / floor-plan photos
├── visual.py            # Drawing code used by app.py
├── layout.py            # Approximate (x, y) position of every place, used by app.py
├── requirements.txt     # Python libraries needed

```

---

## Setup

1. Install **Python 3.9 or newer** (tick "Add Python to PATH" on Windows).
2. Put all the files in one folder, keeping the `floorplans` folder.
3. Open the folder in a terminal (or VS Code) and install the libraries:

```
python -m pip install -r requirements.txt
```

(The terminal program needs no libraries at all. Streamlit and matplotlib are only for the web page.)

---

## How to run

### Terminal version

```
python algorithim.py
```

Type a start and a destination, for example `A001` and `A018`. Type `Q` to quit.

Example output:

```
A001 -> J003 -> J002 -> J001 -> J032 -> J031 -> A018

Distance (counted steps) : 40 steps
Approx. in metres        : 28 m  (at 0.7 m per step)
Approx. walking time     : 0.4 min (23 s)
```

### Web page (Streamlit)

Web Page version:

```
python -m streamlit run app.py
```

The page opens at `http://localhost:8501`. Choose a floor and a place for "From" and "To", then click **Find shortest route**. Press `Ctrl+C` in the terminal to stop it.

If `streamlit` is "not recognized", always start it with `python -m streamlit ...` as shown above.

---

## Place codes

| Code | Meaning | Example |
|---|---|---|
| `A###` | Room in Block A | `A003` |
| `B###` | Room in Block B | `B318` |
| `J###` | Junction (a point in a corridor where paths meet or a door connects) | `J031` |
| `S###` | Staircase | `S007` |
| `G##` | Gents toilet | `G01` |
| `L##` | Ladies toilet | `L02` |
| `E###` | Lift (**not used**) | `E001` |

The **second character is the floor**: `A003` is ground floor, `A118` is 1st floor, `B318` is 3rd floor, `J205` is a 2nd-floor junction.

---

## How it works

1. **The graph.** `Maps.json` stores each place and its neighbours with the counted steps between them, for example `"J003": {"J002": 5, "A001": 5, "J004": 15}`.
2. **Dijkstra's algorithm.** It keeps the best known distance to every node (infinity at first, 0 at the start) and uses a min-heap to always process the closest unvisited node. For each neighbour it checks whether going through the current node is shorter. It stops as soon as the destination is taken out of the heap, because with positive weights that distance can no longer improve.
3. **Rebuilding the route.** Each time a distance improves, the code remembers where it came from. Following these links back from the destination and reversing them gives the route.
4. **Rules applied.**
   - Only junctions and stairs can be passed through. Rooms and toilets can only be the first or last stop.
5. **Conversion.** `metres = steps x STEP_LENGTH_M` and `time = metres / walking speed`.

**Complexity:** with a binary heap, O((V + E) log V), where V is the number of places (394) and E the number of connections.

---

## About the distances

- The numbers in `Maps.json` are **real counted steps**, taken by walking the campus.
- **Metres are an approximation.** They use `STEP_LENGTH_M = 0.7` (a typical adult step) in `algorithim.py`. To use your own step length, walk 10 m, count your steps, and divide 10 by the count. Then change the value:

```python
STEP_LENGTH_M = 0.7
```

- Walking time assumes 1.2 m/s (`WALKING_SPEED_MPS`).

---

## Floor-plan drawings (app.py)

`app.py` shows the route on a clean diagram or on the real floor-plan photos, with one tab per floor the route passes through. Orange is the route, green the start, red the end, and a blue triangle marks stairs.

The positions of places on the drawings were read off the plan photos by eye and are **approximate**. They only affect the pictures, never the distances. To nudge a place, edit its number in `layout.py` (the same position is used on every floor).

---

## Limitations

- Lifts are not included (by instruction). The lift nodes in `Maps.json` are ignored.
- Metres and time are approximate because they depend on step length and walking speed.
- Only Blocks A and B are mapped. Block C and outdoor paths are not.
- Stair-climbing effort is not modelled beyond the counted steps.
- Drawing positions are approximate (see above).

---

## Possible future work

- Add lifts back with an "accessible route" option
- Compare Dijkstra with BFS and A* (nodes visited and run time)
- Nearest toilet or exit finder
- Add Block C and outdoor routes

---

## Built with

Python, `heapq` (priority queue), Streamlit, Matplotlib

## Authors

Kushagra Bhatnagar
Soumabho Dey
