ASSEMBLY_KMERS
================

ASSEMBLY_KMERS section in PARAMS can optionally be used to assembly significant kmers obtained by pcadapt or/and lfmm.

Contigs are assembled by iKISS using  mergeTags from dekupl package https://github.com/Transipedia/dekupl-mergeTags.

Chose minimal overlap size "OVERLAP_SIZE" allowed to assembly kmers.

Feel free to filter contigs by size "FILTER_CONTIG_SIZE".

Assembled contigs could be mapped activating **MAPPING_CONTIGS**. This mapping can be launch versus a **REF** reference file using bwa-mem2 by default.
Reference file used in this step can be a different reference from **MAPPING_KMERS** options. Feel free of change parametters of mapping using **MAPPING_OPTIONS**

Assembled contigs could be used by blastn against a database, you can also try to annotate them!

.. code-block:: yaml

   PARAMS:
      ASSEMBLY:
         OVERLAP_SIZE : 15
         FILTER_CONTIG_SIZE : 100
         MAPPING_CONTIGS: True
         # if MAPPING_CONTIGS is activate, ikiss maps contigs vs REF using bwamem2
         REF: 'reference.fasta'
         MAPPING_OPTIONS : ""

