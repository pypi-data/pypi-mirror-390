from .config import Config
import pandas as pd
import sys
import numpy as np
import ftfy
from bs4 import BeautifulSoup
import re

# Read table as Pandas DataFrame
def load_table(file_path):
    
    """Loads CSV input file"""
    
    try:
        # Read the first line
        with open(file_path, 'r', encoding='utf-8') as file:
            first_line = file.readline().strip()

        # Check if the first line is entirely integers
        if all(item.isdigit() for item in first_line.split(',')):
            # Skip the first line if it contains only integers
            df = pd.read_csv(file_path, encoding='utf-8', skiprows=1, quotechar='"', skipinitialspace=True)
        else:
            # Read the file normally
            df = pd.read_csv(file_path, encoding='utf-8', quotechar='"', skipinitialspace=True)
    except IOError:
        sys.exit('No such file in the directory!')
        
    return df

# Read entity table as Pandas DataFrame
def load_entity_table(file):

    """Loads Special Entity CSV input file"""

    try:
        df = df = pd.read_csv(file, header=None, encoding='utf-8')
    except IOError:
        sys.exit('No such file in the directory!')

    prop_names = df[0].unique()
    vertical_data = {}

    for prop_name in prop_names:
        prop_values = df[df[0] == prop_name][1].tolist()  # Get all values for the current property
        vertical_data[prop_name] = prop_values  # Store the values in the dictionary

    df = pd.DataFrame(vertical_data)

    return df


# Table cleaning and pre-processing
def clean_table(df):
    
    """Gets rid of None values, unusual characters and HTML tags"""
    date_pattern = r"\d{4}-\d{2}-\d{2}"
    replacement = r"\g<0>"

    for index, row in df.iterrows():
        for col in df.keys():
            text = row[col]
            if type(text) == str :
                date_match = re.search(date_pattern, text)
                if date_match:
                    df.at[index,col] = date_match.group(0)
                    continue
                if len(text) > 0 and text[0] == '<' and text[-1] == '>':
                    text = BeautifulSoup(text, features="lxml").get_text()
                text = ftfy.fix_text(text)
                df.at[index,col] = text

    df = df.replace("-", None)
    df = df.replace("NaN", None)
    df = df.replace("none", None)
    df = df.replace("None", None)
    df = df.replace("uknown", None)
    df = df.replace(np.NaN, None)
    #df = df.dropna()
                
    
    return df

        
        
        
        
        
        