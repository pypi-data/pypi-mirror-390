INTERSECT
---------------

iKISS uses bedtools intersect to calculate how many kmers/contigs are mapped in **FEATURES** (gene by default).

These **FEATURES** are filtered from the annotation **GFF** file before use bedtools intersect.

iKISS filtered kmers/contigs by using **FILTER_MAPQ_STATS** and minimal kmers/contigs number **FILTER_MIN_STATS** by FEATURE.

.. code-block:: yaml

   PARAMS:
      INTERSECT:
            GFF : 'reference.gff'
            FEATURE : 'gene'
            FILTER_MAPQ_STATS: '15'


