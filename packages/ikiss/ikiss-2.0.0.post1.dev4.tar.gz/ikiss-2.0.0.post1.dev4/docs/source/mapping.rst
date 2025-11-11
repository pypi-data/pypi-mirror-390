MAPPING_KMERS
-------------------

MAPPING_KMERS section in PARAMS can optionally be used to align kmers to a genomic reference. It could give a idea of selected regions in a genome.

.. code-block:: yaml

   PARAMS:
      MAPPING_KMERS:
         REF: "reference.fasta"
         MODE : bwa-aln
         INDEX_OPTIONS: ""
         OPTIONS : "-n 0.04"
         FILTER_FLAG : 4
         FILTER_QUAL : 10


Use a reference file in the **REF** section.

Parameter **MODE** using  *bwa-aln* or *bwa-mem2*

Set up the **INDEX_OPTIONS** according to the MODE you have chosen.

   If *bwa-mem2* leaf empty

   If *bwa-aln* "-a bwtsw" or ""

Set options according of chosen mapper in the **OPTIONS** key.

   If *bwa-mem2* default parameters -A 1 -B 4;

   If *bwa-aln* -n 0.04

Obtained bam could be filtered using **FILTER_FLAG** (-F 4 by default) and **FILTER_QUAL** (mapq>10 by defaut) params.
