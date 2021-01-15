import pickle

class Character:
    'Class representing named characters'
    def __init__(self, firstname, lastname=None, relations=dict()):
        self.firstname = firstname
        self.lastname = lastname
        self.relations = relations
        
        
def find_NE(utterance, j, NE_list):
    '''
    Given an utterance and the location in that utterance of a kinship term, find the 
    closest NE to that term, or None if there is none.
    
    :param utterance: an utterance
    :param j: an index where a kinship term is located in utterance["tok_utt"]
    
    :returns nearest_NE: the nearest NE as a string, or None
    '''
    tokens = utterance["tok_utt"]
    nearest_NE = None
    backward = j-1
    forward = j+1
    while True:
        if backward >= 0:
            if tokens[backward].lower() in NE_list:
                nearest_NE = tokens[backward]
                break
            backward -= 1
        if forward < len(tokens):
            if tokens[forward].lower() in NE_list:
                nearest_NE = tokens[forward]
                break
            forward += 1
        if backward < 0 and forward >= len(tokens):
            nearest_NE = None
            break
            
    return nearest_NE

def load_preprocessed_data(filepath):
    '''
    Loads the MELD preprocessed data into a dictionary
    '''
    field_names = ['source', 'utt', 'tok_utt', 'season', 'episode', 'sr_number']
    data = []
    with open(filepath, "rb") as infile:
        data = pickle.load(infile)
    return data