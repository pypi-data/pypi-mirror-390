from .preprocessing import load_entity_table
from .preprocessing import clean_table
from .annotation import annotate
import spacy
from .config import Config
from .data_load import connect_elastic
import glob
import os
from .utils import *
import pandas as pd
from .lookup import get_type_candidates
from .lookup import lookup_object_cells
from .lookup import get_topic_candidates
from .td_calculation import entity_table_td_calculation
from .cea_calculation import entity_table_cea
from .lookup import get_wd_topic_candidates


def analyze_entity_table(es, df, primary_annotations, secondary_annotations):
    """Analyzes table, finds candidates and scores"""

    #elasticsearch description analysis
    type_candidates = get_type_candidates(es, str(df['Prop0'].to_list()[0]))
    if type_candidates == []:
        return [], []
    topic_candidates = get_topic_candidates(es, type_candidates)

    #topic_candidates = get_wd_topic_candidates(str(df['Prop0'].to_list()[0]))
    #save_object(topic_candidates, "topic_candidates")
    #print([t.qid for t in topic_candidates])

    text_cells = {}
    literal_objects = []
    col_count = -1
    for col in df.columns[1:]:
        col_count += 1
        text_cells[col_count]=[]

    objects_row_prim_annotations = []
    objects_row_sec_annotations = []
    col_count = -1
    for prop in df.columns[1:]:
        col_count += 1
        cell = df[prop].to_list()[0].split(', ')
        for diff_ent in cell:
            text_cells[col_count].append(diff_ent)
            literal_objects.append(diff_ent)
            objects_row_prim_annotations.append(primary_annotations[col_count])
            objects_row_sec_annotations.append(secondary_annotations[col_count])

    object_candidates, all_candidates = lookup_object_cells(es, text_cells)
    #save_object(object_candidates, "obj_cands")
    # object_candidates = load_object("obj_cands")
    
    topic = entity_table_td_calculation(topic_candidates, literal_objects, objects_row_prim_annotations,
    objects_row_sec_annotations, all_candidates)
    #save_object(topic, "topic")
    # topic = load_object("topic")

    if topic == None:
        return [], []
    top_entities = entity_table_cea(topic, object_candidates)

    return topic, top_entities



def analyze_dataset_tfood(input_path, es, nlp):
    """Analyzes Wikidata datsets and calculates annotations"""

    td_columns = ['fileid','topic']
    td_file = Config.R1_TD_TFOOD_ENT

    for file in glob.glob(os.path.join(input_path, '*.csv')):

        filename = file.split("/")[-1].split(".")[0]
        files_analyzed = list(set(pd.read_csv(td_file,
                         header=None, names=td_columns)["fileid"].to_list()))
        print("\nFile:", filename)
        if filename in files_analyzed:
            print("File already analyzed: Skipping...")
            continue

        df = load_entity_table(file)
        df = clean_table(df)
        df = df.dropna(axis=1,how='all')

        primary_annotations, secondary_annotations = annotate(nlp, df)
        if df.columns[0] != "Prop0":
            print("Description missing: Skipping...\n")
            continue

        print("\nTable:", df,"\n")
        print("Primary annotations:", primary_annotations)
        print("Secondary annotations:", secondary_annotations, "\n")

        topic, top_entities = analyze_entity_table(es, df, primary_annotations, secondary_annotations)
        if top_entities == []:
            print("Topic missing: Skipping...\n")
            continue
        
        print("TD:", topic.qid)
        print("CEA:")
        for col in top_entities.keys():
            if top_entities[col] == [[]]: continue
            else:
                for qid in top_entities[col]:
                    print(col, qid)

        write_to_file(topic, top_entities, filename)

    return


def write_to_file(topic, top_entities, filename):
    """Writes annotation results to csv files"""

    entity_prefix = "http://www.wikidata.org/entity/"
    td_file = Config.R1_TD_TFOOD_ENT
    cea_file = Config.R1_CEA_TFOOD_ENT

    topic_line = [filename, entity_prefix+str(topic.qid)]
    append_to_csv(td_file, topic_line)
    #print(topic_line)

    for col in top_entities.keys():
        if top_entities[col] == [[]]: continue
        else: 
            if len(top_entities[col]) == 1:
                line = [filename,1,col,entity_prefix+top_entities[col][0]]
                #print(line)
                append_to_csv(cea_file, line)
            else:
                entity_ids = ''
                for qid in top_entities[col]:
                    if type(qid) != str:
                        continue
                    entity_ids += entity_prefix + qid + ','
                entity_ids = entity_ids[:-1]
                line = [filename,1,col,entity_ids]
                #print(line)
                append_to_csv(cea_file, line)

    return


if __name__ == '__main__':
    
    nlp = spacy.load('en_core_web_sm')
    input_dr = Config.INPUT_DIR_TFOOD_VAL_2023
    es = connect_elastic()

    analyze_dataset_tfood(input_dr, es, nlp)