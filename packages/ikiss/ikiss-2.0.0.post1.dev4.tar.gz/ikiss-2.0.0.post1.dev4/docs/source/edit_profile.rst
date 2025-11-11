Edit your profile
==========================

Before to running iKISS  you need to configurate local or cluster parameters running command line 'ikiss edit_profile'. Modify threads, ram, node and computer resources.

.. code-block:: bash

   ikiss edit_profile

In this file you can parameter cluster or local resources (RAM, cpu ...)

.. code-block:: bash

    # cluster params
    max-jobs-per-second: 10
    max-status-checks-per-second: 10
    jobs: 200

    # Snakemake params
    executor: dryrun        # slurm,slurm-jobstep,local,dryrun,touch
    software-deployment-method: apptainer
    latency-wait: 1296000
    printshellcmds: true
    cores: 8
    keep-going: True
    rerun-incomplete: True
    restart-times: 0
    show-failed-logs: True
    rerun-triggers: ["code","input","mtime","params","software-env"]
    keep-incomplete: False

    # Default resources for all rules
    default-resources:
        slurm_account: orjuela
        #slurm_extra: ""
        slurm_partition: PARTITION
        mem_per_cpu: 4G
        runtime: 130h
        threads: 1

    #(in local)
    set-threads:
      kmers_gwas_per_sample: 8
      kmers_to_use: 4
      kmers_table: 4
      extract_kmers_from_bed: 4
      mapping_kmers: 4
      filter_bam: 8
      kmer_position_from_bam: 8
      pcadapt: 8
      merge_method: 2
      outliers_position: 2
      lfmm: 8
      samtools_merge: 8
      index_ref: 8
      index_ref_to_assembly: 8
      get_pca_from_phenotype: 4

        # Specific resources for some rules
    set-resources:
      kmers_gwas_per_sample:
        threads: 4
        mem-per-cpu: 25G


.. note::

    iKISS copies his provided `config.yaml` file into your home "/home/$USER/.config/ikiss-snake8/config.yaml".
