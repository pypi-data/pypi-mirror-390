.. ikiss documentation master file, created by
   sphinx-quickstart on Fri Aug  2 13:48:06 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

About iKISS
===============

.. image:: _static/logo_ikiss.png
    :target: https://forge.ird.fr/diade/iKISS

**iKISS** (Kmer Inference Selection and Structure) is a snakemake reference-Free pipeline for inferring diversity, structuration, selection and genotype-phenotype association.

iKISS uses `KmersGWAS <https://github.com/voichek/kmersGWAS>`_,
`PCADAPT <https://cran.r-project.org/web/packages/pcadapt/readme/README.html>`_
and `LFMM <https://bcm-uga.github.io/lfmm/articles/lfmm>`_  to select genomics regions under selection.


IKISS PIPELINE
==============

.. toctree::
   :caption: Install
   :name: Install Guide
   :maxdepth: 2

   install.rst

.. toctree::
   :caption: Edit a profile
   :name: Profile
   :maxdepth: 2

   edit_profile.rst

.. toctree::
   :caption: Running a data test
   :name: Running test
   :maxdepth: 2

   run_test.rst

.. toctree::
   :caption: Sections
   :name: Sections
   :maxdepth: 2

   section.rst

.. toctree::
   :caption: Modules
   :name: modules
   :maxdepth: 2

   modules.rst

.. toctree::
   :caption: Output
   :name: output
   :maxdepth: 2

   results.rst


.. toctree::
   :caption: About Us
   :name: Authors and Contributors
   :maxdepth: 2

   authors_contrib.rst


.. toctree::
   :caption: License
   :name: License
   :maxdepth: 2

   licence.rst


Thanks
-------

The authors acknowledge the IRD `i-Trop <https://bioinfo.ird.fr/>`_ HPC from IRD Montpellier and the `IFB <https://www.france-bioinformatique.fr/en/home/>`_ for providing HPC resources that contributed to this work.


Contributions
--------------

iKISS is inspired from `culebrONT project <https://culebront-pipeline.readthedocs.io/en/latest/>`_.

iKISS uses `SnakEcdysis package <https://snakecdysis.readthedocs.io/en/latest/package.html>`_  to perform installation and execution in local and cluster mode.


