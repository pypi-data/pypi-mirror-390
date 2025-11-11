#!/bin/bash
#SBATCH -p bigmem
#SBATCH -c 12
#SBATCH --mem 200G

module load python/3.12

cd /shared/projects/kmexplore/thomas_kmers/SPLITTED

for file in x*.txt; do
       	echo $file; 
	time python3 jaccard_from_csv.py --chunk_size 10000 --n_jobs -1 --passport ../passport_fonio.txt $file;
done

echo "FIN ..."
