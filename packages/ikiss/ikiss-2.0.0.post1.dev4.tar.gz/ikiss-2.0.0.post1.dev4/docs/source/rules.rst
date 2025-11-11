Rules
------

Here you can quickly find iKISS snakemake rules list :

.. code-block:: bash

   rule kmers_gwas_per_sample *
   rule kmers_to_use
   rule kmers_table
   rule extract_kmers_from_bed
   rule index_ref
   rule index_ref_to_assembly
   rule mapping_kmers
   rule filter_bam
   rule kmer_position_from_bam *
   rule merge_kmer_position
   rule samtools_merge
   rule pcadapt *
   rule merge_method
   rule outliers_position
   rule extracting_features_from_gff
   rule kmers_bedtools_intersect
   rule get_pca_from_phenotype
   rule lfmm *
   rule mergetags
   rule mapping_contigs
   rule contigs_bedtools_intersect
   rule intersect_and_contigs
   rule intersect_and_outliers
   rule aggregate_presence_absence_matrix
   rule filter_presence_absence_matrix
   rule merging_annotations_and_binary_matrix
   rule fastq_stats
   rule report_ikiss
   rule html_ikiss

* rules with a `*` can be parallelized.