# GeneXpressor

A friendly DESeq2 runner driven from Python via rpy2. It auto-discovers your counts/metadata, produces plots, CSVs, and an optional HTML report.

## Requirements
- **R** (≥ 4.x) installed and on PATH (on Windows set `R_HOME` or install R normally)
- R packages: `DESeq2`, `BiocParallel`, `dplyr`, `ggplot2`, `ggrepel`, `pheatmap`, `readr`, `tidyr`, `tibble`, `rmarkdown`, `RColorBrewer`
  - (optional) `readxl`, `arrow` for Excel/feather/parquet
- Python: `rpy2`

## Install (editable)
```bash
pip install -e .
