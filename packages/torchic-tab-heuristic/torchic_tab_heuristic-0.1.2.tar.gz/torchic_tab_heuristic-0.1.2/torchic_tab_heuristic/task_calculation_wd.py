from .preprocessing import load_table
from .preprocessing import clean_table
from .annotation import annotate
import spacy
from .config import Config
from .data_load import connect_elastic
import glob
import os
from .lookup import get_entity_combos
from .lookup import get_candidates
from .lookup import get_candidates_wd
from .entity_classes import EntityCell
from .entity_classes import EntityColumn
from .entity_classes import CandidateEntity
from .context_score import get_wd_candidate_data
from .cpa_calculation import cpa_table
from .annotation import key_column_detection
from .cea_calculation import cea_table
from .cta_calculation import cta_table
from .wikidata_searcher import WikidataSearcher
from .utils import * 
import pandas as pd

def analyze_table(es, df, prim_annotations, sec_annotations, subject_column, searcher):
    
    """Analyzes table, finds candidates and scores"""
    
    columns = df.keys()
    entity_columns = []
    entities_analyzed = []
    candidates_list = []
    literal_scores_list = []
    candidate_objects = []
    
    print("\n\n\nCandidates searching...")
    for i in range(len(prim_annotations)):

        if prim_annotations[i] == "NE":    

            column_list = df[columns[i]].to_list()
            entity_column = EntityColumn(i)

            for j in range (len(column_list)):
                cell = EntityCell(str(column_list[j]), j, i)
                #print("Processing cell:", cell.name)

                if column_list[j] == None:
                    entity_column.cells.append(cell)
                    continue

                #print("\nFinding entity candidates...")
                #Check if entity has been investigated already, else find candidates
                if column_list[j] in entities_analyzed:
                    candidate_index = entities_analyzed.index(column_list[j])
                    candidates = candidates_list[candidate_index]
                    literal_scores = literal_scores_list[candidate_index]
                else:
                    entities_analyzed.append(column_list[j])
                    entity_combos, discrete_words = get_entity_combos(cell.name)
                    if es:
                        candidates, literal_scores = get_candidates(es, entity_combos, discrete_words, searcher)
                    else:
                        candidates, literal_scores = get_candidates_wd(entity_combos, discrete_words, searcher)
                    #print("Entity candidates found!\n")
                    candidates_list.append(candidates)
                    if i != subject_column:
                        for candidate in candidates:
                            candidate_objects.append(candidate)
                    literal_scores_list.append(literal_scores)  

                for qid in candidates:
                    cand = CandidateEntity(qid)
                    cand.literal_score = literal_scores[candidates.index(qid)]
                    #print("\t", cand.qid, cand.literal_score)
                    cell.candidate_entities.append(cand)

                #print("Candidates found!\n")
                entity_column.cells.append(cell)

            entity_columns.append(entity_column)


    print("\n\n\nContext score estimation...")
    ne_col_count = -1
    for i in range(len(prim_annotations)):

        if prim_annotations[i] == "NE":    
            
            ne_col_count += 1
            column_list = df[columns[i]].to_list()
            entity_column = entity_columns[ne_col_count]

            for j in range (len(column_list)):
                
                cell = entity_column.cells[j]
                cell_row, prim_neighbor_annotations, sec_neighbor_annotations = \
                get_cell_row(df, j, i, columns, prim_annotations, sec_annotations)
                
                #print("Retrieving candidates' properties and attributes...")
                for cand in cell.candidate_entities:
                    if cell_row == []:
                        cand.candidate_score = cand.literal_score
                    else:
                        is_subject = True if i == subject_column else False
                        cand = get_wd_candidate_data(cand, cell_row, prim_neighbor_annotations,
                               sec_neighbor_annotations, candidate_objects, searcher, is_subject)
                        cand.candidate_score = get_candidate_score(
                                               cand.literal_score, cand.context_score)
    
    return entity_columns



def get_cell_row(df, row, col, columns, prim_annotations, sec_annotations):
    """Extracts context (neighboring cells) of a cell"""

    cell_row = df.iloc[row].drop(columns[col]).to_list()
    
    prim_neighbor_annotations = prim_annotations[:col] + prim_annotations[col+1:]
    sec_neighbor_annotations = sec_annotations[:col] + sec_annotations[col+1:]

    for item in cell_row:
        if item == None:
            del prim_neighbor_annotations[cell_row.index(item)]
            del sec_neighbor_annotations[cell_row.index(item)]
            del cell_row[cell_row.index(item)]
            
    return cell_row, prim_neighbor_annotations, sec_neighbor_annotations


def get_candidate_score(literal_score, context_score):
    """Assigns candidate final scores (Literal scores + Context score)"""

    context_factor, literal_factor, total_factor = 1.0, 4.0, 1.0  
    score = ((context_score) * (literal_score**literal_factor))
    return score


def analyze_dataset_wd(input_path, es, nlp):
    """Analyzes Wikidata datsets and calculate annotations"""
    subject_column = 0

    cta_columns = ['fileid','col','type']
    cta_file = Config.R1_CTA_WD

    for file in glob.glob(os.path.join(input_path, '*.csv')):

        files_analyzed = list(set(pd.read_csv(cta_file,
                         header=None, names=cta_columns)["fileid"].to_list()))
        filename = file.split("/")[-1].split(".")[0]
        print("\nFile:", filename)
        if filename in files_analyzed:
            print("Skip!")
            continue

        df = load_table(file)
        df = clean_table(df)
        primary_annotations, secondary_annotations = annotate(nlp, df)
        #subject_column = key_column_detection(df, primary_annotations)

        print("Table:", file, "\n", df,"\n")
        print("Primary annotations:", primary_annotations)
        print("Secondary annotations:", secondary_annotations, "\n")
            
        
        entity_columns = analyze_table(es, df, primary_annotations,
        secondary_annotations, subject_column)

        top_properties, bonus_entities = \
        cpa_table(df, entity_columns, primary_annotations, secondary_annotations)
        print("CPA:")
        for property in top_properties:
            print(property.pid)
        top_entities = cea_table(entity_columns, bonus_entities)
        print("CEA:")
        for key in top_entities.keys():
            for ent in top_entities[key]:
                if ent != None:
                    print(key, ent.qid)
        print("CTA:")
        top_types = cta_table(top_entities)
        for type in top_types:
            print(type.qid)

        
        write_to_files(filename, top_properties, top_entities, top_types)
        

    return


def generate_annotations(file, es_index=True):
    """Generates detailed annotations for a given table"""

    print("TorchicTab Initiated!")
    PREFIX_ENT = "http://www.wikidata.org/entity/"
    PREFIX_PROP = "http://www.wikidata.org/prop/direct/"
    searcher = WikidataSearcher()

    try:
        nlp = spacy.load("en_core_web_sm")
    except OSError:
        print("Downloading 'en_core_web_sm' model for structural annotations...")
        spacy.cli.download("en_core_web_sm")
        nlp = spacy.load('en_core_web_sm')

    es = connect_elastic() if es_index else None

    print("Loading table...")
    df = load_table(file)
    df = clean_table(df)
    print("Table:", file, "\n", df,"\n")

    print("Calculating structural annotations...")
    primary_annotations, secondary_annotations = annotate(nlp, df)
    subject_column = key_column_detection(df, primary_annotations)
    
    # print("Primary annotations:", primary_annotations)
    # print("Secondary annotations:", secondary_annotations, "\n")

    print("Calculating semantic annotations...")
    entity_columns = analyze_table(es, df, primary_annotations,
        secondary_annotations, subject_column, searcher)
    
    print("\n\n\nCPA calculation...")
    top_properties, bonus_entities = \
    cpa_table(df, entity_columns, primary_annotations, secondary_annotations)
    # print("CPA:")
    # for property in top_properties:
    #     print(property.pid)

    print("\n\n\nCEA calculation...")
    top_entities = cea_table(entity_columns, bonus_entities)
    # print("CEA:")
    # for key in top_entities.keys():
    #     for ent in top_entities[key]:
    #         if ent != None:
    #             print(key, ent.qid)

    print("\n\n\nCTA calculation...")
    top_types = cta_table(top_entities, searcher)
    # for type in top_types:
    #     print(type.qid)

    print("Exporting all annotations...")
    cea_annotations = []
    cea_results_index = 0
    for i in range(len(entity_columns)):
        column = entity_columns[i].col
        eindex = 0
        for ent in top_entities[cea_results_index]:
            eindex += 1
            if ent != None:
                line = [str(eindex), str(column), PREFIX_ENT+ent.qid]
                cea_annotations.append(line)
            else: 
                line = [str(eindex), str(column), None]
                cea_annotations.append(line)
        cea_results_index += 1

    cpa_annotations = []
    pindex = 0
    for property in top_properties:
        pindex += 1
        line = [str(subject_column), pindex, PREFIX_PROP+property.pid]
        cpa_annotations.append(line)

    tindex = -1
    cta_annotations = []
    for type in top_types:
        tindex += 1
        col = entity_columns[tindex].col
        line = [str(col), PREFIX_ENT+type.qid]
        cta_annotations.append(line)

    # print(cea_annotations)
    # print(cpa_annotations)
    # print(cta_annotations)

    if es_index: es.transport.close()

    searcher.close()

    return (subject_column, 
            primary_annotations, 
            secondary_annotations, 
            cea_annotations, 
            cpa_annotations, 
            cta_annotations)
        

def write_to_files(filename, top_properties, top_entities, top_types):
    """Writes annotation results to csv files"""

    property_prefix = "http://www.wikidata.org/prop/direct/"
    entity_prefix = "http://www.wikidata.org/entity/"
    # cpa_file = "SemTab/R1_cpa_wd.csv"
    # cea_file = "SemTab/R1_cea_wd.csv"
    # cta_file = "SemTab/R1_cta_wd.csv"
    cpa_file = Config.R1_CPA_WD
    cea_file = Config.R1_CEA_WD
    cta_file = Config.R1_CTA_WD


    pindex = 0
    for property in top_properties:
        pindex += 1
        line = [filename, str(0), pindex,property_prefix+property.pid]
        append_to_csv(cpa_file, line)

    ent_keys = []
    for key in top_entities.keys():
        ent_keys.append(int(key))
        eindex = 0
        for ent in top_entities[key]:
            eindex += 1
            if ent != None:
                line = [filename, str(eindex), str(key), entity_prefix+ent.qid]
                append_to_csv(cea_file, line)

    tindex = -1
    for type in top_types:
        tindex += 1
        col = ent_keys[tindex]
        line = [filename, str(col), entity_prefix+type.qid]
        append_to_csv(cta_file, line)

    print("Results written to files!")
    return




# if __name__ == '__main__':
    
#     # try:
    #     nlp = spacy.load("en_core_web_sm")
    #     print("Model 'en_core_web_sm' is already downloaded.")
    # except OSError:
    #     print("Model 'en_core_web_sm' not found. Downloading...")
    #     spacy.cli.download("en_core_web_sm")
    #     nlp = spacy.load('en_core_web_sm')
#     input_dr = Config.INPUT_DIR_2023
#     # es = connect_elastic()


#     # es.transport.close()

#     #analyze_dataset_wd(input_dr, es, nlp)

#     for file in glob.glob(os.path.join(input_dr, '*.csv')):
#         filename = file.split("/")[-1].split(".")[0]
#         print("\nFile:", filename)
#         generate_annotations(file)
#         break
        
    
        
    
    