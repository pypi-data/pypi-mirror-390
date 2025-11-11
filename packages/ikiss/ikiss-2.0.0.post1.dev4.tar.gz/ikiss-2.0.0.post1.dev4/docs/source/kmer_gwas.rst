Kmers module
==============

KMERS_GWAS module decompose reads into kmers and create a binary table of presence/absence of kmers. This table can be filter to use only most informative kmers into the populations. PLINK format outfile are obtained in this module.

.. code-block:: yaml

   PARAMS:
      KMERS_MODULE:
         KMER_SIZE : 31
         MAC : 2
         P : 0.2
         MAF : 0.05
         B : 1000000 # nb kmers in each bed file
         SPLIT_LIST_SIZE : 100000
         MIN_LIST_SIZE : 50000
         SAMPLES_FILE: "samples.txt"


+---------------------+------------------------------------------------+----------------+
| Type                | Description                                    | Default Value  |
+=====================+================================================+================+
| KMER_SIZE           | Length of kmers (should be between 15-31)      |        31      |
+---------------------+------------------------------------------------+----------------+
| MAC                 | Minor allele count (min allowed appearance     |                |
|                     | of a kmer)                                     |                |
+---------------------+------------------------------------------------+----------------+
| P                   | Minimum percent of appearance in each strand   |                |
|                     | form                                           |                |
+---------------------+------------------------------------------------+----------------+
| MAF                 | Minimum allele frequency                       |                |
+---------------------+------------------------------------------------+----------------+
| B                   | Number of kmers in each bed file               |                |
+---------------------+------------------------------------------------+----------------+
| SPLIT_LIST_SIZE     | Number of kmers by bed file                    |                |
+---------------------+------------------------------------------------+----------------+
| MIN_LIST_SIZE       | Minimal number of kmers allowed in the         |                |
|                     | smaller bed file after splitting               |                |
+---------------------+------------------------------------------------+----------------+


.. note::

    if you active `KMERS_MODULE` and no active `PCADAPT` and `LFMM`, iKISS calculate occurrences of presence and absence of kmers into the populations using the whole of kmers and groups given by user into the SAMPLES_FILE. If `MAPPING` and `INTERSECT` are also activated you can check occurrences found into chosen features (genes).
