# Pine Ridge Bison Habitat Explorer

This is a local, no-code learning and discussion dashboard for the BHSI series.
It reads `outputs/pine_ridge_bhsi_cube.nc` directly.

After running notebooks 01–07, start it from the repository root:

```bash
streamlit run dashboard/app.py
```

It provides four learning views: cube exploration, side-by-side layer
comparison, hypothetical weighting scenarios, and a learning guide. Map
previews are downsampled so the dashboard remains responsive on ordinary
student laptops; point inspection uses the original cube resolution.
It does not publish data and is not a management-decision tool.
