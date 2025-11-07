import bz2
from .config import Config
from elasticsearch import Elasticsearch
import sys
import os
import re
from elasticsearch import helpers

class DataLoader:
    """Class to load data from wikidata nt file to elasticsearch. All wikidata properties are included"""
    
    #Prefixes definition
    PREFIX_ENT = b"<http://www.wikidata.org/entity/Q"
    PREFIX_PROP = b"<http://www.wikidata.org/prop/direct/P"
    PREFIX_XML = b"^^<http://www.w3.org/2001/XMLSchema#"
    PREFIX_GEO = b"^^<http://www.opengis.net/ont/geosparql#"
    #PREFIX_MATH = b"^^<http://www.w3.org/1998/Math/MathML>"
    
    #RDFS_LABEL = b'<http://www.w3.org/2000/01/rdf-schema#label>'
    SCHEMA_NAME = b'<http://schema.org/name>'
    #SKOS_ALT = b'<http://www.w3.org/2004/02/skos/core#altLabel>'
    SCHEMA_DES = b'<http://schema.org/description>'
    SAME_AS = b'<http://www.w3.org/2002/07/owl#sameAs>'
    
    REGEX = re.compile(r'[À-žß\w\s.\-()\[\]{}]+')
    
    #ID definition for properties that symbolize name or alias
    NAME_PROPS = {0, 373, 742, 1448, 1476, 1705, 1813, 2561, 8408}

    #Wikdidata instance property 
    INSTANCE_PROP = 31
    
    #Entity to be ignored
    IGNORE_ENTS = {14782, 4167836, 9476502}
    
    def __init__(self, es):
        self.es = es
        
    # Function that extracts entities, properties ant literals from wikidata triples
    def read_wikidata(self, file):
        
        # self.es.options(ignore_status=[400,404]).indices.delete(index='wd_names_2023')
        # self.es.indices.create(index='wd_names_2023')

        # for i in range(1,10):
        #     self.es.options(ignore_status=[400,404]).indices.delete(index='entities_'+str(i))
        
        # self.es.options(ignore_status=[400,404]).indices.delete(index='wd_2023')
        # self.es.indices.create(index='wd_2023')
        
        print(f"Reading {os.path.basename(file)}...")
        
        at_line = 0
        bulk_chunk = 10000000
        total_lines = 7387963546

        current_subject = -1
        subject_names = [] #array to store all names/alias of an entity
        
        entries = [] #array to store all queries that are to be executed with bulk by elasticsearch
        
        #Open file
        with bz2.open(file) as fin:
            for line in fin:
                at_line += 1
                
                #Print loading milestones
                if at_line % 1000000 == 0:
                    print(f"At line {at_line}/{total_lines} [{100*at_line/total_lines:.2f}%];")
            
                #Load elasticseach bulk    
                if at_line % bulk_chunk == 0:
                    print("Adding bulk to elasticsearch...")
                    helpers.bulk(self.es, entries)
                    entries = []
                    print("Bulk added to elasticsearch!")
                   
                #Decoding and encoding of the triples
                line = line.decode('unicode-escape').encode('utf8')    
                #print(line)
                
                #Get subject ID
                if line.startswith(self.PREFIX_ENT):
                    subject_id = self.extract_subject_id(line)

                    #Recognition of new entity and initialization of names array
                    if subject_id != current_subject:
                        current_subject = subject_id
                        subject_names = []
                        subject_descriptions = []
                        
                    #Disposal of fault entries
                    if subject_id < 0:
                        continue
                    
                    #Get property ID
                    parts = line.strip().split(maxsplit=2)
                    parts[2] = parts[2][:-2]
                    property_id = self.extract_property_id(parts[1])  
                    
                    #If property is important
                    if property_id != -1:
                        
                        #Get object 
                        object_id = self._extract_name(parts[2])
                        
                        #Discrimination between entity and literal objects
                        if object_id.startswith(self.PREFIX_ENT):
                            object_id = 'Q' + str(self.extract_subject_id(object_id))    
                            
                        else:
                            #Discovery of literals with a datatype
                            if (self.PREFIX_XML in object_id) or (self.PREFIX_GEO in object_id):
                                datatype_split = object_id.decode('utf-8').split("^^")
                                object_id = datatype_split[0][1:-1]
                                #object_datatype = datatype_split[1].split("#")[1][0:-1]
                                #print(object_datatype)
                                
                            else:
                                object_id = object_id.decode('utf-8')
                            
                        #Discard big math formulas and large text
                        if len(object_id) > 200:
                            continue
                        
                        #Discard entities to be ignored
                        if property_id == self.INSTANCE_PROP:
                            try:
                                if int(object_id[1:]) in self.IGNORE_ENTS:
                                    continue
                            except Exception:
                                continue 

                        
                        #Create 'names' entry
                        if property_id in self.NAME_PROPS:   
                            # Check if the found name has already been discovered for the given entity
                            if object_id not in subject_names:
                                subject_names.append(object_id)

                                entry = {
                                    "_index": Config.ELASTIC_INDEX,
                                    "document": "doc",
                                    "_source": {
                                        "subject": subject_id,
                                        "property": property_id,
                                        "object": object_id
                                        }
                                    } 

                                entries.append(entry)

                            else: 
                                continue  
                            
                        #Create an entry for all the other properties
                        # else:
                        #     if property_id == 1:
                        #         if object_id not in subject_descriptions:
                        #             subject_descriptions.append(object_id)
                            
                        #             entry = {
                        #                     "_index": 'wd_2023',
                        #                     "document": "doc",
                        #                     "_source": {
                        #                         "subject": subject_id,
                        #                         "property": property_id,
                        #                         "object": object_id,
                        #                         }
                        #                     }  
                                    
                        #             entries.append(entry)
                        #             continue

                        #         else:
                        #             continue
                            
                        #     entry = {
                        #         "_index": 'wd_2023',
                        #         "document": "doc",
                        #         "_source": {
                        #             "subject": subject_id,
                        #             "property": property_id,
                        #             "object": object_id,
                        #             }
                        #         } 
                            
                        #     entries.append(entry)

        return
                    

    # Extract subject ID              
    @classmethod
    def extract_subject_id(cls, l):
        """Extracts entity property of subjects"""
        
        try:
            id = int(l.split()[0][len(cls.PREFIX_ENT):-1])
        except Exception:
            id = -1
        
        return id
    
    # Extract property ID
    @classmethod
    def extract_property_id(cls, l):
        
        """Extract property id if it belongs to the wanted properties"""
        
        try:
            if not l.startswith(cls.PREFIX_PROP):
                if l.startswith(cls.SCHEMA_NAME): return 0
                elif l.startswith(cls.SCHEMA_DES): return 1
                elif l.startswith(cls.SAME_AS): return 2
                else:
                    return -1
            id = int(l[len(cls.PREFIX_PROP):-1])
        except Exception:
            id = -1

        return id

    # Extract objects' content
    @staticmethod
    def _extract_name(part: bytes):
        """ Extracts string from object's bute form"""
        
        part = part.strip()
        if part.startswith(b'"'):
            if b'"@' in part:
                part = part.rsplit(b'"@', 1)[0]
                part = part[1:]
            elif part.endswith(b'"'):
                part = part[1:-1]

        return part
        
     
# Function to establish connection with elasticsearch
def connect_elastic():
    
    """Connect with elasticsearch server"""
    
    print("Connecting with Elasticsearch...")
    config = Config()

    if not config.ACTIVATE_AUTH:
        es = Elasticsearch([{"host" : "localhost","port" : 9200,"scheme": "http"}])
    else:
        ca_certs = config.CA_CERTS
        usr_name = config.USER_NAME
        password = config.PASSWORD
        es = Elasticsearch("https://localhost:9200", ca_certs=ca_certs, basic_auth=(usr_name, password))

    #Exit in case of failure
    if not es.ping():
        sys.exit('Connection with ElasticSearch failed!')   
    
    return es
    
# if __name__ == '__main__':
    
#     es = connect_elastic()
#     dl = DataLoader(es)
#     dl.read_wikidata(Config.FILE_WD)
#     es.transport.close()


    