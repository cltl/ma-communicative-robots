'''
Text Similarity - Compare user descriptions with robot observations
'''
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

class TextSimilarity:
    def __init__(self):
        # TODO: Load model
        # self.model = SentenceTransformer('sentence-transformers/roberta-large-nli-stsb-mean-tokens')
        pass

    def calculate_similarity(self, text1, text2):
        '''Calculate similarity score between two texts (0-1)'''
        # TODO: Implement
        pass
