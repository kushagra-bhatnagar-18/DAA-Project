"""Drawing helpers: show a route on a clean floor schematic or on the real floor-plan photo."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

from layout import PHOTO_REF_SIZE, photo_position, position

PHOTO_DIR = Path(__file__).resolve().parent / "floorplans"
ROUTE_COLOUR = "#e8590c"
START_COLOUR = "#2f9e44"
END_COLOUR = "#c92a2a"


def floor_photo(floor):
    """Path of the floor-plan photo if we have one for this floor, else None."""
    p = PHOTO_DIR / f"floor{floor}.jpg"
    return p if p.exists() else None


def _floor_of(node):
    return int(node[1])


def _segments(path, floor):
    """Split the route into runs of consecutive nodes that are on this floor."""
    runs, run = [], []
    for node in path:
        if _floor_of(node) == floor:
            run.append(node)
        elif run:
            runs.append(run)
            run = []
    if run:
        runs.append(run)
    return runs


def _draw_route(ax, path, floor, photo=False):
    def pt(n):
        return photo_position(n, floor) if photo else position(n)

    for run in _segments(path, floor):
        xs, ys = zip(*(pt(n) for n in run))
        ax.plot(xs, ys, "-", color=ROUTE_COLOUR, lw=4, solid_capstyle="round", zorder=5)
        ax.plot(xs, ys, "o", color=ROUTE_COLOUR, ms=4, zorder=6)

    on_floor = [n for n in path if _floor_of(n) == floor]
    if not on_floor:
        return
    if path[0] in on_floor:
        x, y = pt(path[0])
        ax.plot(x, y, "o", color=START_COLOUR, ms=11, mec="white", mew=2, zorder=8)
        ax.annotate("START", (x, y), (0, 14), textcoords="offset points", ha="center",
                    fontsize=8, fontweight="bold", color=START_COLOUR, zorder=9)
    if path[-1] in on_floor:
        x, y = pt(path[-1])
        ax.plot(x, y, "o", color=END_COLOUR, ms=11, mec="white", mew=2, zorder=8)
        ax.annotate("END", (x, y), (0, 14), textcoords="offset points", ha="center",
                    fontsize=8, fontweight="bold", color=END_COLOUR, zorder=9)
    # Stairs where the route enters or leaves this floor
    for n in on_floor:
        if n[0] == "S":
            neighbours_off = [
                m for m in (path[i] for i in range(len(path)))
                if _floor_of(m) != floor and m[0] == "S"
            ]
            if neighbours_off:
                x, y = pt(n)
                ax.plot(x, y, "^", color="#1c7ed6", ms=11, mec="white", mew=1.5, zorder=7)


def schematic_figure(building_map, floor, path):
    """Clean drawing: corridors as grey lines, rooms as boxes, route on top."""
    fig, ax = plt.subplots(figsize=(9, 6.8))
    w, h = PHOTO_REF_SIZE

    # corridors
    drawn = set()
    for a, nbrs in building_map.items():
        if a[0] == "E" or _floor_of(a) != floor or a[0] not in "JS":
            continue
        for b in nbrs:
            if b[0] not in "JS" or b[0] == "E" or _floor_of(b) != floor:
                continue
            if (b, a) in drawn:
                continue
            drawn.add((a, b))
            (x1, y1), (x2, y2) = position(a), position(b)
            ax.plot([x1, x2], [y1, y2], "-", color="#ced4da", lw=2, zorder=1)

    # rooms / toilets / stairs
    for n in building_map:
        if n[0] == "E" or _floor_of(n) != floor or n[0] == "J":
            continue
        x, y = position(n)
        if n[0] == "S":
            ax.plot(x, y, "s", color="#74c0fc", ms=9, zorder=2)
            continue
        colour = {"A": "#d0ebff", "B": "#d3f9d8", "G": "#fff3bf", "L": "#ffdeeb"}[n[0]]
        ax.add_patch(FancyBboxPatch((x - 18, y - 13), 36, 26, boxstyle="round,pad=2",
                                    fc=colour, ec="#868e96", lw=0.8, zorder=2))
        ax.text(x, y, n, ha="center", va="center", fontsize=6, zorder=3)

    _draw_route(ax, path, floor)
    ax.set_xlim(150, w - 140)
    ax.set_ylim(870, 140)  # inverted y like an image
    ax.set_aspect("equal")
    ax.axis("off")
    fig.tight_layout()
    return fig


def photo_figure(floor, path):
    """Route drawn on top of the real floor-plan photo."""
    img = plt.imread(floor_photo(floor))
    fig, ax = plt.subplots(figsize=(9, 6.8))
    ax.imshow(img)
    _draw_route(ax, path, floor, photo=True)
    ax.axis("off")
    fig.tight_layout()
    return fig