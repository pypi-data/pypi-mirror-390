from .preprocessing import load_table
from .preprocessing import clean_table
from .annotation import annotate
import random
from itertools import permutations
import requests
import spacy
from .config import Config
from .data_load import connect_elastic
from elasticsearch.helpers import scan
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from Levenshtein import ratio
import requests
import numpy as np
from .entity_classes import CandidateEntity
from .entity_classes import CandidateTopic
from SPARQLWrapper import SPARQLWrapper, JSON

def get_candidates(es, entity_combos, discrete_words, searcher):
    """Entity lookup using Elasticsearch names index and different lookup strategies"""
    
    candidate_entities, candidate_entities_ids, lav_scores, bm25_scores = [], [], [], []
    #fuzz_perfect_score = 100.0 
    n_combos = len(entity_combos)
    no_result_counter = 0 #Counter for consecutive queries without results
    no_result_penalty_limit = Config.PENALTY_LIMIT #Limit of allowed consecutive queries without results
    candidates_limit = Config.CANDIDATE_LIMIT #Candidates limit for efficiency
    lav_threshold = True #Minimum lavenshtein distance threshold
    candidate_enrich_n = 10 #Allowed extra candidates from wikidata API
    names_index = Config.ELASTIC_INDEX #Elasticsearch index for wikidata
    
    for entity in entity_combos:
        #token_distance = (fuzz_perfect_score - fuzz.ratio(entity_combos[0], entity))/fuzz_perfect_score

        results = execute_fuzzy_keyword_query(es, entity, names_index)

        # Check consecutive queries without results to stop the process
        if results == []:
            no_result_counter += 1
            if (n_combos > 25) and  no_result_counter > no_result_penalty_limit:
                #print("Combinations are not performing well, skip!")
                break
        else:
            no_result_counter = 0
        
        if entity == entity_combos[0]:
            candidate_entities, candidate_entities_ids, lav_scores, bm25_scores = \
            get_candidates_from_results(candidate_entities, candidate_entities_ids,
            lav_scores, bm25_scores, entity_combos[0], results, lav_threshold)
        else:
            if len(candidate_entities)>20:
                candidate_entities, candidate_entities_ids, lav_scores, bm25_scores = \
            get_candidates_from_results(candidate_entities, candidate_entities_ids,
            lav_scores, bm25_scores, entity_combos[0], results, lav_threshold)
            else:
                candidate_entities, candidate_entities_ids, lav_scores, bm25_scores = \
            get_candidates_from_results(candidate_entities, candidate_entities_ids,
            lav_scores, bm25_scores, entity, results, False)


    if len(candidate_entities) < candidates_limit:
        lav_threshold = False

    if len(discrete_words) < 5:
        for word in ([entity_combos[0]]+discrete_words):
            results = execute_fuzzy_query(es, word)

            candidate_entities, candidate_entities_ids, lav_scores, bm25_scores = \
            get_candidates_from_results(candidate_entities, candidate_entities_ids,
            lav_scores, bm25_scores, entity_combos[0], results, lav_threshold)

    
    if candidate_entities_ids != []:

        # Sort candidates by score
        candidate_scores = get_candidate_scores(lav_scores, bm25_scores)
        candidate_entities_ids = [x for _,x in sorted(zip(candidate_scores,candidate_entities_ids))]
        candidate_entities = [x for _,x in sorted(zip(candidate_scores,candidate_entities))]
        candidate_scores.sort()

        # Limit candidates to a maximum allowed number
        n_initial_candidates = len(candidate_entities_ids)
        if n_initial_candidates > candidates_limit:
            candidate_entities_ids = candidate_entities_ids[n_initial_candidates-candidates_limit:]
            candidate_entities = candidate_entities[n_initial_candidates-candidates_limit:]
            candidate_scores = candidate_scores[n_initial_candidates-candidates_limit:]

    else:
        candidate_scores = []

    if len(candidate_entities_ids) > 11:
        if (candidate_scores[10] == 1.0) or (candidate_scores[10] == 0.0):
            extra_entities, extra_titles = searcher.query_name([entity_combos[0]])
            if len(extra_entities) > candidate_enrich_n:
                search_number = candidate_enrich_n
            else:
                search_number = len(extra_entities)
            for entity_num in range(search_number):
                if extra_entities[entity_num] not in candidate_entities_ids:
                    candidate_entities_ids.append(extra_entities[entity_num])
                    candidate_scores.append(ratio(entity_combos[0], extra_titles[entity_num]))
    else:
        extra_entities, extra_titles = searcher.query_name([entity_combos[0]])
        for entity_num in range(len(extra_entities)):
            if extra_entities[entity_num] not in candidate_entities_ids:
                candidate_entities_ids.append(extra_entities[entity_num])
                candidate_scores.append(ratio(entity_combos[0], extra_titles[entity_num]))
           
    return candidate_entities_ids, candidate_scores


def get_candidates_wd(entity_combos, discrete_words, searcher):
    """Entity lookup using Wikidata API and different lookup strategies"""
    
    candidate_entities, candidate_entities_ids, candidate_scores = [], [], []
    n_combos = len(entity_combos)
    no_result_counter = 0 #Counter for consecutive queries without results
    no_result_penalty_limit = Config.PENALTY_LIMIT #Limit of allowed consecutive queries without results
    candidates_limit = Config.CANDIDATE_LIMIT #Candidates limit for efficiency

    #Query Wikidata API using combos
    for combo in entity_combos:
        entities, titles = searcher.query_name(combo)

        if entities == []:
            no_result_counter += 1
            if (n_combos > 25) and  no_result_counter > no_result_penalty_limit:
                #print("Combinations are not performing well, skip!")
                break
        else:
            no_result_counter = 0

        for i in range(len(entities)):
            if entities[i] not in candidate_entities_ids:
                candidate_entities_ids.append(entities[i])
                candidate_scores.append(ratio(entity_combos[0], titles[i]))
            else:
                pos = candidate_entities_ids.index(entities[i])
                candidate_scores[pos] = max(candidate_scores[pos], ratio(entity_combos[0], titles[i]))

    #Query Wikidata API using discrete words. 
    # If it's 1, we don't need to query again, it has been queries.
    # If it's 5 or more, single words are less relevant and it would become less efficient.
    if 1 < len(discrete_words) < 5:
        for word in discrete_words:
            entities, titles = searcher.query_name(word)

            for i in range(len(entities)):
                if entities[i] not in candidate_entities_ids:
                    candidate_entities_ids.append(entities[i])
                    candidate_scores.append(ratio(entity_combos[0], titles[i]))
                else:
                    pos = candidate_entities_ids.index(entities[i])
                    candidate_scores[pos] = max(candidate_scores[pos], ratio(entity_combos[0], titles[i]))

    assert len(candidate_entities_ids) == len(candidate_scores)

    # Sort candidates by score
    candidate_entities_ids = [x for _,x in sorted(zip(candidate_scores,candidate_entities_ids))]
    candidate_scores.sort()

     # Limit candidates to a maximum allowed number
    n_initial_candidates = len(candidate_entities_ids)
    if n_initial_candidates > candidates_limit:
        candidate_entities_ids = candidate_entities_ids[n_initial_candidates-candidates_limit:]
        candidate_scores = candidate_scores[n_initial_candidates-candidates_limit:]

    return candidate_entities_ids, candidate_scores



def get_entity_combos (entity: str):
    """Clean and get all combinations of words contained in the cell to be analyzed"""

    combos = [entity]
    words = [entity]
    
    n_words = len(entity.strip().split(" "))
    if n_words == 1:
        return combos, words
    
    # Entity tokenization and stopword strip
    words = word_tokenize(entity)
    words_without_stopwords = [word for word in words if word.lower() not in stopwords.words()]
    for word in words_without_stopwords:
        if len(word) == 1:
            words_without_stopwords.pop(words_without_stopwords.index(word))

    if len(words_without_stopwords) < 6:
        combos = calculate_permutations(entity, words_without_stopwords)
        seen = set()
        unique_combos = [x for x in combos if not (x in seen or seen.add(x))]
    else:
        unique_combos = [entity]
    # print("Words that the cell contains:", words_without_stopwords)
    # print("Combinations of words:", unique_combos)
    
    return unique_combos, words_without_stopwords



def calculate_permutations(entity, sentence):
    """Mix words of a sentence and return possible combinations"""
    
    base_entity = [entity]
    extra_combinations = []
 
    # Store all possible permutations
    # of words in this list
    permute = permutations(sentence)
 
    # Iterate over all permutations
    for i in permute:
       
        tmp = ' '.join(i)
        if tmp not in base_entity:
            extra_combinations.append(tmp)

    random.shuffle(extra_combinations)
    combos = base_entity + extra_combinations
        
    return combos



def execute_fuzzy_keyword_query(es, term, els_index):
    """Fuzzy keyword elasticsearch query"""

    fuzzy_query = {
        "track_scores": True,
        "query": {
                "fuzzy" : {
                    "object.keyword": {
                    "value":term,
                    "fuzziness": "AUTO",
                    "max_expansions": 100,
                    "prefix_length": 0,
                    "transpositions": True,
                    # "rewrite": "constant_score"
                        }
                    }
                } 
        }  

    rel = scan(client=es,             
        query=fuzzy_query,                                     
        scroll='1m',
        index=els_index,
        raise_on_error=True,
        preserve_order=False,
        clear_scroll=True,
        request_timeout=60)

    results = list(rel)
    #print(len(results))

    return results


def execute_instance_query(es, term):
    """Triple object query (used for retrieving instances (P31))"""

    instance_query = {
        "term": {
            "object.keyword": term,
        }
    }

    rel = es.search(    
        index="wd_2023",
        query=instance_query,
        size=10000,
        explain= True                                   
        )

    results = list(rel["hits"]["hits"])

    return results


def execute_desc_query(es, term):
    """Triple object fuzzy query (mostly used for entity descriptions)"""

    instance_query = {
        "fuzzy" : {
            "object.keyword": {
            "value":term,
            "fuzziness": "AUTO",
            "max_expansions": 100,
            "prefix_length": 0,
            "transpositions": True,
            # "rewrite": "constant_score"
                }
            }
        } 
    

    rel = es.search(    
        index="wd_2023",
        query=instance_query,
        size=10000,
        explain= True                                   
        )

    results = list(rel["hits"]["hits"])

    return results


def execute_fuzzy_query(es, term):
    """Entity fuzzy query for names search"""

    fuzzy_query = {
        "fuzzy": {
            "object": {
                "value": term,
                "fuzziness": "AUTO",
                "max_expansions": 100,
                }
            }
        }

    rel = es.search(    
        index="wd_names_2023",
        query=fuzzy_query,
        size=1000,
        explain= True                                   
        )

    results = list(rel["hits"]["hits"])

    return results



def get_candidates_from_results(candidate_entities, candidate_entities_ids,
 lav_scores, bm25_scores, entity, results, threshold):
    """Extract candidates from query results"""

    # Score thresholds
    if threshold == True:
        bm25_threshold = 9
        lav_threshold = 0.6
    else: 
        bm25_threshold = 4
        lav_threshold = -5

    # Storage of results' IDs and scores
    for result in results:
        candidate_entity = result['_source']['object']
        label_type = int(result['_source']['property'])
        candidate_entity_id = 'Q' + str(result['_source']['subject'])
        lav_score = ratio(candidate_entity, entity)
        if label_type == 0: lav_score += 0.1
        bm25_score = result['_score']
        #print(candidate_entity_id, candidate_entity, lav_score, bm25_score)

        if (candidate_entity_id not in candidate_entities_ids) \
        and bm25_score > bm25_threshold \
        and lav_score > lav_threshold:
            candidate_entities.append(candidate_entity)
            candidate_entities_ids.append(candidate_entity_id)
            lav_scores.append(lav_score)
            bm25_scores.append(bm25_score)
            # print(candidate_entity_id, candidate_entity, lav_score, bm25_score)
            

        elif candidate_entity_id in candidate_entities_ids:
            pos = candidate_entities_ids.index(candidate_entity_id)
            if lav_score > lav_scores[pos]:
                lav_scores[pos] = lav_score

            if bm25_score > bm25_scores[pos]:
                bm25_scores[pos] = bm25_score

    return candidate_entities, candidate_entities_ids, lav_scores, bm25_scores


def get_candidate_scores(lav_scores, bm25_scores):
    """Calculate candidate scores (Lavenstein distance + BM25 scores) and normalize them"""

    max_lav_scores = max(lav_scores)
    min_lav_scores = min(lav_scores)
    lav_scores = np.array(lav_scores)

    if max_lav_scores != min_lav_scores:
        lav_scores_norm = (lav_scores - min_lav_scores)/(max_lav_scores - min_lav_scores)
    else:
        lav_scores_norm = lav_scores
    
    
    max_bm25_scores = max(bm25_scores)
    min_bm25_scores = min(bm25_scores)
    bm25_scores = np.array(bm25_scores)

    if max_bm25_scores != min_bm25_scores:
        bm25_scores_norm = (bm25_scores - min_bm25_scores)/(max_bm25_scores - min_bm25_scores)
    else: 
        bm25_scores_norm = bm25_scores / max_bm25_scores

    # Literal score calculation for each candidate
    w1 = 0.75
    w2 = 0.25
    candidate_scores = w1*lav_scores_norm + w2*bm25_scores_norm
    candidate_scores = candidate_scores.tolist()

    # for i in range(len(lav_scores)):
    #     candidate_scores[i] = weighted_lav_scores[i] + weighted_bm25_scores[i]

    return candidate_scores


def search_wd(search_string):
    """Searches Wikidata for extra candidates"""

    url = "https://www.wikidata.org/w/api.php"

    params = {
        "action": "wbsearchentities",
        "format": "json",
        "language": "en",
        "search": search_string
    }

    response = requests.get(url, params=params).json()

    entities = []
    titles = []
    for result in response["search"]:
        entity_id = result["id"]
        try:
            titles.append(result["display"]["label"]["value"])
            entities.append(entity_id)
        except:
            pass

    return entities, titles


def get_type_candidates(es, description):
    """Get candidates given their description (used for tfood tables)"""

    type_candidates = []
    description_id = 1
    results = execute_desc_query(es, description)
    for result in results:
        if (int(result['_source']['property']) == description_id) \
        and (result['_source']['subject'] not in type_candidates):
            type_candidates.append(result['_source']['subject'])

    return type_candidates


def get_topic_candidates(es, type_candidates):
    """Get entities that are instance of a ID (used for tfood tables)"""

    candidate_topics = []
    instance_pids = [31, 279]
    topics_seen = []
    for type in type_candidates:
        results = execute_instance_query(es, "Q"+str(type))
        for result in results:
            if int(result['_source']['property']) in instance_pids \
            and (str(result['_source']['subject']) not in topics_seen):
                cand_topic = CandidateTopic("Q"+str(result['_source']['subject']))
                candidate_topics.append(cand_topic)
                topics_seen.append(str(result['_source']['subject']))

    return candidate_topics


def lookup_object_cells(es, text_cells):
    """Lookup text cells that may contain multiple entities (used for tfood tables)"""

    obj_candidates = text_cells
    all_cands = []

    for col in text_cells.keys():
        ent_count = -1
        for ent in text_cells[col]:         
            ent_count += 1
            entity_combos, discrete_words = get_entity_combos(ent)
            candidate_entities_ids, candidate_scores = get_candidates(es, entity_combos, discrete_words)
            obj_candidates[col][ent_count] = candidate_entities_ids
            for n_cand in range(len(candidate_entities_ids)):
                all_cands.append(candidate_entities_ids[n_cand])

    return obj_candidates, all_cands


def get_wd_topic_candidates(description):
    """ Wikidata query (as an alternative to elasticsearch) to get instances of entities 
        with a specific descriptions"""

    endpoint_url = "https://query.wikidata.org/sparql"
    sparql = SPARQLWrapper(endpoint_url)
    topics_seen = []
    candidate_topics = []
    
    language = 'en'
    instance_query = f"""
    SELECT ?s2 WHERE {{
        {{
            ?s <http://schema.org/description> '{description}'@{language}.
            ?s2 <http://www.wikidata.org/prop/direct/P31> ?s.
        }}
        UNION
        {{
            ?s <http://schema.org/description> '{description}'@{language}.
            ?s2 <http://www.wikidata.org/prop/direct/P279> ?s.
        }}
    }}
    """

    sparql.setQuery(instance_query)
    sparql.setReturnFormat(JSON)

    results = sparql.query().convert()
    for result in results['results']['bindings']:
        qid = result['s2']['value'].split('/')[-1]
        if qid not in topics_seen:
            topics_seen.append(qid)
            cand_topic = CandidateTopic(qid)
            candidate_topics.append(cand_topic)

    return candidate_topics
