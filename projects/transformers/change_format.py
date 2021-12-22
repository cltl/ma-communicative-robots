""" This file is used to transform the webNLG dataset into the right format for the model """
# import packages
import glob
import xml.etree.ElementTree as ET
import pandas as pd
# webNLG dataset xml file
files = glob.glob("webNLG_train.xml", recursive=True)
data_dct = {}
for file in files:
    tree = ET.parse(file)
    root = tree.getroot()
    for sub_root in root:
        for ss_root in sub_root:
            structured_master = []
            unstructured = []
            for entry in ss_root:
                unstructured.append(entry.text)
                structured=[triple.text for triple in entry]
                structured_master.extend(structured)

            unstructured = [i for i in unstructured if i.replace('\t', ' ').strip() != '']
            triples_num = int(len(structured_master)/2)
            structured_master = structured_master[-triples_num:]
            structured_master_str = (' && ').join(structured_master)
            data_dct[structured_master_str] = unstructured

mdata_dct = {"input_text": [], "target_text":[]}
for st,unst in data_dct.items():
    for i in unst:
        mdata_dct['input_text'].append(st)
        mdata_dct['target_text'].append(i)


df = pd.DataFrame(mdata_dct)
# save to csv file
df.to_csv('output_with_sentences.csv')