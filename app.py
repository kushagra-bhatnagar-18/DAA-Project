import streamlit as st

from algo import (
    STEP_LENGTH_M,
    dijkstra,
    floor_of,
    is_lift,
    load_map,
    to_real_units,
)
from visual import floor_photo, photo_figure, schematic_figure

st.set_page_config(page_title="PathPilot", page_icon="🧭", layout="centered")

FLOOR_NAMES = {0: "Ground floor", 1: "1st floor", 2: "2nd floor", 3: "3rd floor"}


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

st.title("🧭 PathPilot")
st.caption("Shortest walking route between two places on campus (lifts not included)")

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
            # keep result for reruns (changing the view toggle reruns the script)
            st.session_state["result"] = (start, destination, path, units)
        except ValueError as error:
            st.session_state.pop("result", None)
            st.error(str(error))

if "result" in st.session_state:
    start, destination, path, units = st.session_state["result"]
    metres, steps, seconds = to_real_units(units)

    m1, m2, m3 = st.columns(3)
    m1.metric("Steps (counted)", f"{steps:g}")
    m2.metric("Approx. distance", f"{metres:.0f} m")
    m3.metric("Approx. time", f"{seconds / 60:.1f} min")

    if floor_of(start) != floor_of(destination):
        st.warning(
            f"Floor change: {FLOOR_NAMES[floor_of(start)]} → "
            f"{FLOOR_NAMES[floor_of(destination)]} (via stairs)"
        )

    st.subheader("Map")
    floors_used = sorted({floor_of(n) for n in path})
    has_photo = any(floor_photo(f) for f in floors_used)
    view = "Clean diagram"
    if has_photo:
        view = st.radio("View", ["Clean diagram", "Floor-plan photo"], horizontal=True)

    tabs = st.tabs([FLOOR_NAMES[f] for f in floors_used])
    for tab, floor in zip(tabs, floors_used):
        with tab:
            if view == "Floor-plan photo" and floor_photo(floor):
                st.pyplot(photo_figure(floor, path))
            else:
                if view == "Floor-plan photo":
                    st.caption("No photo added for this floor yet, showing the clean diagram.")
                st.pyplot(schematic_figure(building_map, floor, path))
    st.caption("Orange line = route, green = start, red = end, blue triangle = stairs. "
               "Positions are approximate.")

    st.subheader("Route")
    st.write(" → ".join(path))

    with st.expander("Step-by-step walk"):
        for i in range(len(path) - 1):
            a, b = path[i], path[i + 1]
            st.write(f"{i + 1}. {describe(a)} → {describe(b)}  ({building_map[a][b]} steps)")

    st.caption(
        "Distances are real counted steps. Metres assume "
        f"{STEP_LENGTH_M} m per step, so they are approximate."
    )