from utils import Character
from utils import find_NE
from utils import load_preprocessed_data
from collections import defaultdict, Counter
import pickle

from Rule_control import find_control, main_control
from Rule1 import find_relation1, main1
from Rule2 import find_relation2, main2

#Get results from seperate rules. Rule 2_1 gives us good results on source and relation, so we use this rule to check other rules against. 
check_dict = main_control("../Preprocessing/Preprocessed_html_data.pkl")
rule1, utt1 = main1("../Preprocessing/Preprocessed_html_data.pkl")
rule2, utt2 = main2("../Preprocessing/Preprocessed_html_data.pkl")

def create_control_set(check_dict):
    """
    Takes the output of rule 2_1 and turns it into a set of tuples
    :param chec_dict: dictionary
    """
    list_tuples = []
    for index, content in check_dict.items():
        tupl = (content[:2])
        list_tuples.append(tupl)

    control_set = list(set([ tuple(sorted(t)) for t in list_tuples]))
    return(control_set)

def get_output(rule, control_set):
    """
    Takes either the output of one rule or the output of several rules, and checks the output againsy the sources and relations in the control set. It outputs unique rules that get extracted in a list.
    """
    
    if type(rule) == dict:
        collected_output = []
        for index, content in rule.items():
            if tuple(content[:2]) in control_set:
                collected_output.append(content)
    
    if type(rule) == list:
        collected_output = []
        for dic in rule:
            for index, content in dic.items():
                if tuple(content[:2]) in control_set:
                    collected_output.append(content)

    triples = []
    for item in collected_output:
        if item not in triples:
            triples.append(item)
            
    return(triples)

def get_and_write_utt(triples, utt, outfilename):
    filtered_utt_dict = {}
    for l in triples:
        for key, entry in utt.items():
            if l == list(key):
                filtered_utt_dict[key] = entry
            else:
                continue
                
    with open(outfilename+".tsv", "w+", encoding="utf-8") as outfile:
        outfile.write("extracted_triple\tutterance-1\tutterance\tutterance+1\n")
        for key, entry in filtered_utt_dict.items():
            outfile.write(f"{key}\t{entry[0]}\t{entry[1]}\t{entry[2]}\n")

def write_to_pkl(triples, filename):
    """
    Takes a list of triples and writes them to a .pkl file
    :param triples: list
    :param filename: str
    """
    
    with open(filename, "wb") as outfile:
        pickle.dump(triples, outfile)
    

control_set = create_control_set(check_dict)
output1 = get_output(rule1, control_set)
#print(len(output1))
#print(output1)
output2 = get_output(rule2, control_set)
#print(output2)
#print(len(output2))
output_combined = get_output([rule1, rule2], control_set)
#print(len(output_combined))
#write_to_pkl(output1, "../data/predictions_rule1.pkl")
#write_to_pkl(output2, "../data/predictions_rule2.pkl")
#write_to_pkl(output_combined, "../data/predictions_combined_rules.pkl")
#get_and_write_utt(output1, utt1, "../data/error_analysis_rule1")
#get_and_write_utt(output2, utt2, "../data/error_analysis_rule2")


