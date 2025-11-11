#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from .global_variables import *
from snakecdysis import *

class IKISS(SnakEcdysis):
    """
    class IKISS creates an object with fastq attributes and self functions (adapted from CulebrONT)
    """
    def __init__(self, dico_tool, workflow, config):
        super().__init__(**dico_tool, workflow=workflow, config=config)
        self.workflow = workflow
        self.config = config
        self.fastq_files_list = []
        self.fastq_files_ext = []
        self.fastq_names_list = []
        self.fastq_gzip = None
        self.ref = None
        self.samples = {}
        self.phenotype = {}
        self.mapping_mode = 'bwa-aln'
        self.method = []
        self.diversity_method = []
        self.times_div = 1
        self.mode = 'apptainer'

        self.forward = ""
        self.reverse = ""

        #self.use_env_modules = workflow.use_env_modules
        #self.use_conda = workflow.use_conda
        #self.use_apptainer = workflow.use_apptainer

        self.__check_config_dic()
        self.__split_illumina()

        # checked config.yaml:
        self.write_config(f"{self.config['DATA']['OUTPUT']}/config_corrected.yaml")

    def __split_illumina(self):
        forward = []
        reverse = []
        for fastq in self.fastq_files_list:
            if '_R1' in fastq:
                forward.append(fastq)
            elif '_1' in fastq:
                forward.append(fastq)
            elif '_R2' in fastq:
                reverse.append(fastq)
            elif '_2' in fastq:
                reverse.append(fastq)
        return forward, reverse

    def __check_config_dic(self):
        """Configuration file checking"""
        self.tools_activated = self.__build_tools_activated("WORKFLOW", ("KMERS_MODULE", "SNMF", "PCADAPT", "LFMM", "MAPPING_KMERS", "ASSEMBLY_KMERS", 'INTERSECT'), True)

        # check mandatory directory
        self.check_dir_or_string(level1="DATA", level2="OUTPUT")
        self.check_dir_or_string(level1="DATA", level2="FASTQ")

        def get_mapping_mode(self, list):
            if self in list:
                #print (self)
                return self
            else:
                raise ValueError(
                    f"CONFIG FILE CHECKING FAIL : you need to chose between {ALLOW_MAPPING_MODE} in MAPPING_KMERS mode !")

        def get_dico_samples_and_pop(self, path):
            # check of header
            infile = open(path, 'r')
            if not 'accession_id\tgroup' in infile.readline():
                raise ValueError(
                    f"SAMPLES FILE CHECKING FAIL : Please add accession_id\tgroup in SAMPLES tabulated header !")
            infile.close()
            # populating self.samples
            with open(path, "r") as samples_open:
                for line in samples_open:
                    if not 'accession_id' in line:
                        key, value = line.strip().split('\t')
                        self.samples[key] = value
            return self.samples

        def get_dico_phenotype_and_pop(self, path):
            # check of header
            infile = open(path, 'r')
            if not 'accession_id\tgroup' in infile.readline():
                raise ValueError(
                    f"PHENOTYPE_FILE CHECKING FAIL : Please add accession_id\tgroup in PHENOTYPE_FILE tabulated header !")
            infile.close()
            # populating self.samples
            with open(path, "r") as phenotype_open:
                for line in phenotype_open:
                    if not 'accession_id' in line:
                        key, *value = line.strip().split('\t')
                        self.phenotype[key] = value
            return self.phenotype

        # pick fastq and extension
        self.fastq_files_list, fastq_files_list_ext = get_files_ext(self.get_config_value(level1='DATA', level2='FASTQ'), ALLOW_FASTQ_EXT)
        if not self.fastq_files_list:
            raise ValueError(
                f"CONFIG FILE CHECKING FAIL : you need to append at least on fastq with extension on {ALLOW_FASTQ_EXT}")
        # check if all fastq have the same extension
        if len(fastq_files_list_ext) > 1:
            raise ValueError(
                f"CONFIG FILE CHECKING FAIL : Please use only the same format for assembly FASTQ data, not: {fastq_files_list_ext}")
        else:
            self.fastq_files_ext = fastq_files_list_ext[0]
        # check if fastq are gzip
        if "gz" in self.fastq_files_ext:
            self.fastq_gzip = True

        self.forward, self.reverse = self.__split_illumina()

        self.mapping_mode = get_mapping_mode(self.config['PARAMS']['MAPPING_KMERS']['MODE'], ALLOW_MAPPING_MODE)

        # get methods 
        for ele in AVAIL_METHOD:
            if ele in self.tools_activated:
                self.method.append(ele)

        if 'SNMF' in self.tools_activated:
            self.diversity_method.append('SNMF')

        # get samples name from reads files
        for elem in self.fastq_files_list:
            if '_R1' in elem :
                fastq_name = Path(elem).stem.split('_R1')[0]
                self.fastq_names_list.append(fastq_name)
            if '_1' in elem or '_1' in elem:
                fastq_name = Path(elem).stem.split('_1')[0]
                self.fastq_names_list.append(fastq_name)


        # kmers_module is obligatory and has to be activated,
        if not bool(self.config['WORKFLOW']['KMERS_MODULE']):
            raise ValueError(
                f"CONFIG FILE CHECKING ERROR : KMERS_MODULE is the minimal step you need to activate in the configuration file !! \n")

        # if mapping is true pcadapt or lfmm has to be activated
        if not self.config['WORKFLOW']['PCADAPT'] and not self.config['WORKFLOW']['LFMM'] and not self.config['WORKFLOW']['KMERS_MODULE'] and self.config['WORKFLOW']['MAPPING_KMERS']:
            raise ValueError(
                f"CONFIG FILE CHECKING ERROR : MAPPING_KMERS is irrelevant if you have not activated PCADAPT or LFMM !! \n")

        if self.config['WORKFLOW']['KMERS_MODULE'] and not self.config['WORKFLOW']['PCADAPT'] and not self.config['WORKFLOW']['LFMM']:
                if self.config['WORKFLOW']['INTERSECT'] and not self.config['WORKFLOW']['MAPPING_KMERS']:
                    raise ValueError(
                        f"CONFIG FILE CHECKING ERROR : INTERSECT is irrelevant if you have not activated MAPPING_KMERS when you are in KMERS_MODULE only (not methods) !!\n")

        # if intersect is true, mapping or assembly of kmers have to be activated
        if self.config['WORKFLOW']['INTERSECT'] and not self.config['WORKFLOW']['ASSEMBLY_KMERS'] and not self.config['WORKFLOW']['MAPPING_KMERS']:
           raise ValueError(
               f"CONFIG FILE CHECKING ERROR : INTERSECT is irrelevant if you have not activated MAPPING_KMERS or ASSEMBLY_KMERS !!\n")

        # check if reference is given by user if mapping is activated
        if self.config['WORKFLOW']['MAPPING_KMERS']:
            self.check_file_or_string(level1="PARAMS", level2="MAPPING_KMERS", level3="REF", mandatory=['MAPPING_KMERS'])
        
        # if intersect is true. check reference, gff and feature if mapping of kmers is activated
        # if intersect is true. check reference, gff and feature  if assembly_kmers is activated
        if self.config['WORKFLOW']['INTERSECT'] :
            self.check_file_or_string(level1="PARAMS", level2="INTERSECT", level3="GFF", mandatory=['INTERSECT'])
            self.check_file_or_string(level1="PARAMS", level2="INTERSECT", level3="FEATURE")

        if self.config['WORKFLOW']['ASSEMBLY_KMERS'] and not self.config['WORKFLOW']['LFMM'] and not self.config['WORKFLOW']['PCADAPT']:
            raise ValueError(
               f"CONFIG FILE CHECKING ERROR : ASSEMBLY_KMERS is irrelevant if you have not activated PCADAPT or LFMM !!\n")

        if self.config['PARAMS']['ASSEMBLY_KMERS']['MAPPING_CONTIGS'] :
            self.check_file_or_string(level1="PARAMS", level2="ASSEMBLY_KMERS", level3="REF", mandatory=['ASSEMBLY_KMERS'])
        
        if self.config['WORKFLOW']['MAPPING_KMERS']:
            self.check_file_or_string(level1="PARAMS", level2="MAPPING_KMERS", level3="REF", mandatory=['MAPPING_KMERS'])


        # check if samples file is correct if KMERS_MODULE is activated
        if self.config['WORKFLOW']['KMERS_MODULE']:
            self.check_file_or_string(level1="PARAMS", level2="KMERS_MODULE", level3="SAMPLES_FILE", mandatory=['KMERS_MODULE'])
            # get dico with samples names as key and population as value.
            self.samples = get_dico_samples_and_pop(self, self.get_config_value(level1='PARAMS', level2='KMERS_MODULE', level3='SAMPLES_FILE'))
            # comparing names from reads and names from samples.txt given by user
            if sorted(self.fastq_names_list) != sorted(list(self.samples.keys())):
                print("samples in FASTQ but not in SAMPLES")
                print(set(sorted(self.fastq_names_list)) - set(sorted(list(self.samples.keys()))))
                print("samples in SAMPLES but not in FASTQ")
                print(set(sorted(list(self.samples.keys()))) - set(sorted(self.fastq_names_list)))
                raise ValueError(
                f"CONFIG FILE CHECKING ERROR : FASTQ names and SAMPLES names are different. Please check your samples file !")



        # check if phenotype file is correct if LFMM is activated
        if self.config['WORKFLOW']['LFMM']:
            self.check_file_or_string(level1="PARAMS", level2='LFMM', level3="PHENOTYPE_FILE", mandatory=['LFMM'])
            # get dico with samples names as key and phenotype as value.
            self.phenotype = get_dico_phenotype_and_pop(self, self.get_config_value(level1='PARAMS', level2='LFMM',  level3='PHENOTYPE_FILE'))
            # comparing names from reads and names from phenotype.txt given by user
            if sorted(self.fastq_names_list) != sorted(list(self.phenotype.keys())):
                # print(sorted(self.fastq_names_list))
                # print(sorted(list(self.phenotype.keys())))
                print("samples in FASTQ but not in PHENOTYPE")
                print(set(sorted(self.fastq_names_list)) - set(sorted(list(self.phenotype.keys()))))
                print("samples in SAMPLES but not in PHENOTYPE")
                print(set(sorted(list(self.phenotype.keys()))) - set(sorted(self.fastq_names_list)))
                raise ValueError(
                    f"CONFIG FILE CHECKING ERROR : FASTQ names and PHENOTYPE names are different. Please check your phenotype file !")


        if self.config['WORKFLOW']['PCADAPT']:
            if type(self.config['PARAMS']['PCADAPT']['K']) is not int:
                raise TypeError( f"CONFIG FILE CHECKING ERROR :  PARAMS/PCADAPT/K is not a integer !! \n")

        if self.config['WORKFLOW']['LFMM']:
            if type(self.config['PARAMS']['LFMM']['K']) is not int:
                raise TypeError( f"CONFIG FILE CHECKING ERROR :  PARAMS/LFMM/K is not a integer !! \n")

        if self.config['WORKFLOW']['SNMF']:
            if type(self.config['PARAMS']['SNMF']['NB']) is not int:
                raise TypeError( f"CONFIG FILE CHECKING ERROR :  PARAMS/SNMF/NB is not a integer !! \n")
            else:
                self.times_div = self.config['PARAMS']['SNMF']['NB']

        if self.config['WORKFLOW']['SNMF']:
            if type(self.config['PARAMS']['SNMF']['BEST_K']) is not int:
                raise TypeError( f"CONFIG FILE CHECKING ERROR :  PARAMS/SNMF/BEST_K is not a integer !! \n")

            if type(self.config['PARAMS']['SNMF']['K_MIN']) is not int:
                raise TypeError( f"CONFIG FILE CHECKING ERROR :  PARAMS/SNMF/K_MIN is not a integer !! \n")

            if type(self.config['PARAMS']['SNMF']['K_MAX']) is not int:
                raise TypeError( f"CONFIG FILE CHECKING ERROR :  PARAMS/SNMF/K_MAX is not a integer !! \n")

            if type(self.config['PARAMS']['SNMF']['REPETITIONS']) is not int:
                raise TypeError( f"CONFIG FILE CHECKING ERROR :  PARAMS/SNMF/REPETITIONS is not a integer !! \n")

            if self.config['PARAMS']['SNMF']['K_MIN'] >= self.config['PARAMS']['SNMF']['K_MAX'] :
                raise TypeError( f"CONFIG FILE CHECKING ERROR :  K_MIN is greater or equal than K_MAX!! \n")

            if self.config['PARAMS']['SNMF']['BEST_K'] > self.config['PARAMS']['SNMF']['K_MAX'] :
                raise TypeError( f"CONFIG FILE CHECKING ERROR : BEST_K is greater than K_MAX, please adapt SNMF parameters !! \n")

    def __check_tools_config(self, tool, mandatory=[]):
        """Check if path is a file and if it is not empty
        :return absolute path file"""
        tool_OK = False
        deployment = str(list(self.workflow.deployment_settings.deployment_method)[0])
        # If only envmodule
        if deployment == "env-modules":
            envmodule_key = self.tools_config["ENV-MODULES"][tool]
            if not envmodule_key:
                raise ValueError(
                    f'CONFIG FILE CHECKING FAIL : please check tools_path.yaml in the "ENV-MODULES" section, {tool} is empty')
            tool_OK = True

        if len(mandatory) > 0 and not tool_OK:
            raise FileNotFoundError(
                f'CONFIG FILE CHECKING FAIL : please check tools_path.yaml in the {tool} params, please add module, is mandatory for tool: {" ".join(mandatory)}')

    def __build_tools_activated(self, level1, allow, mandatory=False):
        tools_activate = []
        for tool, activated in self.config[level1].items():
            if tool in allow:
                boolean_activated = var_2_bool(level1, tool, activated)
                if boolean_activated:
                    tools_activate.append(tool)
                    self.set_config_value(level1=level1, level2=tool, value=boolean_activated)
                    #self.__check_tools_config(tool, [tool])
            else:
                raise ValueError(f'CONFIG FILE CHECKING FAIL : {level1} {tool} not allow on iKISS"')
        if len(tools_activate) == 0 and mandatory:
            raise ValueError(f"CONFIG FILE CHECKING FAIL : you need to set True for at least one {level1} from {allow}")
        return tools_activate
