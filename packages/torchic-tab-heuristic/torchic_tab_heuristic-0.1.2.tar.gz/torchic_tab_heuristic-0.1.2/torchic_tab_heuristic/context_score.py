import requests
import time
from .entity_classes import CandidateEntity
from Levenshtein import ratio

NUMBER_ANNOTATIONS = ["INT", "FLOAT", "COORDS", "PHONE"]
TYPE_PROPERTIES = ["P31", "P279"]

def get_wd_candidate_data(cand_graph, cell_row, prim_annotations, sec_annotations, candidate_objects, searcher, is_subject):
    """Gets subgraph of candidates and their score based on context similarity with the row in the table"""

    results = searcher.query_qid(cand_graph.qid, False)
    for key in results.keys():
        if key == "missing":
            return cand_graph

    row_scores = [0.0]*len(cell_row)

    # Print all properties and objects of the entity
    for property_id, property_value in results["claims"].items():
        for claim in property_value:

            try:
                _object, row_scores = extract_object_value(claim["mainsnak"]["datavalue"]["value"],
                          cell_row, row_scores, prim_annotations, sec_annotations, 
                          candidate_objects, property_id, searcher, is_subject)

                if _object != None:
                    cand_graph.property_dict = add_object_to_property_dict(cand_graph.property_dict, property_id, _object)

            except Exception as e: 
                pass

    context_score = sum(row_scores)/len(row_scores)
    if context_score < 0.1:
        context_score = 0.0001
    cand_graph.context_score = context_score
    # for prop in cand_graph.property_dict.keys():
    #     print(prop, cand_graph.property_dict[prop])
    return cand_graph

                
          
def extract_object_value(object_value, cell_row, row_scores, prim_annotations,
                          sec_annotations, candidate_objects, property_id, searcher, is_subject):
    """Analyzes objects of candidates subgraph, according to their datatype and compares them with the context of the row  """

    if type(object_value) == str and is_subject:
        if ("NE" in prim_annotations):
            row_scores, score_change = calculate_text_similarity(cell_row, row_scores,
                prim_annotations, object_value)
            if score_change:
                return object_value, row_scores

        try:
            int_val = int(object_value)
            if ("INT" in sec_annotations):
                row_scores, score_change = calculate_number_similarity(cell_row, row_scores,
                    sec_annotations, int_val)
                if score_change:
                    return({"amount": int_val}, row_scores) 
        except:
            pass

        return None, row_scores

    keys_list = []
    for key in object_value.keys():
        keys_list.append(key)
    
    if "id" in keys_list: 
        if ("NE" in prim_annotations) and is_subject:
            if object_value["id"] in candidate_objects:
                names_list = extract_names_and_aliases(object_value["id"], searcher)
                for name in names_list:
                    row_scores, score_change = calculate_text_similarity(cell_row, row_scores,
                    prim_annotations, name)
                return({"id": object_value["id"]}, row_scores)
        
        if property_id in TYPE_PROPERTIES:
            return({"id": object_value["id"]}, row_scores)

        return(None, row_scores)

    elif "amount" in keys_list and is_subject:
        for anno in NUMBER_ANNOTATIONS:
            if anno in sec_annotations:
                row_scores, score_change = calculate_number_similarity(cell_row, row_scores,
                sec_annotations, float(object_value["amount"]))
                if score_change:
                    return({"amount": object_value["amount"]}, row_scores)

        return(None, row_scores)

    elif "text" in keys_list and is_subject: 
        if ("NE" in prim_annotations):
            row_scores, score_change = calculate_text_similarity(cell_row, row_scores,
             prim_annotations, object_value["text"])
            if score_change:
                return(object_value["text"], row_scores)
        
        return(None, row_scores)

    elif "time" in keys_list and is_subject: 
        if ("DATE" in sec_annotations):
            date_variations = [str(object_value["time"])[1:11], str(object_value["time"])[1:11].replace("-","/"),
            str(object_value["time"])[1:11].replace("-00","-01"), str(object_value["time"])[1:11].replace("-01","-00"),
            str(object_value["time"])[1:11].replace("-00","/01"), str(object_value["time"])[1:11].replace("-01","/00")]

            for date in date_variations:
                row_scores, score_change = calculate_date_similarity(cell_row, row_scores,
                    sec_annotations, date)
                if score_change:
                    return({"time": object_value["time"]}, row_scores)

        if ("INT" in sec_annotations):
            row_scores, score_change = calculate_number_similarity(cell_row, row_scores,
                sec_annotations, float(object_value["time"][1:5]))
            if score_change:
                return({"amount": int(object_value["time"][1:5])}, row_scores)

        return(None, row_scores)


    elif "longitude" in keys_list and is_subject: 

        for anno in NUMBER_ANNOTATIONS:
            if anno in sec_annotations:
                row_scores, score_change = calculate_number_similarity(cell_row, row_scores,
                    sec_annotations, float(object_value["longitude"]))
                if score_change:
                    return({"longitude": object_value["longitude"]}, row_scores)
                row_scores, score_change = calculate_number_similarity(cell_row, row_scores,
                    sec_annotations, float(object_value["latitude"]))
                if score_change:
                    return({"longitude": object_value["longitude"]}, row_scores)

        return(None, row_scores)
    
    return (None, row_scores)
     


def calculate_number_similarity(cell_row, row_scores, sec_annotations, cand_object):
    """Calculates number similarity between two numbers"""

    score_change = False

    for i in range(len(cell_row)):

        if (sec_annotations[i] in NUMBER_ANNOTATIONS):
            score = number_similarity_score(float(cell_row[i]), cand_object)
            if (score > 0) and (score >= float(row_scores[i])): 
                row_scores[i] = score
                score_change = True

    return row_scores, score_change


def number_similarity_score(value1, value2):
    """Assigns number similarity scores """

    threshold = 0.97

    if value1 == 0.0 or value2 == 0.0:
        score = 1 - abs(value1 - value2)
        if score >= threshold: return score
        else: return 0.0
    
    score = 1.0 - ((abs(value1-value2)/max(abs(value1),abs(value2))))
    if score < threshold: return 0.0
    return score


def calculate_text_similarity(cell_row, row_scores, prim_annotations, cand_object):
    """Calculates text similarity between two texts """

    score_change = False
    threshold = 0.97
    for i in range(len(cell_row)):

        if (prim_annotations[i] == "NE"):
            score = text_similarity_score(cell_row[i], cand_object, threshold)
            if (score > 0) and (score >= row_scores[i]): 
                row_scores[i] = score
                score_change = True

    return row_scores, score_change
    

def text_similarity_score(value1, value2, threshold):
    """Assigns text similarity score using levenshtein distance"""

    score = ratio(value1, value2)
    if score < threshold: return 0.0
    return score


def calculate_date_similarity(cell_row, row_scores, sec_annotations, cand_object):
    """Calculates date similarity between two dates """

    score_change = False
    threshold = 0.9
    for i in range(len(cell_row)):
        if (sec_annotations[i] == "DATE"):
            score = text_similarity_score(cell_row[i], cand_object, threshold)
            if (score > 0) and (score >= row_scores[i]): 
                row_scores[i] = score
                score_change = True

    return row_scores, score_change


def extract_names_and_aliases(qid, searcher):
    """Extracts names and aliases from Wikidata IDs"""

    obj_results = searcher.query_qid(qid, names_search=True)
    labels = obj_results['labels']
    aliases = obj_results['aliases']
    names_list = []

    for key in labels.keys():
        if labels[key]["value"] not in names_list:
            names_list.append(labels[key]["value"])
    for key in aliases.keys():
        for pair in aliases[key]:
            if pair["value"] not in names_list:
                names_list.append(pair["value"])

    return names_list


def query_wd_api(qid, names_search):
    """Wikidata API request for names and aliases of IDs"""

    # Wikidata API endpoint
    endpoint = "https://www.wikidata.org/w/api.php"

    # Parameters for the API request
    params = {
        "action": "wbgetentities",
        "ids": qid,
        "format": "json"
    }

    if names_search :
        params = {
            "action": "wbgetentities",
            "ids": qid,
            "props": "labels|aliases",
            "format": "json"
        }

    # Send the API request and get the response
    try:
        response = requests.get(endpoint, params=params).json()
    except:
        time.sleep(2)
        entity = query_wd_api(qid, names_search)
        return entity

    # Get the entity corresponding to the Wikidata ID
    entity = response["entities"][qid]

    return entity


def add_object_to_property_dict(property_dict, property_path, _object):
    """Adds names and aliases to candidate subgraph"""

    if property_path not in property_dict:
        if (type(_object) == str) or (type(_object) == dict):
            property_dict[property_path] = [_object]
        else:
            property_dict[property_path] = _object
    else:
        if type(_object) == list:
            for obj in _object:
                if obj not in property_dict[property_path]:
                    property_dict[property_path].append(obj)
        else:
            if _object not in property_dict[property_path]:
                property_dict[property_path].append(_object)

    return property_dict


def scan_for_references(cand_graph, claim, property_id):
    """Scans wikidata API json results to find references"""

    try:
        extra_refs = claim["references"][0]["snaks"]
        ref_props = [key for key in extra_refs.keys()]
        for property in ref_props:
            ref_obj = extract_object_value(extra_refs[property][0]["datavalue"]["value"])
            property_path = property_id+" --> "+property
            add_object_to_property_dict(cand_graph, property_path, ref_obj)

            # print("Properties:", property_id, "-->", property,
            # "Object:", ref_obj)

    except:
        pass


def scan_for_bn_references(cand_graph, claim, property_id, property_id_2):
    """Scans wikidata API json results to find references of 'blank nodes'"""

    try:
        extra_refs = claim["references"][0]["snaks"]
        ref_props = [key for key in extra_refs.keys()]
        for property in ref_props:
            ref_obj = extract_object_value(extra_refs[property][0]["datavalue"]["value"])
            property_path = property_id+" --> "+property_id_2+" --> "+property
            add_object_to_property_dict(cand_graph, property_path, ref_obj)
            # print("Properties:", property_id, "-->", property_id_2, 
            # "-->", property,
            # "Object:", ref_obj)

    except:
        pass


def scan_for_bn(cand_graph, claim, property_id):
    """Scans wikidata API json results to find 'blank nodes'"""

    blank_node = claim["qualifiers"]
    property_id_2 = [key for key in blank_node.keys()][0]
    _object2 = extract_object_value(blank_node[property_id_2][0]["datavalue"]["value"])
    print("Properties:", property_id, "-->", property_id_2,
    "Object:", _object2)
    scan_for_bn_references(cand_graph, claim, property_id, property_id_2)

