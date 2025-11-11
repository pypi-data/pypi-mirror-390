#!/bin/bash
#SBATCH -J iKISS
#SBATCH -p normal
#SBATCH -c 12
#SBATCH --mem-per-cpu=3G
#SBATCH --nodelist=node0

module load system/python/3.7.2
module load bioinfo/kmersGWAS/0.2-beta
module load bioinfo/KMC/3.0.0
module unload system/python/2.7.10
module load bioinfo/samtools/1.9
#module load  bioinfo/bwa/0.7.12
module load bioinfo/R/4.0.2

cd /scratch/orjuela/ikiss/

time snakemake -p -s Snakefile --configfile config.yaml --latency 60000 --cores 12 --set-threads kmers_gwas_per_sample=4 mapping_kmers=10 filter_bam=2 km
er_position_from_bam=4 pcadapt=4
#--dryrun --quiet


#rule kmers_gwas_per_sample:
#rule kmers_to_use:
#rule kmers_table:
#rule extract_kmers_from_bed:
#rule index_ref:
#rule mapping_kmers:
#rule filter_bam:
#rule kmer_position_from_bam:
#rule merge_kmer_position:
#rule pcadapt:
#rule merge_pcadapt: