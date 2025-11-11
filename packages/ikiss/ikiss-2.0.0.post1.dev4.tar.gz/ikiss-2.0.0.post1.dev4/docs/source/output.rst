iKISS Output
------------

This is a overwiew of iKISS output directory:

.. code-block:: bash

   OUTPUT-KISS/
      config_corrected.yaml
      0.FASTQ_STATS
      └── fastq_stats.txt
      1.KMERS_MODULE
      ├── Clone12
      ├── Clone14
      ├── Clone16
      ├── Clone2
      ├── Clone20
      ├── Clone4
      └── Clone8
      2.KMERS_TABLE
      ├── kmers_list_paths.txt
      ├── kmers_table.names
      ├── kmers_table.table
      ├── kmers_to_use
      ├── kmers_to_use.no_pass_kmers
      ├── kmers_to_use.shareness
      ├── kmers_to_use.stats.both
      ├── kmers_to_use.stats.only_canonical
      └── kmers_to_use.stats.only_non_canonical
      3.TABLE2BED
      ├── log
      ├── output_file.0.bed
      ├── output_file.0.bim
      ├── output_file.0.fam
      ├── output_file.1.bed
      ├── output_file.1.bim
      ├── output_file.1.fam
      ├── output_file.2.bed
      ├── output_file.2.bim
      ├── output_file.2.fam
      ├── output_file.3.bed
      ├── output_file.3.bim
      ├── output_file.3.fam
      ├── output_file.4.bed
      ├── output_file.4.bim
      └── output_file.4.fam
      4.EXTRACT_FASTA
      ├── output_file.0.fasta.gz
      ├── output_file.1.fasta.gz
      ├── output_file.2.fasta.gz
      ├── output_file.3.fasta.gz
      └── output_file.4.fasta.gz
      5.RANGES
      ├── output_file.0
      ├── output_file.1
      ├── output_file.2
      ├── output_file.3
      └── output_file.4
      6.LFMM
      ├── output_file.0_10_LFMM_outliers.csv
      ├── output_file.0_10_LFMM_pvalues.csv
      ├── output_file.0_10_LFMM.rplot.pdf
      ...
      6.LFMM_PHENO
      ├── PCA_from_phenotype.csv
      ├── PCA_from_phenotype.html
      └── PCA_from_phenotype.ipynb
      6.PCADAPT
      ├── output_file.0_10_PCADAPT_outliers.csv
      ├── output_file.0_10_PCADAPT_pvalues.csv
      ├── output_file.0_10_PCADAPT.rplot.pdf
      ├── output_file.0_10_PCADAPT_scores.csv
      6.SNMF
      ├── output_file.0_5_SNMF/
      ├── output_file.0_2_SNMF/
         ├── kmer.geno
         ├── kmer.snmf/
            ├── K2
                ├── run1
                ├── run2
                ├── run3
            ├── K3
         ├── kmer.snmf.pdf
         ├── kmer.snmfProject
      ...
      7.MERGED_LFMM
      ├── merged_LFMM_outliers.csv
      └── merged_LFMM_pvalues.csv
      7.MERGED_PCADAPT
      ├── merged_PCADAPT_outliers.csv
      └── merged_PCADAPT_pvalues.csv
      8.MAPPING_KMERS
      ├── bam_files.txt
      ├── output_file.0_vs_reference.bam
      ├── output_file.0_vs_reference_FMQ.bam
      ├── output_file.0_vs_reference.sai
      ├── output_file.0_vs_reference_sorted.bam
      ├── output_file.0_vs_reference_sorted.bam.bai
      ├── output_file.0_vs_reference_sorted.bam.idxstats
      ├── output_file.0_vs_reference_sorted.bam.stats
      ...
      9.KMERPOSITION
      ├── output_file.0_vs_reference_KMERPOSITION.txt
      ├── output_file.1_vs_reference_KMERPOSITION.txt
      ├── output_file.2_vs_reference_KMERPOSITION.txt
      ├── output_file.3_vs_reference_KMERPOSITION.txt
      └── output_file.4_vs_reference_KMERPOSITION.txt
      10.MERGE_KMERPOSITION
      ├── kmer_position_merged.txt
      └── kmer_position_samtools_merge.bam
      11.OUTLIERS_LFMM_POSITION
      └── outliers_with_position.csv
      11.OUTLIERS_PCADAPT_POSITION
      └── outliers_with_position.csv
      12.ASSEMBLY_OUTLIERS_LFMM
      ├── contigs_LFMM_vs_reference.bam
      ├── contigs_LFMM_vs_reference.sorted.bam
      ├── contigs_LFMM_vs_reference.sorted.bam.bai
      ├── contigs_LFMM_vs_reference.sorted.bam.idxstats
      ├── contigs_LFMM_vs_reference.sorted.bam.stats
      ├── outliers_LFMM_mergetags.csv
      └── outliers_LFMM_mergetags.fasta
      12.ASSEMBLY_OUTLIERS_PCADAPT
      ├── contigs_PCADAPT_vs_reference.bam
      ├── contigs_PCADAPT_vs_reference.sorted.bam
      ├── contigs_PCADAPT_vs_reference.sorted.bam.bai
      ├── contigs_PCADAPT_vs_reference.sorted.bam.idxstats
      ├── contigs_PCADAPT_vs_reference.sorted.bam.stats
      ├── outliers_PCADAPT_mergetags.csv
      └── outliers_PCADAPT_mergetags.fasta
      13.GFF_FEATURES
      └── extracted.gff
      14.CONTIGS_INTERSECT_LFMM
      └── contigs_intersect_annotation.bed
      14.CONTIGS_INTERSECT_PCADAPT
      └── contigs_intersect_annotation.bed
      14.KMERS_INTERSECT
      └── kmers_bedtools_intersect_annotation.bed
      15.STATS_INTERSECT
       ├── ALLKMERS_INTERSECT
       │   └── intersect_stats
       │       ├── nb_feature_by_chr.csv
       │       ├── nb_feature_by_gene.csv
       │       └── nb_feature_by_gene_filter.csv
       ├── CONTIGS_LFMM_INTERSECT
       ├── CONTIGS_PCADAPT_INTERSECT
       ├── OUTLIERS_LFMM_INTERSECT
       └── OUTLIERS_PCADAPT_INTERSECT
     16.KMERS_IN_GENES_MATRIX
       ├── global_presence_absence_matrix.txt
       ├── kmers_into_feature.fasta
     17.MATRIX_AND_ANNOTATION
       ├── annotations_and_binary_matrix_info.csv
       ├── occurrences_by_group.csv
       └── occurrences_by_sample.csv
      REF
      ├── reference2.fasta
      ├── reference2.fasta.0123
      ├── reference2.fasta.amb
      ├── reference2.fasta.ann
      ├── reference2.fasta.bwt.2bit.64
      ├── reference2.fasta.pac
      ├── reference.fasta
      ├── reference.fasta.amb
      ├── reference.fasta.ann
      ├── reference.fasta.bwt
      ├── reference.fasta.pac
      └── reference.fasta.sa
      REPORT
      ├── iKISS_report.csv
      ├── iKISS_report.html
      ├── iKISS_report.ipynb
      ├── PCA_from_phenotype.html
      └── PCA_from_phenotype.ipynb
      BENCHMARK
      LOGS


.. note:: Note

    We recommended to remove 1.KMER_GWAS repertory after analysis.