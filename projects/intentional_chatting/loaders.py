import json
import os
from collections import defaultdict

from cltl.dialogue_act_classification.midas_classifier import MidasDialogTagger


class DataLoader:
    def __init__(self, data_dir='./data', out_dir='./processed_data'):
        self.data_dir = data_dir
        self.out_dir = out_dir
        self.data = []

    def load_data(self, file_prefix, file_suffix='.json'):
        file_path = os.path.join(self.data_dir, file_prefix + file_suffix)

        assert os.path.exists(file_path), f'File {file_path} does not exist.'

        with open(file_path, 'r', encoding='utf8') as f:
            data = json.load(f)
        return data

    def save_to_file(self, file_name):
        file_path = os.path.join(self.out_dir, file_name + '.json')

        assert os.path.exists(self.out_dir), f'Directory {self.out_dir} does not exist.'

        with open(file_path, 'w', encoding='utf8') as f:
            json.dump(self.data, f, indent=4)


class EmoryLoader(DataLoader):
    def __init__(self):
        super().__init__(data_dir="data/emory_nlp")
        for i in range(1, 11):
            filename = 'friends_season_0'
            if i == 10:
                filename = filename[:-1]
            filename += str(i)

            data = self.load_data(filename)
            for episode in data['episodes']:
                for scene in episode['scenes']:
                    conv_dict = defaultdict(list)
                    for utterance in scene['utterances']:
                        if not utterance['speakers']:
                            speaker = None
                        else:
                            speaker = utterance['speakers'][0]
                        conv_dict[scene['scene_id']] = {'speaker': speaker, 'text': utterance}
                    self.data.append(conv_dict)


class CommonsenseLoader(DataLoader):
    def __init__(self):
        super().__init__(data_dir="data/commonsense")
        for name in ('test', 'train', 'valid'):
            data = self.load_data(name)
            for context_id, context_data in data.items():
                speaker = context_data['speaker']
                conv_dict = defaultdict(list)
                for utterance in context_data['turns']:
                    conv_dict[context_id].append({'speaker': speaker, 'text': utterance})
                self.data.append(conv_dict)


class ConvAI2Loader(DataLoader):
    def __init__(self):
        super().__init__(data_dir="data/conv_ai_2")
        data = self.load_data("conv_ai_2")
        for row in data['rows']:
            row = row['row']
            dialog_id = row['dialog_id']
            conv_dict = defaultdict(list)
            for utterance in row['dialog']:
                conv_dict[dialog_id].append({'speaker': utterance['sender'],
                                             'text': utterance['text']})
            self.data.append(conv_dict)


class DailyDialogueLoader(DataLoader):
    '''Runs through daily_dialog.json to collect all data'''

    def __init__(self):
        super().__init__(data_dir="data/daily_dialogue", out_dir='processed_data/daily_dialogue')
        data = self.load_data("daily_dialogue")
        speech_act_tagger = MidasDialogTagger('midas-da-roberta/classifier.pt')
        for row in data['rows']:
            row_id = row['row_idx']
            conv_dict = defaultdict(list)
            for i, utterance in enumerate(row['row']['dialog']):
                speaker = "speaker1" if i % 2 == 0 else "speaker2"
                speech_act = speech_act_tagger.extract_dialogue_act(utterance)
                conv_dict[row_id].append({'turn': i,
                                          'speaker': speaker,
                                          'text': utterance,
                                          'speech-act': speech_act[0].value,
                                          'given_emotion': row['row']['emotion'][i],
                                          'given_act': row['row']['act'][i],
                                          'rdf_file': []}
                                         )
            self.data.append(conv_dict)
