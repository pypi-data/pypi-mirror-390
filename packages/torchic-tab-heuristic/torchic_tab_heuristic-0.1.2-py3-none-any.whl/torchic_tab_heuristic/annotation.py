from .config import Config
from .preprocessing import load_table
from .preprocessing import clean_table
import commonregex
import re
import numpy as np
import pandas as pd

# Regex Types
REGEX_TYPES = ["DATE", "TIME", "PHONE", "URL", "EMAIL",
               "IP", "IP", "HEX", "CREDIT_CARD", "ADDRESS",
               "EMPTY", "INT", "FLOAT",
               "BOOLEAN", "IMG_FILE", "COORDS", "ISBN"]

# Dataframe column types
DATAFRAME_TYPES = {"object": "NE",
                   "int64": "INT",
                   "float64": "FLOAT",
                   "bool": "BOOLEAN",
                   "datetime64": "DATETIME",
                   "timedelta[ns]": "TIME_DIFF",
                   "category": "CATEGORY"}

# Regex patterns 
USUAL_PATS = {"empty": re.compile('^$'), 
              "int": re.compile('^[-+]?[0-9]+$'),
              "float": re.compile(r'^[+-]?((\d\d*\.\d*)|(\.\d+))([Ee][+-]?\d+)?$'),
              "boolean": re.compile(r'^([Tt]rue)|([Ff]alse)$'),
              "img": re.compile(r'([-\w]+\.(?:jpg|gif|png))'),
              "coords": re.compile(r'^(\+|-)?(?:90(?:(?:\.0{1,14})?)|(?:[0-9]|' \
                        r'[1-8][0-9])(?:(?:\.[0-9]{1,14})?)),?\s' \
                        r'(\+|-)?(?:180(?:(?:\.0{1,14})?)|(?:[0-9]|[1-9]' \
                        r'[0-9]|1[0-7][0-9])(?:(?:\.[0-9]{1,14})?))$'),
               "isbn": re.compile('^(?:ISBN(?:-1[03])?:? )?(?=[-0-9 ]{17}$|[-0-9X ]" \
                                  "{13}$|[0-9X]{10}$)(?:97[89][- ]?)?[0-9]{1,5}[- ]" \
                                      "?(?:[0-9]+[- ]?){2}[0-9X]$')}

# Commonregex library patterns
COMMONREGEX_PATS = ["date", "time", "phone", "link", "email",  
                    "ip", "ipv6", "hex_color", "credit_card",
                    "street_address" 
                    ]


def annotate(nlp, df):
    
    """Column initial annotation to help scoring"""
    #df = df.dropna()
    primary_labels = []
    secondary_labels = []
    df_length = len(df)
    columns = df.keys()
    
    #For every csv column
    for col in columns:
        #print(df[col])
        
        literal_check = regex_check(df[col].dropna(), len(df[col].dropna()))
        
        if literal_check == "NE":

            primary_labels.append(literal_check)
            nlp_check = spacy_check(col, df, nlp, df_length)
            secondary_labels.append(nlp_check)
            
        else:
            
            primary_labels.append("L")
            secondary_labels.append(literal_check)

    
    primary_labels, secondary_labels = assert_labels(primary_labels, secondary_labels, df, columns)
            
    return primary_labels, secondary_labels


def regex_check (col, df_length):

    """Check for predefined regex patterns in the column"""

    int_counter = 0
    float_counter = 0
    bool_counter = 0

    for element in col:
        text = str(element)

        if text == "True" or text == "False":
            bool_counter += 1
            continue

        elif "." in text:
            try:
                float_elem = float(text)
                float_counter += 1
                continue
            except: 
                pass

        else:
            try:
                int_elem = int(text)
                int_counter += 1
                continue
            except: 
                pass

    
    #Majority voting
    if bool_counter >= df_length/2:
        return "BOOLEAN"
    elif float_counter >= df_length/2:
        return "FLOAT"
    elif int_counter >= df_length/2:
        return "INT"
    
    for i in range(len(COMMONREGEX_PATS)):    
        matches = col.astype(str).str.match(getattr(commonregex, COMMONREGEX_PATS[i]))
        if matches.sum() > df_length/2.0:
            return(REGEX_TYPES[i])
        
    
    for key in USUAL_PATS:
        i = i + 1
        matches = col.astype(str).str.match(USUAL_PATS[key])
        if matches.sum() > df_length/2.0:
            return(REGEX_TYPES[i])
        
         
    return(DATAFRAME_TYPES[str(col.dtype)])


def spacy_check (col, df, nlp, df_length):
    """Use Spacy NLP to check column type"""
    
    possible_labels = []
    
    for index, row in df.iterrows(): 
        if row[col] == None:
            continue
        text = str(row[col])
        
        col_doc = nlp(text)
        
        if col_doc.ents: 
            for ent in col_doc.ents:
                possible_labels.append(ent.label_) 
                
        else:
            possible_labels.append("NE")
        

    #Majority voting
    for label in list(set(possible_labels)):
        
        frequency = possible_labels.count(label)
        if frequency > df_length/2.0:
            return label
        
    
    return "NE"


def key_column_detection(df, primary_labels):
    """Key column detection based on empty cells, unique values and average word count"""
    
    key_column = 10
    df_length = len(df)
    df_index = 0
    
    ne_frequency = primary_labels.count("NE")
    #If only one NE column, it is the subject column
    if ne_frequency == 1:
        return primary_labels.index("NE")
    #If no NE column, there is no subject column
    if ne_frequency == 0:
        return -1 
    
    empty_cells_counter = []  
    unique_cells_counter = [] 
    avg_word_counter = [] 
    col_index = []
     
    
    for col in df.keys():
        
        if primary_labels[df_index] == "NE":
            
            empty_df = df[col].astype(str).str.match('^$')
            empty_cells_counter.append (empty_df.sum()/float(df_length))
            
            unique_cells_counter.append(df[col].nunique()/float(df_length))
            
            word_counter = 0
            for index, row in df.iterrows(): 
                text = row[col]
                word_counter += len(str(text).split())
            
            avg_word_counter.append(word_counter/float(df_length))
            
            col_index.append(df_index + 1)
                
            
        df_index += 1   
        
    #print(empty_cells_counter, unique_cells_counter, avg_word_counter) 
        
    if np.max(empty_cells_counter) > 0:
        empty_cells_counter = np.around((empty_cells_counter ) / np.max(empty_cells_counter), 1)
        
    unique_cells_counter = np.around((unique_cells_counter ) / np.max(unique_cells_counter), 1)
    avg_word_counter = np.around((avg_word_counter ) / np.max(avg_word_counter), 1)
      
    #print(empty_cells_counter, unique_cells_counter, avg_word_counter)      

    score = list((2*unique_cells_counter + avg_word_counter - empty_cells_counter)   /
              np.sqrt(col_index))    
      
    best_score_index = score.index(max(score))
    
    nes_found = 0
    for i in range(len(primary_labels)):
        if primary_labels[i] == "NE":
            if nes_found != best_score_index:
                nes_found += 1
            else:
                return i


def validate_date(date_string):
    """Check if string is a valid date"""
    
    pattern1 = "^\d{4}-\d{2}-\d{2}$"
    pattern2 = "^\d{4}/\d{2}/\d{2}$"
    if re.match(pattern1, date_string) or re.match(pattern2, date_string):
        return True
    else:
        return False

# Assert label results to make sure they make sense for SemTab tables
def assert_labels(primary_labels, secondary_labels, df, columns):
    """Assert/fix initial annotation labels based on observed CSV patterns"""

    for i in range(len(secondary_labels)):
        
        #Date secondary label
        if (secondary_labels[i] == "DATE"):
            cell_list = df[columns[i]].tolist()
            for cell in cell_list:
                if cell != None:
                    if validate_date(str(cell)) == True:
                        pass
                    else:
                        secondary_labels[i] = "NE"
                        break
            primary_labels[i] = "L"
        
        #Cardinal secondary label
        elif (secondary_labels[i] == "CARDINAL") \
            or (secondary_labels[i] == "INT")\
            or (secondary_labels[i] == "FLOAT"):
            check_if_num = True
            cell_list = df[columns[i]].tolist()
            for cell in cell_list:
                if validate_date(str(cell)) == True:
                    secondary_labels[i] = "DATE"
                    primary_labels[i] = "L"
                    break
                else:
                    pass
            
        #Named entity secondary label
        if (secondary_labels[i] == "NE"):
            cell_list = df[columns[i]].tolist()
            check_if_date = False
            for cell in cell_list:
                if cell != None:
                    if validate_date(str(cell)) == True:
                        check_if_date = True
                    else:
                        check_if_date = False
                        secondary_labels[i] = "NE"
                        break
            if check_if_date == True:
                primary_labels[i] = "L"
                secondary_labels[i] = "DATE"

    #Ensure that primary and secondary labels agree in cases that they should
    for i in range(len(secondary_labels)):
        if (secondary_labels[i] == "NE"):
            primary_labels[i] = "NE"
    
    if primary_labels[0] != "NE":
        primary_labels[0] = "NE"
        secondary_labels[0] ="NE"

    return primary_labels, secondary_labels
            

        
        
        
        
        
    
        
        
