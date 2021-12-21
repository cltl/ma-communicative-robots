from scipy.spatial import distance
from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer(r"multi-qa-mpnet-base-cos-v1")
model.save(r"sbert_models\multi-qa-mpnet-base-cos-v1")

#### Alternative SBERT language model 2 #####

# model = SentenceTransformer(r'all-mpnet-base-v2')
# model.save(r"sbert_models\all-mpnet-base-v2")

#### Alternative SBERT language model 3 #####

# model = SentenceTransformer(r'msmarco-distilbert-base-v4')
# model.save(r"sbert_models\msmarco-distilbert-base-v4")


def get_the_most_similar(
    sent1, cand_list, model=model
):  # model = SentenceTransformer("multi-qa-mpnet-base-dot-v1")

    sentence1_embeddings = model.encode(sent1)
    similarity_dict = dict()
    for sent in cand_list:
        candidate_embedding = model.encode(sent)
        similarity = util.cos_sim(sentence1_embeddings, candidate_embedding)
        # similarity = (1 - distance.cosine(sentence1_embeddings, candidate_embedding))
        similarity_dict[sent] = similarity

    the_most_similar = max(similarity_dict, key=similarity_dict.get)
    explanation = sorted(
        similarity_dict.items(), key=lambda item: item[1], reverse=True
    )

    return the_most_similar, explanation


def get_similarity_score(sent1, cand_sent, model=model):
    sentence1_embeddings = model.encode(sent1)
    candidate_embedding = model.encode(cand_sent)
    similarity = distance.cosine(sentence1_embeddings, candidate_embedding)

    return similarity


##### test the functions uncommenting following lines #####

# sent1 = 'Karla likes singing.'
# cand_list= ['I did not know that! I had never heard about singing before!',
#     'I would like to know. Has karla ever be family of a person?',
#    'I would like to know. Has karla experience smell?']

# answer, explanation = get_the_most_similar(sent1, cand_list)
# print(answer)
# print(explanation)

# cand_sent = 'I did not know that! I had never heard about singing before!'

# similarity = get_similarity_score(sent1, cand_sent, model=model)

# print(similarity)
