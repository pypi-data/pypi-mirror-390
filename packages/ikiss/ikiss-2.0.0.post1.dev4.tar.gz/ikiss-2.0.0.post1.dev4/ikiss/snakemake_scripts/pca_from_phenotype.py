import nbformat as nbf
import argparse
from pathlib import Path, PurePosixPath


nb = nbf.v4.new_notebook()
nb['cells'] = []

parser = argparse.ArgumentParser()
parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
parser.add_argument("-p", "--phenotype_file", help="phenotype file with variables continuos", type=str)
parser.add_argument("-o", "--output_file", help="output file", type=str)

args = parser.parse_args()
pheno = args.phenotype_file
pheno = Path(pheno).resolve()
name_pheno = PurePosixPath(pheno).stem
dir_pheno = PurePosixPath(pheno).parent

jupyter = args.output_file
jupyter = f"{Path(jupyter).resolve()}"
name_jupyter = PurePosixPath(jupyter).stem
dir_jupyter = PurePosixPath(jupyter).parent
csv = f"{dir_jupyter}/{name_jupyter}.csv"

texte = f"""\
# PCA from phenotype 
This is an auto-generated jupyter notebook from iKISS package. """
code = f"""\
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.backends.backend_pdf import PdfPages
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA"""

nb['cells'].append(nbf.v4.new_markdown_cell(texte))
nb['cells'].append(nbf.v4.new_code_cell(code))

texte = f"""\
Variables declaration """

code = f"""\
pheno = "{pheno}"
name_pheno = "{name_pheno}"
dir_pheno = "{dir_pheno}" """
nb['cells'].append(nbf.v4.new_markdown_cell(texte))
nb['cells'].append(nbf.v4.new_code_cell(code))

texte = f"""\
Phenotype file loading by pandas """
code = f"""\
df = pd.read_csv(pheno, delimiter='\\t', header=0, decimal=",")
df.head() """
nb['cells'].append(nbf.v4.new_markdown_cell(texte))
nb['cells'].append(nbf.v4.new_code_cell(code))

texte = f"""\
# show features with count of NaN values

NaN by variable in the phenotype file """
code = f"""\
s = df.isnull().sum()
s = s.sort_values(ascending=False)
s = s[s > 0] 
s """
nb['cells'].append(nbf.v4.new_markdown_cell(texte))
nb['cells'].append(nbf.v4.new_code_cell(code))

texte = f"""\
Dropping NaN """
code = f"""\
df = df.dropna()
df.shape """
nb['cells'].append(nbf.v4.new_markdown_cell(texte))
nb['cells'].append(nbf.v4.new_code_cell(code))

texte = f"""\
## Pearson correlation

headmap """
code = f"""\
font1 = fm.FontProperties(size=20)
font2 = fm.FontProperties(size=24)
fig1 = plt.figure(figsize=(24, 24))
plt.title('Correlation Pearson des variables', y=1.05, size=18)
sns.heatmap(df.iloc[:, 2:].corr(), linewidths=0.3, vmax=1.0, square=True, cmap='coolwarm', linecolor='white', annot=True)"""
nb['cells'].append(nbf.v4.new_markdown_cell(texte))
nb['cells'].append(nbf.v4.new_code_cell(code))

texte = f"""\
## Pearson correlation

pairplot"""
code = f"""\
fig2 = sns.pairplot(data=df)
plt.style.use('ggplot') """

nb['cells'].append(nbf.v4.new_markdown_cell(texte))
nb['cells'].append(nbf.v4.new_code_cell(code))


texte = f"""\
## PCA using given variable in phenotype.txt file

We remove first and second colon """
code = f"""\
X = df.drop(['accession_id','group'], axis=1)
print(X.head())"""
nb['cells'].append(nbf.v4.new_markdown_cell(texte))
nb['cells'].append(nbf.v4.new_code_cell(code))


texte = f"""\
## Z-score the feature (optional) """
code = f"""\
modelStd = StandardScaler()
modelStd.fit(X)
x = modelStd.transform(X)
# x sont les zscores transformés
x"""
nb['cells'].append(nbf.v4.new_markdown_cell(texte))
nb['cells'].append(nbf.v4.new_code_cell(code))

texte = f"""\
### Fit PCA with the whole of dimensions"""
code = f"""\
pca = PCA()
model = pca.fit(x)"""
nb['cells'].append(nbf.v4.new_markdown_cell(texte))
nb['cells'].append(nbf.v4.new_code_cell(code))



texte = f"""\
### variance in each axe of PCA"""
code = f"""\
pca.explained_variance_ratio_.shape[0]"""
nb['cells'].append(nbf.v4.new_markdown_cell(texte))
nb['cells'].append(nbf.v4.new_code_cell(code))

texte = f"""\
### cumulated PCA variance """
code = f"""\
pca.explained_variance_ratio_.cumsum()*100"""
nb['cells'].append(nbf.v4.new_markdown_cell(texte))
nb['cells'].append(nbf.v4.new_code_cell(code))

texte = f"""\
Cumulated variance plot"""
code = f"""\
fig3 = plt.figure(figsize=(8, 6))
plt.plot(pca.explained_variance_ratio_.cumsum())"""
nb['cells'].append(nbf.v4.new_markdown_cell(texte))
nb['cells'].append(nbf.v4.new_code_cell(code))

texte = f"""\
Calculate automatically components"""
code = f"""\
n_components = sum(pca.explained_variance_ratio_.cumsum() < .95 ) + 1
print(f"more of 95% of the variance is explained by {{n_components}} components")"""
nb['cells'].append(nbf.v4.new_markdown_cell(texte))
nb['cells'].append(nbf.v4.new_code_cell(code))

texte = f"""\
# plotting inertia in each axe
"""
code = f"""\
font1 = fm.FontProperties(size=12)
inertie = pd.DataFrame(pca.explained_variance_ratio_, columns=['Inertie'])
inertie['label'] = np.round(pca.explained_variance_ratio_.cumsum() * 100, 2)
inertie['Dimension'] = range(0, pca.explained_variance_ratio_.shape[0])
ndim = 8
fig4 = plt.figure(figsize=(6,4),dpi=120)

sns.set_style("whitegrid")
g = sns.barplot(x="Dimension", y='Inertie',
                data=inertie.iloc[:ndim, :],
                palette="Blues_d")
for index, row in inertie.iloc[:ndim, :].iterrows():
    g.text(row.name, row.Inertie,
           row.label,
           color='black', ha="center",
           rotation=30,
           fontproperties=font1)
plt.xlabel('Dimension', fontproperties=font1)
plt.ylabel('Inertie', fontproperties=font1)
#plt.show()
plt.style.use('ggplot') """
nb['cells'].append(nbf.v4.new_markdown_cell(texte))
nb['cells'].append(nbf.v4.new_code_cell(code))

texte = f"""\
# PCA with n_components """
code = f"""\
modelPCA = PCA(n_components=n_components)
modelPCA.fit(x)
## transform of x (matrice de zscores)
df2 = pd.DataFrame(data=modelPCA.transform(x), columns=[f'Dim{{str(x+1)}}' for x in range(0, n_components)]) 
# we include colonne accesion_id and groups columns
df1 = pd.DataFrame(data=df['accession_id'])
df1['group'] = df['group'].values
dfPCA = pd.concat([df1, df2], axis = 1) 
dfPCA.head()"""
nb['cells'].append(nbf.v4.new_markdown_cell(texte))
nb['cells'].append(nbf.v4.new_code_cell(code))


texte = f"""\
Saving csv file with PCA dimensions obtained by sample (id and group columns are added)"""
code = f"""\
dfPCA.to_csv("{csv}", index=False, sep = '\\t', header=True)"""
nb['cells'].append(nbf.v4.new_markdown_cell(texte))
nb['cells'].append(nbf.v4.new_code_cell(code))

texte = f"""\
# pearson correlation plot from ACP variables"""
code = f"""\
fig5 = plt.figure(figsize=(8,8))
sns.set(font_scale=2.5)
plt.title('Correlation Pearson des variables', y=1.05, size=18)
sns.heatmap(dfPCA.iloc[:,2:].corr(),linewidths=0.3,vmax=1.0, fmt='.3f',
            square=True, cmap='coolwarm', linecolor='white', annot=True)
sns.set(font_scale=1)
plt.style.use('ggplot')
"""
nb['cells'].append(nbf.v4.new_markdown_cell(texte))
nb['cells'].append(nbf.v4.new_code_cell(code))

texte = f"""\
# PCA representation """
code = f"""\
sns.set(font_scale=2)
font1 = fm.FontProperties(size=16)
font2 = fm.FontProperties(size=32)

fig6 = plt.figure(figsize=(24, 24))
ax = sns.lmplot(x='Dim1',y='Dim2', hue='group', data=dfPCA,
                fit_reg=False, height=12, aspect=2 )
plt.title('PCA from phenotype file in iKISS ', fontproperties=font2)
plt.xlabel('Dimension 1', fontproperties=font1)
plt.ylabel('Dimension 2', fontproperties=font1)
def label_point(x, y, val, ax):
    a = pd.concat({{'x': x, 'y': y, 'val': val}}, axis=1)
    for i, point in a.iterrows():
        ax.text(point['x']+.02, point['y']+.02, str(point['val']),
                fontproperties=font1)

label_point(dfPCA.Dim1, dfPCA.Dim2, dfPCA.accession_id, plt.gca())
plt.style.use('ggplot')"""
nb['cells'].append(nbf.v4.new_markdown_cell(texte))
nb['cells'].append(nbf.v4.new_code_cell(code))


texte = f"""\
### Pearson for variables in new ACP dimensions """
code = f"""\
fig7 = plt.figure(figsize=(52, 52))
sns.set(font_scale=2.5)
plt.title("L'influence des variables dans les nouvelles dimensions", y=1.05, size=24)
sns.heatmap(pd.DataFrame(modelPCA.components_, columns=X.columns),
            fmt='.2f', linewidths=0.3, vmax=1.0,
            square=True, cmap='coolwarm', linecolor='white', annot=True) """
nb['cells'].append(nbf.v4.new_markdown_cell(texte))
nb['cells'].append(nbf.v4.new_code_cell(code))


texte = f"""\
# Biplot """

code = f"""\
loadings = pca.components_
num_pc = pca.n_features_in_
pc_list = ["PC"+str(i) for i in list(range(1, num_pc+1))]
loadings_df = pd.DataFrame.from_dict(dict(zip(pc_list, loadings)))
#loadings_df['variable'] = df.columns.values
#loadings_df = loadings_df.set_index('variable')
loadings_df"""
nb['cells'].append(nbf.v4.new_markdown_cell(texte))
nb['cells'].append(nbf.v4.new_code_cell(code))


texte = f"""\
### plotting variable forces in PCA"""

code = f"""\
plt.rcParams.update({{'font.size': 12}})
from bioinfokit.visuz import cluster
fig8 = cluster.biplot(cscore=x, 
               loadings=loadings, 
               labels=df.columns.values, 
               var1=round(pca.explained_variance_ratio_[0]*100, 2),
               var2=round(pca.explained_variance_ratio_[1]*100, 2),
               #colordot='blue',
               arrowcolor='red',
               dim=(12,9),
               r=600,
               #theme='white',
               show=True)"""
nb['cells'].append(nbf.v4.new_markdown_cell(texte))
nb['cells'].append(nbf.v4.new_code_cell(code))

with open(jupyter, 'w') as f:
    nbf.write(nb, f)
