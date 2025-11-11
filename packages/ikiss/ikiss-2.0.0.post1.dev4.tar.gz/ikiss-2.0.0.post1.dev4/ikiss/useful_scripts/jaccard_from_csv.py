#!/usr/bin/env python
# coding: utf-8
# Auteur: Julie Orjuela IRD DIADE
# Description: Ce script calcule la similarité de Jaccard moyenne des kmers (fichier d'entrée) et utilise un fichier passeport pour recuperer les infos des populations (Fonio).

import numpy as np
import pandas as pd
import argparse
from sklearn.metrics import pairwise_distances
from joblib import Parallel, delayed

# Configuration de l'argument parser
parser = argparse.ArgumentParser(
    description=(
        "Ce script calcule la similarité moyenne de Jaccard à partir d'un fichier d'entrée.\n\n"
        "Le fichier d'entrée doit être un fichier tabulé (.txt ou .tsv) sans en-tête, où chaque ligne\n"
        "représente une observation et chaque colonne une variable binaire (0 ou 1)."
    ),
)
    
parser.add_argument(
    "input_file", 
    type=str, 
    help="Chemin vers le fichier d'entrée (ex. : 'large_file.txt').\n"
         "Le fichier doit être au format TSV (colonnes séparées par des tabulations)."
)

parser.add_argument(
    "--chunk_size",
    type=int,
    default=1000,
    help="Nombre de lignes par chunk pour la parallélisation (par défaut : 1000)."
)

parser.add_argument(
    "--n_jobs",
    type=int,
    default=-1,
    help="Nombre de processus à utiliser pour la parallélisation (-1 pour tous les cœurs disponibles)."
)


parser.add_argument(
    "--passport",
    type=str,
    default=-1,
    help="Chemin vers le fichier passport pour recuperer les infos des populations"
)

# Lecture des arguments
args = parser.parse_args()
input_file = args.input_file
chunk_size = args.chunk_size
passeport = args.passport
n_jobs = args.n_jobs
output_file = f"results_jaccard_{input_file}"


# Fonction pour calculer la similarité de Jaccard pour un chunk
def compute_chunk_similarity(chunk, full_data):
    return 1 - pairwise_distances(chunk, full_data, metric='jaccard')

# Fonction pour calculer la moyenne par pop
def calculate_mean_in_a_pop(df_np):
    # Découpage en chunks
    num_rows = df_np.shape[0]
    chunks = [df_np[i:i + chunk_size] for i in range(0, num_rows, chunk_size)]

    # Calcul parallèle des similarités
    results = Parallel(n_jobs=n_jobs)(
        delayed(compute_chunk_similarity)(chunk, df_np) for chunk in chunks)

    # Moyenne globale des similarités (sans charger toute la matrice en mémoire)
    total_similarity = 0
    num_comparisons = 0
    list_moy = []
    for indx, chunk_sim in enumerate(results):
        total_similarity += np.sum(chunk_sim)
        num_comparisons += chunk_sim.size
        average_similarity_per_chunk = np.sum(chunk_sim) / chunk_sim.size
        #print(indx, average_similarity_per_chunk)
        list_moy.append(average_similarity_per_chunk)

    #average_similarity = total_similarity / num_comparisons
    #return (average_similarity)
    return(list_moy)

# Lecture du fichier de passeport
pass_df= pd.read_csv(passeport, sep=' ')
## modification des noms de samples pour qu'elle soient les memes traités par ikiss
pass_df['ID'] = pass_df['ID'].str.replace('_','')
pass_df['ID'] = pass_df['ID'].str.replace('-','')
pass_df['ID'] = pass_df['ID'].str.replace('NER2011','NER')
pass_df['ID'] = pass_df['ID'].str.replace('MNHNPP','PP')
## nouvelle dataframe pour recuperer les ind par espece 
grouped = pass_df.groupby(['species'])

# Lecture du fichier d'entrée dans un DataFrame pandas
df= pd.read_csv(input_file, sep='\t', engine='c', index_col='kmer')

with open(output_file, "w") as fd:
    fd.write(f"input_file\tKmers_nb\tPop\tSize_pop\tJaccard_Average_Disimilarity\n")
    for name, group in grouped:
        pop = group["ID"].tolist()
        df_np = df[pop].to_numpy()
        list_average_similarity = calculate_mean_in_a_pop(df_np)
        for moy in list_average_similarity :
            print(f"{input_file}\t{len(df)}\t{name[0]}\t{len(group['ID'].tolist())}\t{moy}")
            fd.write(f"{input_file}\t{len(df)}\t{name[0]}\t{len(group['ID'].tolist())}\t{moy}\n")