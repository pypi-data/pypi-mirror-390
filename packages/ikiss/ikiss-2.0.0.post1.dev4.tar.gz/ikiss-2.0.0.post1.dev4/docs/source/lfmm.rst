LFMM
===========


LFMM is used by iKISS for testing correlations between kmers and environmental data.

.. code-block:: yaml

   PARAMS:
      LFMM:
         K : 2
         PHENOTYPE_FILE: "pheno.txt"
         PHENOTYPE_PCA_ANALYSIS : false
         CORRECTION: 'BH'
         ALPHA : 0.05

+---------------------------+---------------------------------------------------------------------------------------------------------------------+
| Parameter                 | Description                                                                                                         |
+===========================+=====================================================================================================================+
|   K                       | Number of latent factors used in LFMM association analyses.                                                         |
+---------------------------+---------------------------------------------------------------------------------------------------------------------+
|   PHENOTYPE_FILE          | A phenotype file is mandatory for LFMM analysis. Can include PCA results, climate variables, etc.                   |
+---------------------------+---------------------------------------------------------------------------------------------------------------------+
|   PHENOTYPE_PCA_ANALYSIS  | - If **true**, iKISS automatically runs PCA using the file provided in **PHENOTYPE_FILE**.                          |
|                           | - If **false**, iKISS uses the file directly as 'phenotype' for LFMM analysis. Kmers are used as 'genotype' data    |
+---------------------------+---------------------------------------------------------------------------------------------------------------------+
|   CORRECTION              | kmers outliers are obtained using a correction of BONFERONNI, BH or FDR model                                       |
+---------------------------+---------------------------------------------------------------------------------------------------------------------+
|   ALPHA                   | modify the alpha cutoff for outlier detection                                                                       |
+---------------------------+---------------------------------------------------------------------------------------------------------------------+


Here, a example of a phenotype file with climate variables

.. code-block:: bash

    accession_id	group	b2.Mean_Diurnal_Range	b3.Isothermality	b4.Temp_Seasonality	b5.Max_Temp_of_Warmest_Month	b6.Min_Temp_of_Coldest_Month	b7.Temp_Annual_Range	b8.Mean_Temp_of
    _Wettest_Quarter	b9.Mean_Temp_of_Driest_Quarter	b10.Mean_Temp_of_Warmest_Quarter	b11.Mean_Temp_of_Coldest_Quarter	b12.Annual_Precipitation	b13.Precipitation_of_Wettest_Mo
    nth	b14.Precipitation_of_Driest_Month	b15.Precipitation_Seasonality	b16.Precipitation_of_Wettest_Quarter	b17.Precipitation_of_Driest_Quarter	b18.Precipitation_of_Warmest_Quarter	b19.Precipitation_of_Coldest_Quarter
    Clone12	2	99	68	1230	310	166	144	250	226	258	226	1462	249	3	68	573	17	549	17
    Clone14	2	100	68	1235	301	155	146	241	217	248	217	1525	259	3	67	603	18	575	18
    Clone16	2	93	65	1389	310	168	142	250	223	258	223	1416	264	0	73	579	8	544	8
    Clone20	2	154	55	3955	403	123	280	296	234	315	214	118	62	0	184	107	0	45	0
    Clone2	1	152	55	3617	403	128	275	287	242	316	220	173	80	0	167	153	0	18	0
    Clone4	1	168	51	5719	414	86	328	315	201	322	181	20	12	0	166	18	0	17	0
    Clone8	1	NA	NA	NA	NA	NA	NA	NA	NA	NA	NA	NA	NA	NA	NA	NA	NA	NA	NA

