Install iKISS
================

Check dependencies for iKISS : python and apptainer

|PythonVersions| |SnakemakeVersions| |Apptainer|

Install apptainer and python3 in your local machine OR use module load to add apptainer and python3 in your environment if you are working in a cluster :

.. code-block:: bash

   module load system/python/3.12.0
   module load system/apptainer/4.1.0

iKISS is NOW available as a PyPI package (recommended)

.. code-block:: bash

   python3 -m pip install ikiss


OR you can also install iKISS from git repository

.. code-block:: bash

   python3 -m pip install ikiss@git+https://forge.ird.fr/diade/iKISS.git

   #OR

   git clone https://forge.ird.fr/diade/iKISS.git
   cd iKISS
   python3 -m pip install .


Cluster mode
-------------------------------

Install iKISS in cluster mode using **apptainer** container from `ikiss_utilities <https://itrop.ird.fr/ikiss_utilities/>`_

.. code-block:: bash

   ikiss install --help
   ikiss install --mode slurm --env apptainer


Local mode
----------------------------

.. code-block:: bash

   ikiss install --help
   ikiss install --mode local --env apptainer


.. note::

    Only --env apptainner is allowed in iKISS. module environment are not used by iKISS.

.. note::

    If `--mode apptainer` was selected on iKISS installation, it could be needed to give argument --apptainer-args

.. |PythonVersions| image:: https://img.shields.io/badge/python-3.12-blue
   :target: https://www.python.org/downloads
.. |SnakemakeVersions| image:: https://img.shields.io/badge/snakemake-≥5.10.0-brightgreen.svg?style=flat
   :target: https://snakemake.readthedocs.io
.. |Apptainer| image:: https://img.shields.io/badge/apptainer-%E2%89%A53.3.0-7E4C74.svg
   :target: https://sylabs.io/docs/
.. |readthedocs| image:: https://pbs.twimg.com/media/E5oBxcRXoAEBSp1.png
   :target: https://culebront-pipeline.readthedocs.io/en/latest/
   :width: 400px
