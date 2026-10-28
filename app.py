import streamlit as st

from algo import (
    METRES_PER_UNIT,
    dijkstra,
    floor_of,
    is_lift,
    load_map,
    to_real_units,
)

st.set_page_config(page_title="PathPilot", page_icon="🧭", layout="centered")

FLOOR_NAMES = {0: "Ground floor", 1: "1st floor", 2: "2nd floor", 3: "3rd floor"}
BLOCK_NAMES = {"A": "Block A", "B": "Block B"}


@st.cache_data
def get_map():
    return load_map()


def describe(node):
    """Human-friendly label for a node code."""
    if node[0] == "J":
        return f"Junction {node}"
    if node[0] == "S":
        return f"Stairs {node}"
    if node[0] == "G":
        return f"Gents toilet {node}"
    if node[0] == "L":
        return f"Ladies toilet {node}"
    return f"Room {node}"


def place_picker(label, key, building_map):
    """Floor dropdown + place dropdown. Returns the chosen node code."""
    st.subheader(label)
    floor = st.selectbox("Floor", list(FLOOR_NAMES), format_func=FLOOR_NAMES.get, key=f"{key}_floor")
    options = sorted(
        n for n in building_map
        if not is_lift(n) and n[0] in "ABGL" and floor_of(n) == floor
    )
    return st.selectbox("Place", options, format_func=describe, key=f"{key}_place")


building_map = get_map()

st.title("PathPilot")
st.caption("Shortest walking route between two places on campus")

col1, col2 = st.columns(2)
with col1:
    start = place_picker("From", "start", building_map)
with col2:
    destination = place_picker("To", "dest", building_map)

if st.button("Find shortest route", type="primary", use_container_width=True):
    if start == destination:
        st.info("You are already there!")
    else:
        try:
            path, units = dijkstra(building_map, start, destination)
            metres, steps, seconds = to_real_units(units)

            m1, m2, m3 = st.columns(3)
            m1.metric("Distance", f"{metres:.0f} m")
            m2.metric("Steps", f"{steps:g}")
            m3.metric("Time", f"{seconds / 60:.1f} min")

            if floor_of(start) != floor_of(destination):
                st.warning(
                    f"Floor change: {FLOOR_NAMES[floor_of(start)]} → "
                    f"{FLOOR_NAMES[floor_of(destination)]} (via stairs)"
                )

            st.subheader("Route")
            st.write(" → ".join(path))

            with st.expander("Step-by-step walk"):
                for i in range(len(path) - 1):
                    a, b = path[i], path[i + 1]
                    st.write(f"{i + 1}. {describe(a)} → {describe(b)}  ({building_map[a][b]} steps)")

            st.caption(
                f"Rough estimate: 1 map unit ≈ 1 step ≈ {METRES_PER_UNIT} m. "
                "Not an exact measurement."
            )
        except ValueError as error:
            st.error(str(error))