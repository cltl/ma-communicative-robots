import pandas as pd
import numpy as np
from collections import defaultdict
import matplotlib.pyplot as plt
import json

if __name__ == "__main__":
    id_file = 'results/replier_ids.json'
    eval_files = ['results/evaluation_dataset_thomas.csv',
                  'results/evaluation_dataset_fina.csv',
                  'results/evaluation_dataset_imme.csv']
    metrics = ['engaging', 'specific', 'relevant', 'correct', 'semantically appropriate']
    
    with open(id_file, 'r') as file:
        id2replier = {id_: f for f, id_ in json.load(file).items()}

    df = pd.concat([pd.read_csv(f, encoding="ISO-8859-1") for f in eval_files])

    for metric in metrics:
        replier_scores = df[['id', metric]].copy()
        replier_scores['replier'] = df['id'].replace(id2replier)

        labels, values = [], []
        for replier, scores in replier_scores.groupby('replier'):
            labels.append(replier[23:-4])
            values.append(scores[metric].mean())

        plt.title(metric)
        plt.bar(np.arange(len(values)), values)
        plt.xticks(np.arange(len(values)), labels, rotation=30)
        plt.show()

        
        
