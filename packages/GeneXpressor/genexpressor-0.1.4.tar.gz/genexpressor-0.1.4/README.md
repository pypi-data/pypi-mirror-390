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


arguments

genexpressor \                                                                                                                                 
>>   --parent_dir "C:\Users\shahr\Downloads\Deseq2-pkg" \
>>   --pick AUTO \
>>   --case_level Disease --control_level Control \
>>   --alpha 0.05 --lfc_thr 2.0 --top_labels 20 --top_heatmap 50 \
>>   --make_report true --debug true --threads 2