#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pathlib import Path
from .module import IKISS

from .global_variables import GIT_URL, DOCS, DATATEST_URL_FILES, APPTAINER_URL_FILES
from ._version import version as __version__
from ._version import version_tuple

logo = Path(__file__).parent.resolve().joinpath('logo_ikiss.png').as_posix()

__doc__ = """ iKISS is a pipeline to identify kmers under selection  """

description_tools = f"""
    Welcome to iKISS version: {__version__} ! 
    @author: Julie Orjuela (IRD)
    @email: julie.orjuela@ird.fr
    Please cite our git: {GIT_URL}
    Licenced under MIT 
    Intellectual property belongs to IRD and authors."""

dico_tool = {
    "soft_path": Path(__file__).resolve().parent.as_posix(),
    "url": GIT_URL,
    "docs": DOCS,
    "description_tool": description_tools,
    "apptainer_url_files": APPTAINER_URL_FILES,
    "datatest_url_files": DATATEST_URL_FILES,
    "snakefile": Path(__file__).resolve().parent.joinpath("Snakefile"),
    "snakemake_scripts": Path(__file__).resolve().parent.joinpath("snakemake_scripts")
    #default_profile est pris par default snakecdysis install default_profile
    #"git_configfile_path": Path(__file__).resolve().parent.joinpath("install_files/configfile.yaml")
}
