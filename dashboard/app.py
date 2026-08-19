"""Local, no-code BHSI explorer for OLC learning and community review."""
from pathlib import Path
import sys

import numpy as np
import rasterio
import streamlit as st
import matplotlib.pyplot as plt

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
from src.constants import BHSI_WEIGHTS, OUTPUTS_DIR  # noqa: E402

st.set_page_config(page_title="Pine Ridge Bison Habitat Explorer", layout="wide")
st.title("Pine Ridge Bison Habitat Explorer")
st.caption("A learning and discussion tool. It does not determine where bison belong or authorize land-management decisions.")

layer_paths = {
    "Vegetation": OUTPUTS_DIR/"bhsi_vegetation.tif",
    "Soils": OUTPUTS_DIR/"bhsi_soils.tif",
    "Topography": OUTPUTS_DIR/"bhsi_topography.tif",
    "Water access": OUTPUTS_DIR/"bhsi_water.tif",
    "Climate stress": OUTPUTS_DIR/"bhsi_climate.tif",
    "Combined BHSI": OUTPUTS_DIR/"bhsi_composite.tif",
}
missing = [name for name, path in layer_paths.items() if not path.exists()]
if missing:
    st.error("Run notebooks 02–07 first. Missing: " + ", ".join(missing))
    st.stop()

@st.cache_data(show_spinner=False)
def read_preview(path: str, max_side: int = 900):
    with rasterio.open(path) as src:
        scale = min(1, max_side / max(src.width, src.height))
        h, w = max(1, int(src.height * scale)), max(1, int(src.width * scale))
        data = src.read(1, out_shape=(1, h, w), masked=True).filled(np.nan)
    return data

choice = st.sidebar.selectbox("Map layer", list(layer_paths))
data = read_preview(str(layer_paths[choice]))
st.sidebar.markdown("### What am I seeing?")
st.sidebar.write("Red indicates lower suitability; green indicates higher suitability. Blank areas are outside the analysis boundary.")

left, right = st.columns([3, 1])
with left:
    fig, ax = plt.subplots(figsize=(9, 6))
    image = ax.imshow(data, cmap="RdYlGn", vmin=0, vmax=1, origin="upper")
    fig.colorbar(image, ax=ax, label="Suitability (0–1)")
    ax.set_axis_off()
    ax.set_title(choice)
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)
with right:
    valid = data[np.isfinite(data)]
    st.metric("Mean score", f"{valid.mean():.2f}")
    st.metric("Higher-score pixels (≥ 0.70)", f"{(valid >= 0.70).mean():.0%}")
    st.markdown("### Default BHSI weights")
    for name, weight in BHSI_WEIGHTS.items():
        st.write(f"{name.title()}: {weight:.0%}")

st.markdown("### Questions to explore")
st.write("What patterns do you notice? Which data layer most changes the map? What information from the land or community should be considered before interpreting a high-score area?")
st.info("Before sharing results beyond the OLC/Oglala Lakota Nation partnership, follow the review process in documents/data_sovereignty.md.")
