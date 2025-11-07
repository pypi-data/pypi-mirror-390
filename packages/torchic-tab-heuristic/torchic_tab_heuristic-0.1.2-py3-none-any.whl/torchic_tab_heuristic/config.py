import os

#Configuration for paths and connection
class Config:

    IS_LOCAL = True
    PENALTY_LIMIT = 5
    CANDIDATE_LIMIT =20
    ELASTIC_INDEX = "wd_names_2023"


    if IS_LOCAL:
        ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        DATA_DIR = os.path.join(ROOT_DIR, 'Data')
        
        FILE_WD = os.path.join(DATA_DIR, 'wikidata-20230201-truthy-BETA.nt.bz2')
        INPUT_DIR = os.path.join(DATA_DIR, 'Input Files')
        INPUT_DIR_2023 = os.path.join(DATA_DIR, 'Input Files 2023/Round 1 - Wikidata/WikidataTables2023R1/DataSets/Valid/tables')
        INPUT_DIR_TEST_2023 = os.path.join(DATA_DIR, 'Input Files 2023/Round 1 - Wikidata/WikidataTables2023R1/DataSets/Test/tables')
        INPUT_DIR_TFOOD_VAL_2023 = os.path.join(DATA_DIR, 'Input Files 2023/tfood/entity/val/tables')
        ACTIVATE_AUTH = False

        R1_CPA_WD = "Results/R1_WD_Valid/R1_cpa_wd.csv"
        R1_CEA_WD = "Results/R1_WD_Valid/R1_cea_wd.csv"
        R1_CTA_WD = "Results/R1_WD_Valid/R1_cta_wd.csv"
        R1_TD_TFOOD_ENT = "Results/R1_WD_Valid/R1_td_tfood_ent.csv"
        R1_CEA_TFOOD_ENT = "Results/R1_WD_Valid/R1_cea_tfood_ent.csv"


    else:
        ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        DATA_DIR = os.path.join(ROOT_DIR, 'Dataset')
        
        FILE_WD = os.path.join(DATA_DIR, 'wikidata-20230201-truthy-BETA.nt.bz2')
        # INPUT_DIR = os.path.join(DATA_DIR, 'Input Files')
        INPUT_DIR_2023 = os.path.join(DATA_DIR, '/users/u0162181/semtab/Dataset/WikidataTables2023R1/Datasets/Valid/tables')

        ACTIVATE_AUTH = True
        CA_CERTS = "/users/u0162181/elasticsearch-8.3.3/config/certs/http_ca.crt"
        USER_NAME = "elastic"
        #PASSWORD = 

        R1_CPA_WD = "SemTab/R1_cpa_wd.csv"
        R1_CEA_WD = "SemTab/R1_cea_wd.csv"
        R1_CTA_WD = "SemTab/R1_cta_wd.csv"

