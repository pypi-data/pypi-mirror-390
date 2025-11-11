PCADAPT
==============

PCADAPT detects kmers involved in biological adaptation and provides outlier detection based on Principal Component Analysis (PCA)

.. code-block:: yaml

   PARAMS:
      PCADAPT:
         K : 2
         CORRECTION: 'FDR'
         ALPHA : 0.05

+---------------------+------------------------------------------------+----------------+
| Type                | Description                                    | Default Value  |
+=====================+================================================+================+
| K                   | number K of principal components               |        2       |
+---------------------+------------------------------------------------+----------------+
| CORRECTION          | kmers outliers are obtained using a            | Bonferonni     |
|                     | Bonferonni, BH correction or a FDR model       |                |
+---------------------+------------------------------------------------+----------------+
| ALPHA               | modify the alpha cutoff for outlier detection  |      0.01      |
+---------------------+------------------------------------------------+----------------+


`Sample file` is a tabulated file contains `accession_id` and `group` columns:

.. code-block:: bash

   accession_id	group
   Clone12	2
   Clone14	2
   Clone16	2
   Clone20	2
   Clone2	1
   Clone4	1
   Clone8	1

+---------------------+------------------------------------------------+----------------+
| Type                | Description                                    | Default Value  |
+=====================+================================================+================+
| accession_id        | contains exactly same name of samples in FASTQ |                |
+---------------------+------------------------------------------------+----------------+
| phenotype_value     | contains sample group                          |                |
|                     | (ex. wild=1, cultivated=2)                     |                |
+---------------------+------------------------------------------------+----------------+

