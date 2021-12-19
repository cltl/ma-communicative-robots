from transformers import RobertaForSequenceClassification, RobertaTokenizer, RobertaConfig
import matplotlib.pyplot as plt
import numpy as np
import torch



class USR:
    def __init__(self, path=None):
        """ Load pretrained and finetuned RoBERTa model for ctx.

            params
            str path: path to stored model or None

            returns: None
        """
        self.__config = RobertaConfig.from_pretrained('adamlin/usr-topicalchat-ctx')
        self.__tokenizer = RobertaTokenizer.from_pretrained('adamlin/usr-topicalchat-ctx')

        if path is not None:
            self.__model = RobertaForSequenceClassification.from_pretrained(path, config=self.__config)
        else:
            self.__model = RobertaForSequenceClassification.from_pretrained('adamlin/usr-topicalchat-ctx',
                                                                            config=self.__config)

        self.__device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
        self.__model.to(self.__device)

    def MCtx(self, context, response):
        """ Scores an input consisting of a (context, response) pair using RoBERTa.

            params
            str context:  the context strings
            sre response: response to the context

            returns: score
        """
        # Concatenates and encodes context-response pair
        input_sequence = context + " \n " + response
        inputs = self.__tokenizer(input_sequence, return_tensors='pt')

        inputs['input_ids'] = inputs['input_ids'].to(self.__device)
        inputs['attention_mask'] = inputs['attention_mask'].to(self.__device)

        # Feeds encoded input through network
        outputs = self.__model(**inputs)
        logits = outputs.logits.detach().cpu().numpy()

        # Returns the softmax score of the positive class, i.e. P(y=1|context, response)
        outputs = np.exp(logits) / np.sum(np.exp(logits))
        return outputs[0][1]


model = USR()

context_file = r'evaluation_dataset\eval_contexts.txt'
response_files = [r'simbot1_responses.txt',
                  r'simbot2_responses.txt',
                  r'simbot3_responses.txt',
                  r'simbot0_lenka_replier_responses.txt']

# Load contexts
with open(context_file, 'r') as file:
    contexts = [line.strip().split(' - ')[-1] for line in file]

# Evaluate responses
response_scores = dict()
for response_file in response_files:

    responses = []
    with open(response_file, 'r') as file:
        responses = [line.strip() for line in file]

    scores = []
    for context, response in zip(contexts, responses):
        score = model.MCtx(context, response)
        scores.append(score)
    response_scores[response_file] = scores

print("Simbot1", np.mean(response_scores[response_files[0]]))
print("Simbot2", np.mean(response_scores[response_files[1]]))
print("Simbot3", np.mean(response_scores[response_files[2]]))
print("LenkaReplier", np.mean(response_scores[response_files[3]]))

dataset = [response_scores[response_files[0]],
           response_scores[response_files[1]],
           response_scores[response_files[2]],
           response_scores[response_files[3]]]
labels = ['Simbot1Replier',
          'Simbot2Replier',
          'Simbot3Replier',
          'LenkaReplier']

plt.violinplot(dataset, widths=0.7, points=300)
for i, data in enumerate(dataset):
    plt.plot([i + 1], [np.mean(data)], 'k^')

plt.title("Response MCtx distribution")
plt.xticks([1, 2, 3, 4], labels)
plt.ylabel("MCtx")
plt.show()