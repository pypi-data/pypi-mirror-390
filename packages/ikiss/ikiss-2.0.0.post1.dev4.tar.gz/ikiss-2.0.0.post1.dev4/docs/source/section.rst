Pipeline configuration file
====================================

Before to run iKISS, create and adapt the pipeline on the `configfile.yaml`.

.. code-block:: bash

   ikiss create_config -c configfile.yaml

Three sections are described on the `configfile.yaml` file.

Data section
-------------------

First, adapt the `configfile.yaml` file with the fastq path (FASTQ) and the outfile path (OUTPUT) in the `DATA` section.

.. code-block:: yaml

   DATA:
      FASTQ: './DATATEST/fastq'
      OUTPUT: './OUTPUT-KISS/'

.. warning::

    if you are using illumina paired reads, you need rename reads SAMPLE_R1.fastq.gz and SAMPLE_R2.fastq.gz. For single reads use SAMPLE_R1.fastq.gz

.. note::

    iKISS uses compressed and decompressed fastq files


Workflow section
-----------------------

Chose the iKISS steps using the section WORKFLOW and parameter it with the PARAMS sections.

In WORKFLOW section, several modes can be launched:

+----------------------+-----------------------------------------------------------------------------------------------------------------------------+
| Tool                 | Description                                                                                                                 |
+======================+=============================================================================================================================+
| **KMERS_GWAS**       | Convert reads in kmers, filter them and create a format ready to use in population genomics                                 |
+----------------------+-----------------------------------------------------------------------------------------------------------------------------+
| **PCADAPT**          | Detects genetic markers (kmers) involved in biological adaptation and provides outlier detection based on Principal         |
|                      | Component Analysis (PCA).                                                                                                   |
+----------------------+-----------------------------------------------------------------------------------------------------------------------------+
| **LFMM**             | Used by iKISS for testing correlations between kmers and environmental data.                                                |
+----------------------+-----------------------------------------------------------------------------------------------------------------------------+
| **SNMF**             | Optionally used to compute least-squares estimates of ancestry proportions and ancestral allelic frequencies.               |
+----------------------+-----------------------------------------------------------------------------------------------------------------------------+
| **MAPPING_KMERS**    | Optionally used to align kmers to a genomic reference (if a reference is available).                                        |
+----------------------+-----------------------------------------------------------------------------------------------------------------------------+
| **ASSEMBLY_KMERS**   | Optionally assembles significant kmers obtained by pcadapt or lfmm.                                                         |
+----------------------+-----------------------------------------------------------------------------------------------------------------------------+
| **INTERSECT**        | Optionally calculates how many kmers (if MAPPING_KMERS is activated) or contigs (if ASSEMBLY_KMERS is activated) are found  |
|                      | in FEATURES (gene by default).                                                                                              |
+----------------------+-----------------------------------------------------------------------------------------------------------------------------+

.. note::

    `KMERS_GWAS` step has to be activated by default.

.. note::

     ̀PCADAPT`,`̀LFMM`, `SNMF`, `MAPPING` or `ASSEMBLY` are optional. Active or deactivate these steps using true or false.


.. code-block:: yaml

    WORKFLOW:
        # convert reads in kmers and computes a binary matrix
        KMERS_MODULE : true
        # structure genotype based in ancestry
        SNMF: true
        # structure genotype based in pca
        PCADAPT : true
        # calculate association between genotype and phenotype
        LFMM : true
        # mapping of kmers over a genomic reference
        MAPPING_KMERS: true
        # assembly kmers outliers detected by pcadapt and lfmm
        ASSEMBLY_KMERS : true
        # intersect outliers position (directly kmers or contigs) and features in a gff
        INTERSECT : true


Params section
--------------------

In the PARAMS section, parameters of tools can be modified and adapted.

Please check the documentation of module you are interested to parameter integrated tools.

