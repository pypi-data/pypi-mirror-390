Running a datatest
====================

Running iKISS using the dataset provided by the tool. Here it will downloaded and decompressed on the TEST directory.

.. code-block:: bash

   ikiss test_install --help
   ikiss test_install -d TEST

Launch suggested command line done by iKISS, in local or cluster:

.. code-block:: bash

   ikiss run --help
   ikiss run -c TEST/data_test_config.yaml --apptainer-args "--bind $HOME"
   # @IFB
   ikiss run -c TEST/data_test_config.yaml --apptainer-args "--bind /shared:/shared"
   #you can also use snakemake parameters as
   ikiss run -c TEST/data_test_config.yaml --rerun-incomplete --nolock --apptainer-args "--bind $HOME"

.. warning::

    In i-Trop cluster, run iKISS using ONLY a node, data has to be in "/scratch" of chosen node. Use `nodelist : nodeX` parameter inside of config.yaml file.


* If you are on your local computer, you can pass `-t` params to parallelize in the local machine.

.. code-block:: bash

   ikiss run_local --help
   ikiss run_local -t 8 -c TEST/data_test_config.yaml --apptainer-args "--bind $HOME"

.. note::

    In local mode, its possible to allocate threads to some rules using `--set-threads` snakemake argument such as

    .. code-block:: bash

        ikiss run_local -t 8 -c TEST/data_test_config.yaml --set-threads kmers_gwas_per_sample=4 mapping_kmers=2 filter_bam=2 kmer_position_from_bam=4 pcadapt=2 extract_kmers_from_bed=2

