#!/usr/bin/env python3

import nbformat as nbf
from pathlib import Path, PurePosixPath
from datetime import datetime

nb = nbf.v4.new_notebook()

date_time = datetime.now()
# methods
outliers_pcadapt_position = ""
outliers_lfmm_position = ""
# mapping and outliers
stats_pcadapt = ""
stats_lfmm = ""
# intersect after kmers mapping
stats_outliers_pcadapt = ""
stats_outliers_lfmm = ""
# kmers assembly 
contigs_pcadapt_csv = ""
contigs_lfmm_csv = ""
# intersect from contigs 
stats_contigs_pcadapt = ""
stats_contigs_lfmm = ""
options=[]


jupyter = snakemake.output[0]
jupyter = f"{Path(jupyter).resolve()}"
name_jupyter = PurePosixPath(jupyter).stem
dir_jupyter = PurePosixPath(jupyter).parent
csv = f"{dir_jupyter}/{name_jupyter}.csv"

# cp _quarto.yml to QMD rep before to changes inside
quarto_yml = snakemake.params["yml"]
book_dir_qmd = snakemake.params["book_dir_qmd"]
new_quarto_yml = f"{book_dir_qmd}_quarto.yml"

#print(snakemake.params['workflow_steps'])
#print(snakemake.input.keys())

##### variables from input
#if config['WORKFLOW']['SNMF']
if "method_diversity" in snakemake.input.keys():
    for ele in list(snakemake.input["method_diversity"]):
        if 'SNMF' in ele:
            out_snmf = ele

## if config['WORKFLOW']['PCADAPT'] or config['WORKFLOW']['LFMM']
if "method_kmers" in snakemake.input.keys():
    for ele in list(snakemake.input["method_kmers"]): 
        if 'PCADAPT' in ele:
            outliers_pcadapt = ele
        elif 'LFMM' in ele:
            outliers_lfmm = ele

##  if config['WORKFLOW']['MAPPING_KMERS']:
if "outliers_and_mapping" in snakemake.input.keys():
    for ele in list(snakemake.input["outliers_and_mapping"]):
        if 'PCADAPT' in ele:
            outliers_pcadapt_position = ele
        elif 'LFMM' in ele:
            outliers_lfmm_position = ele

if "stats" in snakemake.input.keys():
    for ele in list(snakemake.input["stats"]):
        if 'PCADAPT' in ele:
            stats_pcadapt = ele
        elif 'LFMM' in ele:
            stats_lfmm = ele

# if config['WORKFLOW']['ASSEMBLY_KMERS']:
if "outliers_csv" in snakemake.input.keys():
    for ele in list(snakemake.input["outliers_csv"]): 
        if 'PCADAPT' in ele:
            contigs_pcadapt_csv = ele
        elif 'LFMM' in ele:
            contigs_lfmm_csv = ele

# if config['WORKFLOW']['INTERSECT']
if "stats_outliers" in snakemake.input.keys():
    for ele in list(snakemake.input["stats_outliers"]): 
        if 'PCADAPT' in ele:
            stats_outliers_pcadapt = ele
        elif 'LFMM' in ele:
            stats_outliers_lfmm = ele

if "stats_contigs" in snakemake.input.keys():
    for ele in list(snakemake.input["stats_contigs"]): 
        if 'PCADAPT' in ele:
            stats_contigs_pcadapt = ele
        elif 'LFMM' in ele:
            stats_contigs_lfmm = ele


# variables from params
kmer_module_file_list = list(snakemake.params.list_log_kmer_per_sample)
rep_table2bed = snakemake.params.kmer_table_rep
plots_pcadapt = Path(snakemake.params.plots_pcadapt)
plots_lfmm = Path(snakemake.params.plots_lfmm)
plots_snmf = Path(snakemake.params.plots_snmf)
phenotype_pca_html = Path(snakemake.params.phenotype_pca_html)
contig_size = snakemake.params.contig_size
fastq_stats = snakemake.params.fastq_stats

# chemin absolu du dossier des plots
# chemin relatif
plots_snmf_path = plots_snmf.relative_to(Path(dir_jupyter).resolve().parent.parent)
plots_lfmm_path = plots_lfmm.relative_to(Path(dir_jupyter).resolve().parent.parent)
plots_pcadapt_path = plots_pcadapt.relative_to(Path(dir_jupyter).resolve().parent.parent)
phenotype_pca_html_path = phenotype_pca_html.relative_to(Path(dir_jupyter).resolve().parent.parent)


#########################################################################
##                             READS INFO                              ##
#########################################################################
texte = f"""\

# Reads Info
"""

code = f"""\
import pandas as pd

file = "{fastq_stats}"
data = pd.read_csv(file, delimiter="\\t")
data.style.format(thousands=" ", precision=2)
"""

nb['cells'].append(nbf.v4.new_markdown_cell(texte))
nb['cells'].append(nbf.v4.new_code_cell(code))


reads_ipynb = f"{dir_jupyter}/reads.ipynb"
with open(reads_ipynb, 'w') as f:
    nbf.write(nb, f)
nb = nbf.v4.new_notebook()

#########################################################################
##                             KMERS INFO                              ##
#########################################################################
texte = f"""\

# Kmers Info
"""

code = f"""\
from pathlib import Path, PurePosixPath
import pandas as pd
pd.set_option("display.precision", 2)

file_list = {kmer_module_file_list}
output_file = "{csv}"

data = {{}}
for file in file_list:
    file = Path(file).resolve()
    name = PurePosixPath(file).stem.split('_KMERS_MODULE')[0]
    dir = PurePosixPath(file).parent
    with open (file, 'r') as f:
        liste = []
        for line in f:
            #if "Total no. of reads" in line : 
            #    reads = int(line.strip().split(":")[1])
            #    liste.append(reads)
            if "Canonized kmers:" in line : 
                canonized = int(line.strip().split("\\t")[1])
                liste.append(canonized)
            if "Non-canon kmers:" in line : 
                non_canonized = int(line.strip().split("\\t")[1])
                liste.append(non_canonized)
            if "Non-canon kmers found:" in line : 
                non_canonized_founded = int(line.strip().split("\\t")[1])
                liste.append(non_canonized_founded)
            if "kmers to save:" in line : 
                tosave = int(line.strip().split(":")[1])
                liste.append(tosave)               
    data[name] = liste    
df_kmer_module = pd.DataFrame.from_dict(data, orient='index', columns=['Canonized', 'Non-canonized', 'Non-canonized_found','kmers_saved'])
df_kmer_module.to_csv(output_file)
df_kmer_module.style.format(thousands=" ", precision=2)

"""

nb['cells'].append(nbf.v4.new_markdown_cell(texte))
nb['cells'].append(nbf.v4.new_code_cell(code))

### kmers_table


texte = f"""\

## Kmers table 

iKISS uses [kmersGWAS](https://github.com/voichek/kmersGWAS) tool to generate a binary table of kmers. 

This absence/presence table is split in several ones. 

Here you can see how many kmers are in each bim file. 

"""

code = f"""\
from pathlib import Path, PurePosixPath
import pandas as pd
import subprocess

bims = []
nb_lines = []

source = Path("{rep_table2bed}")
for x in source.iterdir():
    if x.name.endswith('.bim'):
        file = f"{rep_table2bed}/{{x.name}}"
        command = ["wc", "-l", file]
        process = subprocess.Popen(command, stdout=subprocess.PIPE)
        data = process.communicate()
        lines = int(str(data[0]).strip().split(' ')[0].removeprefix('b').removeprefix("\'"))
        bims.append(x.name)
        nb_lines.append(lines)
        df = pd.DataFrame(list(zip(bims, nb_lines)), columns =['bim_name', 'nb_kmers'])
total_kmers = df['nb_kmers'].sum()    

print (f'The total number of kmers obtained is {{total_kmers:,}}')

df.style.format(thousands=" ", precision=2)
"""


nb['cells'].append(nbf.v4.new_markdown_cell(texte))
nb['cells'].append(nbf.v4.new_code_cell(code))


kmers_info_ipynb = f"{dir_jupyter}/kmers_info.ipynb"
with open(kmers_info_ipynb, 'w') as f:
    nbf.write(nb, f)
nb = nbf.v4.new_notebook()




#########################################################################
##                             SNMF                                 ##
#########################################################################
if "SNMF" in snakemake.params.workflow_steps:
    texte_snmf = f"""\
# SNMF

iKISS uses [snmf](http://membres-timc.imag.fr/Olivier.Francois/LEA/files/LEA_snmf.html) analyze population genetic structure using directly variation from reads.

"""
    texte_plot_snmf = f"""\
### Plots

Explore the [6.SNMF]("../../../../../../{plots_snmf_path}) directory and check structure of your samples.

If you want to improve SNMF plots, iKISS propose you a quarto [snmf notebook](https://forge.ird.fr/diade/iKISS/-/tree/master/ikiss/notebooks?ref_type=heads)

Follow the documentation using the snmf object created by iKISS with the `load.snmfProject` LEA R function and observe the structure of your populations using directly variations found in the reads (k-mers) 
[LEA SNMF doc](http://membres-timc.imag.fr/Olivier.Francois/LEA/files/LEA_snmf.html)

    """
    nb['cells'].append(nbf.v4.new_markdown_cell(texte_snmf))
    #nb['cells'].append(nbf.v4.new_code_cell(texte_plot_snmf))
    nb['cells'].append(nbf.v4.new_markdown_cell(texte_plot_snmf))

    # writing snmf results into an ipynb
    snmf_ipynb = f"{dir_jupyter}/snmf.ipynb"
    with open(snmf_ipynb, 'w') as f:
        nbf.write(nb, f)
    nb = nbf.v4.new_notebook()
    options.append("    - snmf.qmd")




#########################################################################
##                             PCADAPT                                 ##
#########################################################################

if "PCADAPT" in snakemake.params.workflow_steps:

    texte_pcadapt = f"""\
# PCADAPT

iKISS uses [pcadapt](https://cran.r-project.org/web/packages/pcadapt/index.html) tool to detect significant kmers under selection.

Kmers under selection detected by pcadapt are summary here.

"""
    code_pcadapt = f"""\
from pathlib import Path, PurePosixPath
import pandas as pd
import subprocess

file = []
nb_lines = []
source = Path("{outliers_pcadapt}")
file_name = source.stem
command = ["wc", "-l", source]
process = subprocess.Popen(command, stdout=subprocess.PIPE)
data = process.communicate()
lines = int(str(data[0]).strip().split(' ')[0].removeprefix('b').removeprefix("\'"))
file.append(file_name)
nb_lines.append(lines)
df = pd.DataFrame(list(zip(file, nb_lines)), columns =['file', 'nb_kmers'])
df.style.format(thousands=" ", precision=2)
"""

    texte_pcadapt_bis = f"""\

### Plots 
Explore the [6.PCADAPT]("../../../../../../{plots_pcadapt_path}) directory and check projection onto PC1 and PC2, Manhattan Plot, Q-Q plot and also statistical distribution of pvalues.
    """



    ##################################### OUTLIERS PCADAPT  ######################################

    texte_pcadapt_position = f"""\

## outliers and mapping 
Some statistics about direct mapping of kmers versus {snakemake.params["ref"]}.
    """

    code_pcadapt_position = f"""
from pathlib import Path, PurePosixPath
import pandas as pd
file = Path("{stats_pcadapt}")
file = Path(file).resolve()
name = 'KMERS_AND_POSITIONS'
stats_df = pd.read_json(file)
stats_df.columns = ['INFO']
stats_df.iloc[1].apply(int)
stats_df.style.format(thousands=" ", precision=2)
"""

    ##################################### INTERSECT OUTLIERS PCADAPT  ######################################

    texte_pcadapt_intersect_outliers = f"""\

### Outliers and annotation 

Kmers detected by PCADAPT were mapped and intersected with an annotated reference.  

    """

    code_pcadapt_intersect_outliers = f"""
from pathlib import Path, PurePosixPath
import pandas as pd
import subprocess

file = []
nb_lines = []
source = Path("{stats_outliers_pcadapt}")
file_name = source.stem
command = ["wc", "-l", source]
process = subprocess.Popen(command, stdout=subprocess.PIPE)
data = process.communicate()
lines = int(str(data[0]).strip().split(' ')[0].removeprefix('b').removeprefix("\'"))
file.append(file_name)
nb_lines.append(lines)
df = pd.DataFrame(list(zip(file, nb_lines)), columns =['file', 'nb_features'])
df.style.format(thousands=" ", precision=2)
"""

    ##################################### ASSEMBLY PCADAPT  ######################################

    texte_pcadapt_assembly = f"""\

## Assembly kmers under selection 

Distribution of contigs assembled using kmers under selection detected by PCADAPT in {contigs_pcadapt_csv}.
"""

    code_pcadapt_assembly = f"""

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

df = pd.read_csv("{contigs_pcadapt_csv}", delimiter='\\t')
len(df)

df['len_contig']=df['contig'].apply(len)
df[df['len_contig'] >= {contig_size}]
nb_contigs_user = len(df[df['len_contig'] >= {contig_size}])
print (f'nb contigs selected by contig_size parametter given by user : {{nb_contigs_user}}')

for i in range(0, max(df["len_contig"]), 100):
    start=int(i)
    stop=int(start+100)
    cmd=(len(df[(df["len_contig"]>start) & (df["len_contig"]<stop)]))
    print(f"interval {{start}}-{{stop}}\\t{{cmd}}")

# setting the dimensions of the plot
ax = plt.subplots(figsize=(15, 6))
df2=(df[(df["len_contig"]>0) & (df["len_contig"]<(max(df["len_contig"])+100))])
sns.histplot(data=df2, x="len_contig", log_scale=False, bins=100, stat="count")

# setting the dimensions of the plot
ax = plt.subplots(figsize=(15, 6))
df2=(df[(df["len_contig"]>{contig_size}) & (df["len_contig"]<(max(df["len_contig"])+100))])
sns.histplot(data=df2, x="len_contig", log_scale=False, bins=20, stat="count") 
"""

    ##################################### INTERSECT CONTIGS PCADAPT  ######################################

    texte_pcadapt_intersect = f"""\

### Contigs and annotation


    """
    code_texte_pcadapt_intersect = f"""\
from pathlib import Path, PurePosixPath
import pandas as pd
import subprocess

file = []
nb_lines = []
source = Path("{stats_contigs_pcadapt}")
file_name = source.stem
command = ["wc", "-l", source]
process = subprocess.Popen(command, stdout=subprocess.PIPE)
data = process.communicate()
lines = int(str(data[0]).strip().split(' ')[0].removeprefix('b').removeprefix("\'"))
file.append(file_name)
nb_lines.append(lines)
df = pd.DataFrame(list(zip(file, nb_lines)), columns =['file', 'nb_features'])
df.style.format(thousands=" ", precision=2)
    """

    nb['cells'].append(nbf.v4.new_markdown_cell(texte_pcadapt))
    nb['cells'].append(nbf.v4.new_code_cell(code_pcadapt))
    nb['cells'].append(nbf.v4.new_markdown_cell(texte_pcadapt_bis))
    if "MAPPING_KMERS" in snakemake.params.workflow_steps:
        nb['cells'].append(nbf.v4.new_markdown_cell(texte_pcadapt_position))
        nb['cells'].append(nbf.v4.new_code_cell(code_pcadapt_position))
        if "INTERSECT" in snakemake.params.workflow_steps:
        #if "stats_outliers" in snakemake.input.keys():
            nb['cells'].append(nbf.v4.new_markdown_cell(texte_pcadapt_intersect_outliers))
            nb['cells'].append(nbf.v4.new_code_cell(code_pcadapt_intersect_outliers))
    if "ASSEMBLY_KMERS" in snakemake.params.workflow_steps:
        nb['cells'].append(nbf.v4.new_markdown_cell(texte_pcadapt_assembly))
        nb['cells'].append(nbf.v4.new_code_cell(code_pcadapt_assembly))
        if "INTERSECT" in snakemake.params.workflow_steps:
        #if "stats_contigs" in snakemake.input.keys():
            nb['cells'].append(nbf.v4.new_markdown_cell(texte_pcadapt_intersect))
            nb['cells'].append(nbf.v4.new_code_cell(code_texte_pcadapt_intersect))

    # writing pcadapt results into an ipynb
    pcadapt_ipynb = f"{dir_jupyter}/pcadapt.ipynb"
    with open(pcadapt_ipynb, 'w') as f:
        nbf.write(nb, f)
    nb = nbf.v4.new_notebook()

    #options="    - pcadapt.qmd"
    options.append("    - pcadapt.qmd")





#########################################################################
##                             LFMM                                    ##
#########################################################################

if "LFMM" in snakemake.params.workflow_steps:
    # selected,db, with mapping stats . LOGS/11.OUTLIERS_LFMM_POSITION/OUTLIERS_POSITION.e
    texte_lfmm = f"""\
# LFMM 

iKISS uses [lfmm](https://cran.r-project.org/web/packages/pcadapt/index.html) tool to detect significant kmers associated with a phenotype.

Number of kmers under selection detected by lfmm are summary here.

    """
    code_lfmm = f"""\
from pathlib import Path, PurePosixPath
import pandas as pd
import subprocess

file = []
nb_lines = []
source = Path("{outliers_lfmm}")
file_name = source.stem
command = ["wc", "-l", source]
process = subprocess.Popen(command, stdout=subprocess.PIPE)
data = process.communicate()
lines = int(str(data[0]).strip().split(' ')[0].removeprefix('b').removeprefix("\'"))
file.append(file_name)
nb_lines.append(lines)
df = pd.DataFrame(list(zip(file, nb_lines)), columns =['file', 'nb_kmers'])
df.style.format(thousands=" ", precision=2)
    """

    texte_lfmm_bis = f"""\
### Plots 

Explore the [6.LFMM]("../../../../../../{plots_lfmm_path}) directory and check Manhattan Plot and Q-Q plot.

    """

    ##################################### PHENOTYPE ANALYSYS LFMM  ###############################

    texte_lfmm_phenotype_pca = f"""\

### Phenotype PCA 

PCA complexity reduction was done in phenotype data in the iKISS package. 

Steps are described the [html phenotype report]("../../../../../../{phenotype_pca_html_path}) in the REPORT directory.
"""

    ##################################### OUTLIERS LFMM  ######################################

    texte_lfmm_position = f"""\

## Outliers and mapping

Some statistics about direct mapping of kmers versus {snakemake.params.ref}.
    """

    code_lfmm_position = f"""
from pathlib import Path, PurePosixPath
import pandas as pd
file = Path("{stats_lfmm}")
file = Path(file).resolve()
name = 'KMERS_AND_POSITIONS'
stats_df = pd.read_json(file)
stats_df.columns = ['INFO']
stats_df.style.format(thousands=" ", precision=2)
    """

    ##################################### INTERSECT OUTLIERS LFMM  ######################################

    texte_lfmm_intersect_outliers = f"""\

### Outliers and annotation 

Kmers detected by LFMM were mapped and intersected with the annotation.

    """

    code_lfmm_intersect_outliers = f"""
from pathlib import Path, PurePosixPath
import pandas as pd
import subprocess

file = []
nb_lines = []
source = Path("{stats_outliers_lfmm}")
file_name = source.stem
command = ["wc", "-l", source]
process = subprocess.Popen(command, stdout=subprocess.PIPE)
data = process.communicate()
lines = int(str(data[0]).strip().split(' ')[0].removeprefix('b').removeprefix("\'"))
file.append(file_name)
nb_lines.append(lines)
df = pd.DataFrame(list(zip(file, nb_lines)), columns =['file', 'nb_features'])
df.style.format(thousands=" ", precision=2)
"""

    ################################# ASSEMBLY LFMM ########################################
    texte_lfmm_assembly = f"""\

## Assembly kmers lfmm 

Distribution of contigs assembled using significant kmers detected by LFMM in {contigs_lfmm_csv} file.
"""

    code_lfmm_assembly = f"""

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


df = pd.read_csv("{contigs_lfmm_csv}", delimiter='\\t')
len(df)

df['len_contig']=df['contig'].apply(len)
df[df['len_contig'] >= {contig_size}]
nb_contigs_user = len(df[df['len_contig'] >= {contig_size}])
print (f'nb contigs selected by contig_size parametter given by user : {{nb_contigs_user}}')

for i in range(0, max(df["len_contig"]), 100):
    start=int(i)
    stop=int(start+100)
    cmd=(len(df[(df["len_contig"]>start) & (df["len_contig"]<stop)]))
    print(f"interval {{start}}-{{stop}}\\t{{cmd}}")

# setting the dimensions of the plot
ax = plt.subplots(figsize=(15, 6))
df2=(df[(df["len_contig"]>0) & (df["len_contig"]<(max(df["len_contig"])+100))])
sns.histplot(data=df2, x="len_contig", log_scale=False, bins=100, stat="count")

# setting the dimensions of the plot
ax = plt.subplots(figsize=(15, 6))
df2=(df[(df["len_contig"]>{contig_size}) & (df["len_contig"]<(max(df["len_contig"])+100))])
sns.histplot(data=df2, x="len_contig", log_scale=False, bins=20, stat="count") """

    ##################################### INTERSECT CONTIGS LFMM  ######################################

    texte_lfmm_intersect = f"""\

### Contigs and annotation


    """
    code_texte_lfmm_intersect = f"""\
from pathlib import Path, PurePosixPath
import pandas as pd
import subprocess

file = []
nb_lines = []
source = Path("{stats_contigs_lfmm}")
file_name = source.stem
command = ["wc", "-l", source]
process = subprocess.Popen(command, stdout=subprocess.PIPE)
data = process.communicate()
lines = int(str(data[0]).strip().split(' ')[0].removeprefix('b').removeprefix("\'"))
file.append(file_name)
nb_lines.append(lines)
df = pd.DataFrame(list(zip(file, nb_lines)), columns =['file', 'nb_kmers'])
df.style.format(thousands=" ", precision=2)
    """

    nb['cells'].append(nbf.v4.new_markdown_cell(texte_lfmm))
    nb['cells'].append(nbf.v4.new_code_cell(code_lfmm))
    if not "" in snakemake.params.phenotype:
        nb['cells'].append(nbf.v4.new_markdown_cell(texte_lfmm_phenotype_pca))
    nb['cells'].append(nbf.v4.new_markdown_cell(texte_lfmm_bis))
    if "MAPPING_KMERS" in snakemake.params.workflow_steps:
        nb['cells'].append(nbf.v4.new_markdown_cell(texte_lfmm_position))
        nb['cells'].append(nbf.v4.new_code_cell(code_lfmm_position))
        if "INTERSECT" in snakemake.input.keys():
            nb['cells'].append(nbf.v4.new_markdown_cell(texte_lfmm_intersect_outliers))
            nb['cells'].append(nbf.v4.new_code_cell(code_lfmm_intersect_outliers))
    if "ASSEMBLY_KMERS" in snakemake.params.workflow_steps:
        nb['cells'].append(nbf.v4.new_markdown_cell(texte_lfmm_assembly))
        nb['cells'].append(nbf.v4.new_code_cell(code_lfmm_assembly))
        if "INTERSECT" in snakemake.input.keys():
            nb['cells'].append(nbf.v4.new_markdown_cell(texte_lfmm_intersect))
            nb['cells'].append(nbf.v4.new_code_cell(code_texte_lfmm_intersect))


    # writing lfmm results into an ipynb
    lfmm_ipynb = f"{dir_jupyter}/lfmm.ipynb"
    with open(lfmm_ipynb, 'w') as f:
        nbf.write(nb, f)
    nb = nbf.v4.new_notebook()

    options.append("    - lfmm.qmd")



######### QUARTO YML #############

# ADAPTING _quarto.yml
options = '\n'.join(options)
#print (options)
with open(quarto_yml, 'r') as q:
    txt = q.read()
txt = txt.replace("    OPTIONS", options)

#writing in _quarto.yml conf to Book
with open (new_quarto_yml, 'w') as out:
    out.write(txt)
