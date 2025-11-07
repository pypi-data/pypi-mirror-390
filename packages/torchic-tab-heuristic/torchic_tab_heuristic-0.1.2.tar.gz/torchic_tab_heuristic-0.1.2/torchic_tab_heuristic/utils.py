import pickle
import csv


def save_object(obj, filename):
    """Saves an object to a file using pickle"""
    with open(filename, 'wb') as file:
        pickle.dump(obj, file)

def load_object(filename):
    """Loads an object from a file using pickle"""
    with open(filename, 'rb') as file:
        obj = pickle.load(file)
        return obj
    
def append_to_csv(filename, line):
    """Appends a line to a CSV file"""
    with open(filename, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(line)