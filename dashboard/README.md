# Pine Ridge Bison Habitat Explorer

This is a local, no-code learning and discussion dashboard for the BHSI series.
It reads `outputs/pine_ridge_bhsi_cube.nc` directly.

After running notebooks 01–07, start it from the inner repository folder:

```powershell
& C:\Users\gekek\miniconda3\envs\pine-ridge-bison\python.exe -m streamlit run dashboard/app.py --server.address=127.0.0.1 --server.port=8501 --browser.gatherUsageStats=false
```

This works without `conda activate` and bypasses Streamlit's optional email
prompt. Open `http://127.0.0.1:8501` and keep the terminal open while using
the dashboard.

It provides four learning views: cube exploration, side-by-side layer
comparison, hypothetical weighting scenarios, and a learning guide. Map
previews are downsampled so the dashboard remains responsive on ordinary
student laptops; point inspection uses the original cube resolution.
It does not publish data and is not a management-decision tool.
