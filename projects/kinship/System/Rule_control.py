from utils import Character
from utils import find_NE
from utils import load_preprocessed_data
from collections import defaultdict
import pickle

def find_control(utterances, kinship_term, character_list):
    '''
    Specifically finds relations without a target.
    
    Given a list of utterances and a specific kinship term, defines a kinship triple
    based on a set of heuristics.
    
    :param utterances: a list of utterances
    :param kinship_term: a kinship term as a string
    
    :returns kinship_triple: a tuple of strings (source, relation, target)
    '''
    source = None
    relation = "has-"+kinship_term
    target = None
    
    
    
    with open("../Building_Relations/relations.pkl", "rb") as infile:
        characters = pickle.load(infile)
    
    character_list = [character.firstname for character in characters]
    
    
    # find kinship term location
    kinship_term_location = None
    for i in range(len(utterances)):
        tok_list = utterances[i]["tok_utt"]
        for j in range(len(tok_list)):
            if tok_list[j] == kinship_term:
                kinship_term_location = (i, j)
        if kinship_term_location:
            break
    #if kinship_term_location == None:
    #    break
        
    kinship_utterance = utterances[i]
    tokens = kinship_utterance["tok_utt"]
    tokens = [token.lower() for token in tokens]
    prev_utterance = None
    next_utterance = None
    if i > 0:
        prev_utterance = utterances[i-1]
    if i < len(utterances)-1:
        next_utterance = utterances[i+1]
  
 ################################################################################## edit underneath

    for k in range(len(tokens)-1):
        if tokens[k]== "my":
            # Heuristic: source = source of utterance, target = nearest NE in utterance, 
            #      or None
            source = kinship_utterance["source"]
            #target = None
            if tokens[k+1] in ["brother", "brothers", "sister", "sisters", "cousin", "cousins", "mother", "father", "mom", "dad", "son", "sons", "daughter", "daughters", "niece", "nephew", "twin", "aunt", "uncle", "child", "children", "parent", "parents"]:
                relation = "has-"+tokens[k+1]
                
            
    return source, relation, target

def main_control(data):
    """
    Looks for sentences that only pass this rule in the parsed HTML data
    Returns a dictionary where the key is the utterance id and the value the triple it extracted
    :param data: <str> a filepath
    """
    
    with open("../Building_Relations/relations.pkl", "rb") as infile:
        characters = pickle.load(infile)
    character_list = [character.firstname for character in characters]
    
    data = load_preprocessed_data(data)
    
    kinship_terms = ["brother", "brothers", "sister", "sisters", "cousin", "cousins", "mother", "father", "mom", "dad", "son", \
                 "sons", "daughter", "daughters", "niece", "nephew", "twin", "aunt", "uncle", "child", "children", "parent",\
                 "parents"]
    
    train_data = defaultdict(list) # inner list is list of lists (collections of utterances)
    for kinship_term in kinship_terms:
        for index, d in enumerate(data):
            if kinship_term in (d['tok_utt']):
                train_data[kinship_term].append([data[index-1], data[index], data[index+1]])    
    
    relation_dict = {}
    i = 0
    for kinship_term, utterances in train_data.items():
        for utterance_set in utterances:
            source, relation, target = find_control(utterance_set, kinship_term, character_list)
            i+=1
            if source != None:
                relation_dict[i] = [source, relation, target]
            
    return(relation_dict)


#result = main("../Preprocessing/Preprocessed_html_data.pkl")
#with open("control_dict.pkl", "wb") as outfile:
#    pickle.dump(result, outfile)
#print(result)