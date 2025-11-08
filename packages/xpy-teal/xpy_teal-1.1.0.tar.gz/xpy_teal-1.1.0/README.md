# 🌌 XPy-Teal: XP Tool for Emission and Absorption Lines

XPy-Teal is a Python version of the tool developed by [M. Weiler et al. 2023](https://arxiv.org/abs/2211.06946) for the analysis of Gaia DR3 XP spectra.
This repository provides a modular Python toolkit for downloading, processing, and analyzing **Gaia DR3 XP (BP/RP) spectra**.  
It includes tools for XP data retrieval via the Gaia Archive, data calibration, equivalent width measurement, and mathematical utilities for line analysis.

⚠️ Note: The current version only supports the **Narrow Line Approximation** for equivalent width measurements. See the [original paper](https://arxiv.org/abs/2211.06946) for more details.
---

## 📁 Repository Structure

```
/
├── src
│   └── xpy_teal
│       ├── Codes
│       │   ├── __init__.py
│       │   ├── config.py
│       │   ├── dataIO.py
│       │   ├── download_xp_spectra.py
│       │   ├── line_analysis.py
│       │   ├── main_MareNostrum.py
│       │   ├── math_tools.py
│       │   ├── spectrum_tools.py
│       │   └── xpy_teal_pipeline.py
│       ├── Configuration_Data
│       │   ├── BasisTransformationMatrix_BP.csv
│       │   ├── BasisTransformationMatrix_RP.csv
│       │   ├── DerivativeMatrix_D1.csv
│       │   ├── DerivativeMatrix_D2.csv
│       │   ├── DerivativeMatrix_D3.csv
│       │   ├── DerivativeMatrix_D4.csv
│       │   ├── HermiteIntegrals.csv
│       │   ├── LSFModel_BP.csv
│       │   ├── LSFModel_RP.csv
│       │   ├── RootMatrix_H.csv
│       │   ├── bpC03_v375wi_dispersion.csv
│       │   ├── bpC03_v375wi_response.csv
│       │   ├── rpC03_v142r_dispersion.csv
│       │   └── rpC03_v142r_response.csv
│       └── __init__.py
├── examples
│   ├── XPy_TEAL_Results
│   │   ├── Test_EqWidths.csv
│   │   ├── Test_Extrema.pkl
│   │   └── xp_continuous_downloaded.csv
│   ├── XPy_TEAL_config.xml
│   ├── source_ids.csv
│   └── tutorial.ipynb
├── LICENSE
├── README.md
├── pyproject.toml
└── uv.lock


```

---

## ⚙️ Installation

⚡ Option 1 — Using uv (recommended for speed)

uv is a fast, modern Python package manager built by Astral — it handles environments, dependencies, and builds efficiently.

🪄 Step 1 — Install uv

If you don’t have it already, install with:
```
pip install uv
```
or (recommended):

```
curl -LsSf https://astral.sh/uv/install.sh | sh
```

⚙️ Step 2 — Install XPy-Teal
In the root of this repository, run:
```
uv pip install xpy-teal
```
🚀 Step 3 — uv sync
```
uv sync
```
---

## 🚀 Usage

Here is a simple example of how to use XPy-Teal to run the analysis pipeline on a table of source IDs from Gaia DR3.

```python
from xpy_teal import xpy_teal_pipeline as xpy

results = xpy.run_pipeline(sources_table)
```

---


## 📄 License

GNU GENERAL PUBLIC LICENSE

---

