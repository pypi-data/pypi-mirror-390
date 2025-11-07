from .context_score import text_similarity_score
from .context_score import number_similarity_score
from .entity_classes import CandidateProperty

def cpa_table(df, entity_columns, prim_annotations, sec_annotations):
    """Analyzes table to extract top properties and related entities"""

    #print("Calculating CPA...")
    top_properties = []
    bonus_entities = {}
    for col in range(len(entity_columns)):
        bonus_entities[col]=[]

    ne_column_count = 0
    for col in range(1, len(prim_annotations)):

        if prim_annotations[col] == "NE":  
            ne_column_count += 1 
            property_list, pids = \
            cpa_obj_property(df, entity_columns[0], entity_columns[ne_column_count])
        elif prim_annotations[col] == "L":
            property_list, pids = cpa_lit_property(df[df.keys()[col]].to_list(), 
            entity_columns[0], sec_annotations[col])
        
        top_property, s_entities_with_bonus, o_entities_with_bonus = \
        get_best_property(property_list, pids)
        top_properties.append(top_property)
        for entity in s_entities_with_bonus:
            if entity not in bonus_entities[0]:
                bonus_entities[0].append(entity)
        for entity in o_entities_with_bonus:
            if entity not in bonus_entities[ne_column_count]:
                bonus_entities[ne_column_count].append(entity)

    # for property in top_properties:
    #     print(property.pid, property.frequency, property.subjects)
    # print(bonus_entities)
    #print("CPA calculated!")

    return top_properties, bonus_entities


def cpa_text_property(test_list, subj_column):
    """Finds properties that correspond to objects that are literals and have the form of text
        and also appear in the table"""

    property_list, pids = [], []

    for row in range(len(test_list)):
        for cand in subj_column.cells[row].candidate_entities:
            for prop in cand.property_dict.keys():
                for obj in cand.property_dict[prop]:
                    if type(obj) == str:
                        score = text_similarity_score(obj, test_list[row], 0.97)
                        if score > 0:
                            property_list, pids = \
                            add_property_candidate(property_list, pids, prop, cand)
                    elif type(obj) == dict:
                        try:
                            obj_text = obj["text"]
                            score = text_similarity_score(obj_text, test_list[row], 0.97)
                            if score > 0:
                                property_list, pids = \
                                add_property_candidate(property_list, pids, prop, cand)
                        except:
                            pass


    return property_list, pids


def add_property_candidate(property_list, pids, prop, cand):
    """Adds property candidate to list of properties """

    if prop not in pids:
        pids.append(prop)
        cand_prop = CandidateProperty(prop)
        cand_prop.subjects.append(cand)
        #cand_prop.context_score = cand.candidate_score
        property_list.append(cand_prop)
    else:
        property_list[pids.index(prop)].frequency += 1
        #property_list[pids.index(prop)].frequency += cand.candidate_score
        property_list[pids.index(prop)].subjects.append(cand)
        if cand not in property_list[pids.index(prop)].subjects:
            property_list[pids.index(prop)].subjects.append(cand)

    return property_list, pids


def cpa_lit_property(test_list, subj_column, annotation):
    """Find properties that correspond to objects that are literals and have the form of numbers
        and also appear in the table"""
    
    property_list = []
    pids = []

    if (annotation == "INT") or (annotation == "PHONE") or (annotation == "FLOAT"):

        for row in range(len(test_list)):
            for cand in subj_column.cells[row].candidate_entities:
                for prop in cand.property_dict.keys():
                    for obj in cand.property_dict[prop]:
                        if type(obj) == str:
                            try:
                                obj_val = float(obj)
                                score = number_similarity_score(obj_val,float(test_list[row]))
                                if score>0:
                                    property_list, pids = \
                                    add_property_candidate(property_list, pids, prop, cand)
                            except:
                                pass
                            
                        elif type(obj) == dict:
                            try:
                                obj_val = float(obj["amount"])
                                score = number_similarity_score(obj_val,float(test_list[row]))
                                if score>0:
                                    property_list, pids = \
                                    add_property_candidate(property_list, pids, prop, cand)
                                    continue
                            except:
                                pass

                            try:
                                obj_val = float(obj["longitude"])
                                score = number_similarity_score(obj_val,float(test_list[row]))
                                if score>0:
                                    property_list, pids = \
                                    add_property_candidate(property_list, pids, prop, cand)
                                    continue
                            except:
                                pass

                            try:
                                obj_val = float(obj["latitude"])
                                score = number_similarity_score(obj_val,float(test_list[row]))
                                if score>0:
                                    property_list, pids = \
                                    add_property_candidate(property_list, pids, prop, cand)
                                    continue
                            except:
                                pass

                            try:
                                obj_val = float(obj["time"][1:5])
                                score = number_similarity_score(obj_val,float(test_list[row]))
                                if score>0:
                                    property_list, pids = \
                                    add_property_candidate(property_list, pids, prop, cand)
                                    continue
                            except:
                                pass


    elif (annotation == "DATE"):

        for row in range(len(test_list)):
            for cand in subj_column.cells[row].candidate_entities:
                for prop in cand.property_dict.keys():
                    for obj in cand.property_dict[prop]:
                        if type(obj) == dict:
                            try:
                                date_variations = [str(obj["time"])[1:11], str(obj["time"])[1:11].replace("-","/"),
                                str(obj["time"])[1:11].replace("-00","-01"), str(obj["time"])[1:11].replace("-01","-00"),
                                str(obj["time"])[1:11].replace("-00","/01"), str(obj["time"])[1:11].replace("-01","/00")]
                                
                                for obj_time in date_variations:
                                    score = text_similarity_score(obj_time, test_list[row], 0.95)
                                    if score > 0:
                                        property_list, pids = \
                                        add_property_candidate(property_list, pids, prop, cand)
                            except:
                                pass

    else:
        property_list, pids = cpa_text_property(test_list, subj_column)
                                 
    return property_list, pids


def cpa_obj_property(df, subj_column, test_column):
    """Finds properties that correspond to objects that are Wikidata entities 
       and also appear in the table"""
    
    property_list = []
    pids = []

    for row in range(len(df.index)):
        test_cand_ids = []
        test_cands = []
        for test_cand in test_column.cells[row].candidate_entities: 
            test_cand_ids.append(test_cand.qid)
            test_cands.append(test_cand)
        for subj_cand in subj_column.cells[row].candidate_entities:
            property_list, pids = check_for_obj_property(property_list,
            pids, subj_cand, test_cand_ids, test_cands)
            
    return property_list, pids


def get_best_property(property_list, pids):
    """Ranks properties by how many times they appear in the table"""

    high_score = -1
    top_property = None
    for prop in property_list:
        prop.total_score = prop.frequency + prop.context_score
        if prop.total_score > high_score:
            high_score = prop.total_score
            top_property = prop
    
    if top_property == None:
        return CandidateProperty("P1"), [], []
    s_entities_with_bonus = property_list[pids.index(top_property.pid)].subjects
    o_entities_with_bonus = property_list[pids.index(top_property.pid)].objects
    #print(s_entities_with_bonus, o_entities_with_bonus)

    return top_property, s_entities_with_bonus, o_entities_with_bonus



def check_for_obj_property(property_list, pids, subj_cand, test_cand_ids, test_cands):
    """Checks for additional candidates or assigns a bonus to existing, based on the context of the table"""

    subj_props = []
    for prop in subj_cand.property_dict.keys():
        #print(prop)
        subj_props.append(prop)

    for prop in subj_props:
        for subj_obj in subj_cand.property_dict[prop]:
            if type(subj_obj) == dict:
                try:
                    id_obj = subj_obj["id"]
                    if (id_obj in test_cand_ids):
                        if prop not in pids:
                            pids.append(prop)
                            cand_prop = CandidateProperty(prop)
                            cand_prop.context_score = subj_cand.candidate_score * \
                            test_cands[test_cand_ids.index(id_obj)].candidate_score
                            cand_prop.subjects.append(subj_cand)
                            cand_prop.objects.append(test_cands[test_cand_ids.index(id_obj)])
                            property_list.append(cand_prop)
                        else:
                            property_list[pids.index(prop)].frequency += 1
                            property_list[pids.index(prop)].context_score += \
                            subj_cand.candidate_score * test_cands[test_cand_ids.index(id_obj)].candidate_score
                            if subj_cand not in property_list[pids.index(prop)].subjects:
                                property_list[pids.index(prop)].subjects.append(subj_cand)
                            if test_cands[test_cand_ids.index(id_obj)] not in property_list[pids.index(prop)].objects:
                                property_list[pids.index(prop)].objects.append(test_cands[test_cand_ids.index(id_obj)])

                except:
                    pass

    return property_list, pids