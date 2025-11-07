from .entity_classes import CandidateType

def cea_table(entity_columns, bonus_entities):
    """Analyzes entities that have a bonus score from CPA task"""
    
    bonus_types = find_bonus_types(bonus_entities)

    top_entities = {}

    for column in range(len(entity_columns)):
        top_entities[column]=[]
        for cell in entity_columns[column].cells:
            top_entities[column].append(
            get_top_entity(bonus_entities[column], bonus_types[column], cell.candidate_entities))

    return top_entities


def find_bonus_types(bonus_entities):
    """Assigns a bonus to column types that are associated with entities that have a bonus score"""

    bonus_types = {}
    for col in range(len(bonus_entities)):
        bonus_types[col]=[]

    for col in bonus_entities.keys():
        for ent in bonus_entities[col]:
            for prop in ent.property_dict:
                if prop == "P31":
                    for _obj in ent.property_dict[prop]:
                        try:
                            type = _obj["id"]
                            for bonus_type in bonus_types[col]:
                                if type == bonus_type.qid:
                                    continue
                            new_type = CandidateType(type, 0)
                            bonus_types[col].append(new_type)
                        except:
                            pass

    return bonus_types

def get_top_entity(bonus_ents, bonus_types, candidates):
    """Gets top candidate entity for each cell"""

    top_entity = None
    high_score = -1

    bonus_ent_ids, bonus_type_ids = [], []
    for ent in bonus_ents:
        bonus_ent_ids.append(ent.qid)
    for type in bonus_types:
        bonus_type_ids.append(type.qid)

    for cand in candidates:

        # for prop in cand.property_dict:
        #     if prop == "P31":
        #         for _obj in cand.property_dict[prop]:
        #             if _obj["id"] in bonus_type_ids:
        #                 cand.candidate_score += 0.5
        #                 break

        if cand.qid in bonus_ent_ids:
            cand.candidate_score += 1
        if cand.candidate_score >= high_score:
            high_score = cand.candidate_score
            top_entity = cand

    return top_entity


def entity_table_cea(topic, object_candidates):
    """Gets top entities for tfood 'entity' tables"""

    top_entities = object_candidates

    topic_objects = []
    for prop in topic.property_dict.keys():
        for obj in topic.property_dict[prop]:
            if type(obj) == dict:
                try:
                    obj_id = obj["id"]
                    topic_objects.append(obj_id)
                except:
                    pass

    for col in object_candidates.keys():
        cand_lists_count = -1
        for cand_id_list in object_candidates[col]:
            cand_lists_count += 1
            for cand_id in cand_id_list:
                if cand_id in topic_objects:
                    top_entities[col][cand_lists_count] = cand_id
                    break
                else:
                    top_entities[col][cand_lists_count] = []


    return top_entities
    
