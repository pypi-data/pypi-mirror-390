import argparse
from pathlib import Path, PurePosixPath
import pandas as pd

parser = argparse.ArgumentParser()
parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
#parser.add_argument("-p", "--outliers", help="outliers from lfmm or pcadapt", type=str)
parser.add_argument("-o", "--bed", help="bed file from bedtools intersect (bam and gff intersection, )", type=str, required=True)
parser.add_argument("-m", "--mapq", help="mapq filter used in stats )", type=int)
parser.add_argument("-n", "--nbinfeature", help="contigs/kmers number used in stats)", type=int)

args = parser.parse_args()

if args.mapq!=None:
    mapq = args.mapq
else :
    mapq = 10

if args.nbinfeature!=None:
    nbinfeature = int(args.nbinfeature)
else :
    nbinfeature = 2

# 1. Les kmers/contigs mappés sur le pangenome
bed = args.bed
bed = Path(bed).resolve()
name_bed = PurePosixPath(bed).stem
dir_bed = PurePosixPath(bed).parent
element = "feature"


def stats_from_intersect_element_and_ref (df, direc, element, nbinfeature):
    # on compte combien des kmers par gene sur c/contig
    gp = df.groupby('contig_bam')['ID_gene'].value_counts().reset_index(name='counts')
    # combien des kmers par contig (plus light)
    gp.groupby('contig_bam')['counts'].sum()
    gp.to_csv(f"{direc}/nb_{element}_by_gene.csv",index=False)
    # on garde les genes qui ont au moins 10 kmers
    gp10 = gp.query("counts >= @nbinfeature")
    gp10.to_csv(f"{direc}/nb_{element}_by_gene_filter.csv",index=False)
    # combien de kmers par chromosome
    nb_km_by_chr = gp10.groupby('contig_bam')['counts'].sum()
    nb_km_by_chr.to_csv(f"{direc}/nb_{element}_by_chr.csv",index=True)
    # combien de genes dans c/chr
    nb_gn_by_chr = gp10.groupby('contig_bam')['ID_gene'].count()
    nb_gn_by_chr.to_csv(f"{direc}/nb_{element}_by_chr.csv",index=True)


df_intersection = pd.read_csv(bed, delimiter='\t', header=None)
len(df_intersection)
df_intersection.columns
df_intersection.drop([6, 7, 8, 9, 10, 11, 13, 17, 18, 19], axis = 1, inplace=True)
df_intersection.head()
df_intersection.rename(columns={0: "contig_bam", 1: "start", 2: "stop", 3: "name", 4: "MAPQ", 5: "brin",
                                12: "contig_gff", 14: "feature", 15: "start_gene", 16: "stop_gene", 20: "gene_info"}, inplace=True)
new_df_intersection = df_intersection.gene_info.str.split(";",expand=True)
df = pd.concat([df_intersection, new_df_intersection[[0,1,2,3]] ], axis=1)
df.rename(columns={0: "ID_gene", 1: "Name_gene", 2: "Biotype_gene", 3: "Note_gene"}, inplace=True)

# filtering by MAPQ15
df15 = df.query(f"MAPQ > {mapq}")
df15.groupby(['contig_bam']).count()

# stats
stats_from_intersect_element_and_ref(df15, "intersect_stats", element, nbinfeature)

def histo_nb_genes_by_chr (nb_kmers_pan_df):
    import pandas as pd
    import seaborn as sns
    nb_kmers_pan = nb_kmers_pan_df[~nb_kmers_pan_df["contig_bam"].str.contains("Chr")]['ID_gene'].sum()
    nb_kmers_un = nb_kmers_pan_df[nb_kmers_pan_df["contig_bam"].str.contains("ChrU")]['ID_gene'].sum()
    df = nb_kmers_pan_df[nb_kmers_pan_df["contig_bam"].str.contains("^Chr[0-9]+")]
    df2 = pd.DataFrame({"contig_bam":["PAN"],
                        "ID_gene":[nb_kmers_pan]})
    df3 = pd.DataFrame({"contig_bam":["UNKNOWN"],
                        "ID_gene":[nb_kmers_un]})
    pd.concat([df, df3, df2], ignore_index=True)
    print (pd.concat([df, df3, df2], ignore_index=True))

    # TODO: plot in report
    sns.histplot (pd.concat([df, df3, df2]), x="contig_bam",y="ID_gene")
    #ignore_index=True
    #fig.show()

# only for rice
#nb_kmers_pan_df = pd.read_csv("outliers_kmers/nb_gene_by_chr.csv", delimiter=',')
#histo_nb_genes_by_chr(nb_kmers_pan_df)

