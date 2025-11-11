#!/usr/bin/env python3

import nbformat as nbf
from pathlib import Path
from datetime import datetime

nb = nbf.v4.new_notebook()
nb['cells'] = []

date_time = datetime.now()

#f"{output_dir}REPORT/QMD/about_workflow.ipynb"
jupyter = Path(snakemake.output.about_ipynb)
name_jupyter = jupyter.stem
dir_jupyter = jupyter.parent
jupyter = jupyter.resolve().as_posix()

header = """---
format: 
  html:
    code-fold: false
    toc: true
    toc-depth: 3
    toc-expand: 2
jupyter: python3
execute: 
  echo: false
  warning: false
  message: false
  error: false
  cache: false
---
"""

nb['cells'].append(nbf.v4.new_markdown_cell(header))

text = """
# About Workflow 

## Version of tools used
"""

code_version = f"""
import pandas as pd
from pathlib import Path
from IPython.display import display, Markdown

# create a sample DataFrame
df = pd.read_csv('{snakemake.params.versions}', index_col=False)
df.sort_values(by=df.columns[0], axis=0, inplace=True)

# print the DataFrame
Markdown(df.to_markdown(index=False))
"""
nb['cells'].append(nbf.v4.new_markdown_cell(text))

nb['cells'].append(nbf.v4.new_code_cell(code_version))

text = f"""
## Rulegraph

![dag_file]({Path(snakemake.input.dag).name}){{.center}}

## Config file Parameters

```yaml
{snakemake.params.config_yaml}
```
"""

nb['cells'].append(nbf.v4.new_markdown_cell(text))

with open(jupyter, 'w') as f:
    nbf.write(nb, f)
