import nltk

def extract_name_pronouns(text):
    """
    Reads text and retuns name (or None) and tuple of given pronouns (or empty tuple).
    Tokenises text, then adds pos tags. If pos tag is
    """
    name_list = []
    pronoun_list = []
    # List of first/second person pronouns to exclude
    exclude_pronoun_list = ["i", "we", "you", "it", "me", "us"]

    # Tokenise
    text_tok = nltk.word_tokenize(text)

    # Part of speech tag
    pos_tagged = nltk.pos_tag(text_tok)
    #print(pos_tagged)

    # Loop through pos tagged list
    for token, pos_tag in pos_tagged:
        if pos_tag == "NNP":
            name_list.append(token)
        if pos_tag == "PRP":
            if not token.lower() in exclude_pronoun_list:
                pronoun_list.append(token)

    name = " ".join(name_list)
    pronouns = tuple(pronoun_list)

    return name, pronouns


sentence_1 = "Hi my name is Vivian, my pronouns are she, her."
sentence_2 = "My name is Soren. I prefer the pronouns he him."
sentence_3 = "My name is Maria and my pronouns are I, they, them. How are you?"
sentence_4 = "I'm Jack, I don't mind what you refer to me as, either he, him or they, them."
sentence_5 = "No pronouns here"
sentence_6 = "My name is Johny Johnson my pronouns are zie zim."



extract = sentence_6

print(extract)
print(extract_name_pronouns(extract))
