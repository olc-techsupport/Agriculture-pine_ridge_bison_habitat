"""Local, no-code explorer for the Pine Ridge BHSI NetCDF data cube."""
from pathlib import Path
import sys

import numpy as np
import streamlit as st
import xarray as xr

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
from src.constants import BHSI_WEIGHTS, OUTPUTS_DIR  # noqa: E402

CUBE_PATH = OUTPUTS_DIR / "pine_ridge_bhsi_cube.nc"
COMPONENTS = ["vegetation", "soils", "topography", "water", "climate"]

st.set_page_config(page_title="Pine Ridge Bison Habitat Explorer", layout="wide")
st.title("Pine Ridge Bison Habitat Explorer")
st.caption("A learning and discussion tool. It does not determine where bison belong or authorize land-management decisions.")

if not CUBE_PATH.exists():
    st.error("Data cube not found. Run `python build_data_cube.py` from the inner project folder first.")
    st.stop()


@st.cache_resource
def open_cube(path: str):
    return xr.open_dataset(path)


@st.cache_data(show_spinner=False)
def preview(path: str, variable: str, max_side: int = 600):
    cube = xr.open_dataset(path)
    step = max(1, int(np.ceil(max(cube.sizes["x"], cube.sizes["y"]) / max_side)))
    return cube[variable].isel(y=slice(None, None, step), x=slice(None, None, step)).values


def draw_map(data: np.ndarray, title: str):
    """Show a quick red-to-green suitability preview without Matplotlib."""
    values = np.asarray(data, dtype=np.float32)
    valid = np.isfinite(values)
    score = np.nan_to_num(np.clip(values, 0, 1), nan=0.0)
    image = np.zeros((*score.shape, 3), dtype=np.uint8)
    image[..., 0] = np.round(220 * (1 - score)).astype(np.uint8)  # red: low
    image[..., 1] = np.round(80 + 150 * score).astype(np.uint8)   # green: high
    image[~valid] = (35, 35, 35)  # no data
    st.image(image, caption=f"{title} — red: lower score; green: higher score", width="stretch")


cube = open_cube(str(CUBE_PATH))
# `st.tabs` computes every tab on every rerun.  A single view picker keeps the
# first page lightweight enough for ordinary student laptops and local servers.
view = st.radio(
    "Choose a view",
    ["Explore the cube", "Compare layers", "Try weights", "Learning guide"],
    horizontal=True,
    label_visibility="collapsed",
)

if view == "Explore the cube":
    variable = st.selectbox("Choose a data-cube layer", list(cube.data_vars), format_func=str.title)
    if st.button("Show selected map", type="primary"):
        data = preview(str(CUBE_PATH), variable)
        left, right = st.columns([3, 1])
        with left:
            draw_map(data, variable.replace("_", " ").title())
        with right:
            valid = data[np.isfinite(data)]
            st.metric("Mean score", f"{valid.mean():.2f}")
            st.metric("Higher-score pixels (≥ 0.70)", f"{(valid >= 0.70).mean():.0%}")
            st.write(f"Grid resolution: {cube.attrs.get('grid_resolution_m', 'unknown')} m")
            st.write(f"CRS: {cube.attrs.get('crs', 'unknown')}")
    else:
        st.info("Choose a layer, then select **Show selected map**. Keeping the first page light helps the local dashboard open reliably.")

    st.markdown("#### Inspect one location")
    col1, col2 = st.columns(2)
    row = col1.slider("North–south grid row", 0, cube.sizes["y"] - 1, cube.sizes["y"] // 2)
    col = col2.slider("West–east grid column", 0, cube.sizes["x"] - 1, cube.sizes["x"] // 2)
    point = {name: float(cube[name].isel(y=row, x=col).values) for name in cube.data_vars}
    st.dataframe({"Layer": [name.title() for name in point], "Score": list(point.values())}, hide_index=True)

elif view == "Compare layers":
    first, second = st.columns(2)
    left_name = first.selectbox("First layer", list(cube.data_vars), index=0, format_func=str.title)
    right_name = second.selectbox("Second layer", list(cube.data_vars), index=min(1, len(cube.data_vars) - 1), format_func=str.title)
    left_data, right_data = preview(str(CUBE_PATH), left_name), preview(str(CUBE_PATH), right_name)
    a, b = st.columns(2)
    with a:
        draw_map(left_data, left_name.title())
    with b:
        draw_map(right_data, right_name.title())
    st.write("Ask: where do the layers agree, where do they differ, and what local knowledge would help interpret those differences?")

elif view == "Try weights":
    st.write("Move the sliders to explore a hypothetical weighting scenario. This is for learning, not a management recommendation.")
    weights = {name: st.slider(name.title(), 0.0, 1.0, float(BHSI_WEIGHTS[name]), 0.05) for name in COMPONENTS}
    total = sum(weights.values())
    if total == 0:
        st.warning("Choose at least one non-zero weight.")
    else:
        arrays = [preview(str(CUBE_PATH), name) for name in COMPONENTS]
        scenario = sum(arr * weights[name] for arr, name in zip(arrays, COMPONENTS)) / total
        draw_map(scenario, "Your hypothetical BHSI scenario")
        st.caption("Weights are normalized to sum to 1 for display.")

else:
    st.markdown("### Questions to explore")
    st.markdown("- What patterns do you notice in each layer?\n- Which layers most change the combined map?\n- What does this cube not know about the land, water, or community?\n- What observations would help ground-truth a candidate area?")
    st.markdown("Read `documents/olc_learning_lab.md` for activities and further-study ideas.")
    st.info("Before sharing results outside the OLC/Oglala Lakota Nation partnership, follow the review process in documents/data_sovereignty.md.")
