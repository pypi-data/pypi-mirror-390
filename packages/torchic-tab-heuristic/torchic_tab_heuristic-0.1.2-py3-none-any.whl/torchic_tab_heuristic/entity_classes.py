class EntityColumn:
    """Class that represents a column of a table"""

    def __init__(self, col):
        self.col = col
        self.cells = []

class EntityCell:
    """Class that represents a cell of a table"""

    def __init__(self, name, row, col):
        self.name = name
        self.row = row
        self.col = col
        self.candidate_entities = []

class CandidateEntity:
    """Class that represents a candidate entity of a cell"""

    def __init__(self, qid):
        self.qid = qid
        self.property_dict = {}
        self.literal_score = 0
        self.context_score = 0
        self.candidate_score = 0

class CandidateTopic:
    """Class that represents a candidate topic of a table"""

    def __init__(self, qid):
        self.qid = qid
        self.property_dict = {}
        self.context_score = {}


class CandidateProperty:
    """Class that represents a candidate property between two columns"""

    def __init__(self, pid):
        self.pid = pid
        self.target_column = 0
        self.frequency = 1
        self.context_score = 0
        self.subjects = []
        self.objects = []
        self.total_score = 0

class CandidateType:
    """Class that represents a candidate type of a column"""

    def __init__(self, qid, level):
        self.qid = qid
        self.frequency = 1
        self.level = level