from .context_score import get_wd_candidate_data

def entity_table_td_calculation(topic_candidates, literal_objects, objects_row_prim_annotations,
    objects_row_sec_annotations, all_candidates):
    """Finds highest scoring topic based on row context"""

    high_score = -1.0
    perfect_score = 1.0
    topic = None
    for topic_cand in topic_candidates:
        topic_cand = get_wd_candidate_data(topic_cand, literal_objects, objects_row_prim_annotations,
                                            objects_row_sec_annotations, all_candidates)
        
        if type(topic_cand.context_score) == float: 
            if topic_cand.context_score > high_score:
                high_score = topic_cand.context_score
                topic = topic_cand
                if high_score == perfect_score:
                    return topic

    return topic
    