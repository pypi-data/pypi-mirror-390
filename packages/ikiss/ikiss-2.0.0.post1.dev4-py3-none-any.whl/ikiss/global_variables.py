from pathlib import Path

DOCS = "https://forge.ird.fr/diade/iKISS/-/blob/master/README.rst"
GIT_URL = "https://forge.ird.fr/diade/iKISS"

ALLOW_FASTQ_EXT = (".fastq", ".fq", ".fq.gz", ".fastq.gz")
ALLOW_FASTA_EXT = (".fasta", ".fa", ".fa.gz", ".fasta.gz")
ALLOW_MAPPING_MODE = ("bwa-aln", "bwa-mem2")
ALLOW_GFF_EXT = (".gtf", ".gff")
AVAIL_METHOD = ("LFMM", "PCADAPT")
AVAIL_DIVERSITY_METHOD = ("SNMF")

INSTALL_PATH = Path(__file__).resolve().parent
APPTAINER_URL_FILES = [('https://itrop.ird.fr/ikiss_utilities/apptainer.ikiss_tools.sif',
              'INSTALL_PATH/containers/apptainer.ikiss_tools.sif')]

DATATEST_URL_FILES = ("https://itrop.ird.fr/ikiss_utilities/DATATEST.zip", "DATATEST.zip")
