from .entity_classes import CandidateType
from .context_score import query_wd_api
import random

def cta_table(top_entities, searcher):
    """Analyzes table to detect top types based on CEA entities"""

    top_types = [0]* len(top_entities)

    candidate_types_ids = [ [] for i in range(len(top_entities))]
    candidate_types = {}
    for col in range(len(top_entities)):
        candidate_types[col]=[]
    

    for col in top_entities.keys():
        for ent in top_entities[col]:
            if ent!= None:
                for prop in ent.property_dict:
                    if prop == "P31":
                        for obj in ent.property_dict[prop]:
                            qid = obj["id"]
                            if qid not in candidate_types_ids[col]:
                                cand_type = CandidateType(qid, 0)
                                candidate_types_ids[col].append(qid)
                                candidate_types[col].append(cand_type)
                            else:
                                candidate_types[col][candidate_types_ids[col].index(qid)].frequency += 1
            
    for col in candidate_types.keys():
        if (candidate_types[col]) == []:
            top_types[int(col)] = CandidateType("Q35120", 0)
            continue
        high_score = -1
        high_score_list = []
        for cand in candidate_types[col]:
            if cand.frequency > high_score:
                high_score = cand.frequency
                high_score_list = [cand]
            elif cand.frequency == high_score:
                high_score_list.append(cand)
            
        if len(high_score_list) == 1:
            #print("Type found:", high_score_list[0].qid, high_score)
            top_types[int(col)] = high_score_list[0]
        else:
            top_types = calculate_hierarchy(candidate_types[col], int(col), top_types, searcher)          

    return top_types

 
def calculate_hierarchy(cand_list, col, top_types, searcher):
    """Finds hierarchy (narrower and wider terms) and frequency of candidate types"""

    query_res_dict = {}
    cand_list_ids = []
    for cand in cand_list:
        cand_list_ids.append(cand.qid)

    for cand in cand_list:
        query_res1 = searcher.query_qid(cand.qid, False)
        query_res_dict[cand.qid] = query_res1

        for property_id, property_value in query_res1["claims"].items():
            if property_id == "P279":
                for claim in property_value:
                    try:
                        _object = claim["mainsnak"]["datavalue"]["value"]["id"]
                    except:
                        pass
                    if _object not in cand_list_ids:
                        cand_type = CandidateType(_object, 1)
                        cand_list.append(cand_type)
                        cand_list_ids.append(_object)

                        #Extending the search to find more specific types
                        # query_res2 = searcher.query_qid(_object, False)
                        # query_res_dict[_object] = query_res2
                        # for property_id, property_value in query_res2["claims"].items():
                        #     if property_id == "P279":
                        #         for claim in property_value:
                        #             try:
                        #                 _object = claim["mainsnak"]["datavalue"]["value"]["id"]
                        #             except:
                        #                 pass
                        #             if _object not in cand_list_ids:
                        #                 cand_type = CandidateType(_object, 2)
                        #                 cand_list.append(cand_type)
                        #                 cand_list_ids.append(_object)

                        #             else:
                        #                 cand_list[cand_list_ids.index(_object)].frequency += 1
                        #                 cand_list[cand_list_ids.index(_object)].level += 2


                    else:
                        cand_list[cand_list_ids.index(_object)].frequency += 1
                        cand_list[cand_list_ids.index(_object)].level += 1

    # Decide on top type based on high frequency and low hierarchy (narrowest entity possible)
    high_score = -100
    final_cands = []
    for cand in cand_list:
        score = cand.frequency - cand.level
        if score > high_score:
            high_score = score
            final_cands = [cand]
        elif score == high_score:
            final_cands.append(cand)

    if len(final_cands) == 1:
        top_types[col] = final_cands[0]
        return top_types

    # If there is no winner, choose based on frequency alone
    else:
        high_score = -1
        final_cands2 = []
        for cand in final_cands:
            score = cand.frequency
            if score > high_score:
                high_score = score
                final_cands2 = [cand]
            elif score == high_score:
                final_cands2.append(cand)

        if len(final_cands2) == 1:
            top_types[col] = final_cands2[0]
            return top_types

        # If again there is no winner, choose based on level alone   
        else:
            high_score = 100
            final_cands3 = []
            for cand in final_cands:
                score = cand.level
                if score < high_score:
                    high_score = score
                    final_cands3 = [cand]
                elif score == high_score:
                    final_cands3.append(cand)

            if len(final_cands3) == 1:
                top_types[col] = final_cands3[0]
                return top_types

            # If again there is no winner, find the relationships between candidates to see which is more specific
            else:
                top_types = find_most_specific(final_cands, col, top_types, searcher, query_res_dict)


    return top_types


def find_most_specific(cand_list, col, top_types, searcher, query_res_dict):
    """Finds the most specific type by checking the hierarchy of the candidates"""

    original_final_cands = cand_list

    for cand in cand_list:
        query_res1 = query_res_dict[cand.qid]
        for property_id, property_value in query_res1["claims"].items():
            if property_id == "P279":
                for claim in property_value:
                    try:
                        _object = claim["mainsnak"]["datavalue"]["value"]["id"]
                    except:
                        continue
                    if _object in cand_list:
                        cand_list.pop(cand_list.index(_object))
                        continue
                    # else:
                    #     query_res2 = searcher.query_qid(_object, False)
                    
                    # for property_id, property_value in query_res2["claims"].items():
                    #     if property_id == "P279":
                    #         for claim in property_value:
                    #             try:
                    #                 _object = claim["mainsnak"]["datavalue"]["value"]["id"]
                    #             except:
                    #                 pass
                    #             if _object in cand_list:
                    #                 cand_list.pop(cand_list.index(_object))


    if len(cand_list) == 1:
        top_types[col] = cand_list[0]

    # If again there is no winner, choose a random type out of the best scoring ones
    elif len(cand_list) == 0:
        top_types[col] = original_final_cands[random.randint(0,len(original_final_cands)-1)]
            
    else:
        top_types[col] = cand_list[random.randint(0,len(cand_list)-1)]
    
    return top_types


# def find_distance_to_thing(cand_list):
#     #print("hey")

#     distances = [1]*len(cand_list)

#     index = -1
#     for cand in cand_list:
#         found = False
#         index += 1
#         tree = [cand.qid]
#         stack = []
#         to_delete_from_tree = []
#         while (found == False):
#             for qid in tree:
#                 if found == True:
#                     break
#                 query_res = query_wd_api(qid, False)
#                 for property_id, property_value in query_res["claims"].items():
#                     if found == True:
#                         break
#                     if property_id == "P279":
#                         for claim in property_value:
#                             try:
#                                 _object = claim["mainsnak"]["datavalue"]["value"]["id"]
#                             except:
#                                 pass
#                             if _object == "Q35120":
#                                 found = True
#                                 break
#                             elif _object not in tree:
#                                 stack.append(_object)
#                 to_delete_from_tree.append(qid)

#             for item in stack:
#                 tree.append(item)
#             stack = []
#             distances[index] += 1
#             for qid in to_delete_from_tree:
#                 del tree[tree.index(qid)]
#             to_delete_from_tree = []


#     high_score = 0
#     top_scoring = []
#     for i in range(len(cand_list)):
#         if distances[i] > high_score:
#             high_score = distances[i]
#             top_scoring = [cand_list[i]]
#         elif distances[i] == high_score:
#             top_scoring .append(cand_list[i])

#     return top_scoring



    