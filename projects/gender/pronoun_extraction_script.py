# imports
import requests
import numpy as np
import cv2
import nltk
from datetime import datetime
#
TODO GIVE NAMEAPI KEY HERE
NAMEAPI_KEY=

url = ("http://api.nameapi.org/rest/v5.3/genderizer/persongenderizer?"
    f"apiKey={NAMEAPI_KEY}"
)

from cltl_face_all.face_alignment import FaceDetection
from cltl_face_all.arcface import ArcFace
from cltl_face_all.agegender import AgeGender

ag = AgeGender(device='cpu')
af = ArcFace(device='cpu')
fd = FaceDetection(device='cpu', face_detector='blazeface')

def get_visual_gender(image_filepath, male_threshold=0.35, female_threshold=0.65):
    """
    Reads image
    Load Tae's gender-age code. https://github.com/leolani/cltl-face-all
    Extract gender
    Translate gender  to Male, Female, Unknown/Neutral (0,1,2)
    Maybe we need a function to read the image file path to the format needed for Tae's module

    NOTE: THRESHOLDS ARE ASSUMED AND UNTESTED!

    :param image_filepath: string to filepath
    :return: 0,1,2 for male, female, unknown
    """
    img_BGR = cv2.imread(image_filepath)
    img = cv2.cvtColor(img_BGR, cv2.COLOR_BGR2RGB)

    bboxes = fd.detect_faces(img[np.newaxis, ...])
    landmarks = fd.detect_landmarks(img[np.newaxis, ...], bboxes)
    faces = fd.crop_and_align(img[np.newaxis, ...], bboxes, landmarks)

    # There is only one image per batch. fd returns a list
    bbox = bboxes[0]
    landmark = landmarks[0]
    face = faces[0]
    if len(bbox) > 0:
        # ag and af return a np.ndarray
        #We assume the first recognised face is the correct face
        _, predicted_gender = ag.predict(face)
        if predicted_gender[0] < male_threshold:
            return 0 #for male
        elif predicted_gender[0] > female_threshold:
            return 1 #for female
        else:
            return 2 #for other



def get_name_gender(name_string):
    """
    Use NameAPI.
    Translate result to 0,1,2 for gender coding.
    :param name_string: The name as a string
    :return: 0,1,2 for male, female, unknown
    """
    # Dict of data to be sent to the RESTapi of NameAPI.org:
    payload = {
        "context": {
            "priority": "REALTIME",
            "properties": []
        },
        "inputPerson": {
            "type": "NaturalInputPerson",
            "personName": {
                "nameFields": [
                    {
                        "string": f"{name_string}",
                        "fieldType": "GIVENNAME"
                    }]
            },
            "gender": "UNKNOWN"
        }
    }
    # Proceed, only if no error:
    try:
        # Send request to NameAPI.org by doing the following:
        # - make a POST HTTP request
        # - encode the Python payload dict to JSON
        # - pass the JSON to request body
        # - set header's 'Content-Type' to 'application/json' instead of
        #   default 'multipart/form-data'
        resp = requests.post(url, json=payload)
        resp.raise_for_status()
        # Decode JSON response into a Python dict:
        resp_dict = resp.json()
        name_gender = resp_dict['gender']
        if name_gender == 'MALE':
            name_gender_int = 0
        elif name_gender == 'FEMALE':
            name_gender_int = 1
        elif name_gender == 'NEUTRAL':
            name_gender_int= 2
        elif name_gender == 'UNKNOWN':
            name_gender_int = 2
        return name_gender_int
    except requests.exceptions.HTTPError as e:
        print("Bad HTTP status code:", e)
    except requests.exceptions.RequestException as e:
        print("Network error:", e)


def extract_name_pronouns(text):
    """
    Reads text and retuns name (or None) and tuple of given pronouns (or empty tuple).
    Tokenises text, then adds pos tags. All NNPs in sentence are stored as the name.
    All PRPs are stored as pronouns.

    :param text: The sentence as a string
    :return: tuple(name, pronoun) with name in a string and pronouns in a tuple
    """
    name_list = []
    pronoun_list = []
    # List of first/second person pronouns to exclude
    exclude_pronoun_list = ["i", "we", "you", "it", "me", "us"]

    # Tokenise
    text_tok = nltk.word_tokenize(text)

    # Part of speech tag
    pos_tagged = nltk.pos_tag(text_tok)
    print(pos_tagged)

    # Loop through pos tagged list
    for token, pos_tag in pos_tagged:
        if pos_tag == "NNP":
            name_list.append(token)
        if pos_tag == "PRP":
            if not token.lower() in exclude_pronoun_list:
                pronoun_list.append(token)

    # Reformat name
    if len(name_list) == 0:
        name = None
    elif len(name_list) == 1:
        name = name_list[0]
    else:
        name = " ".join(name_list)

    # Reformat pronouns
    if len(pronoun_list) == 0:
        pronouns = None
    elif len(pronoun_list) == 1:
        pronouns = pronoun_list[0]
    else:
        pronouns = "/".join(pronoun_list)

    return name, pronouns

def greeting_script():
    """
    Script where Leolani introduces herself and asks who are you

    :return: tuple(name, pronouns) with name in string and pronouns as tuple
        or tuple(name, None)
    """
    name = None
    pronouns = None
    self_defined= None

    print("Hi! I'm Leolani, my pronouns are she/her. I love getting to know new people.")
    answer = input("Who are you? \n")

    detected_name, detected_pronouns = extract_name_pronouns(answer)

    # Determine name
    if detected_name == None:
        name = input("I am sorry, I didn't understand. What is your name?")
    else:
        name = detected_name

    # Determine pronouns
    if detected_pronouns != None:
        pronouns = detected_pronouns
        print(f"Nice to meet you, {name}. Your pronouns are {pronouns}")
        self_defined=True
    else:
        # if no pronouns are given (None)
        print(f"Nice to meet you, {name}.")
        # TODO: remove later
        print("You have not specified your pronouns.")
        pronouns = None

    return name, pronouns, self_defined

# Design change. Not suggesting pronouns due to questionnaire results.
# def suggest_pronouns_script(suggesting_pronouns):
#     """
#     Verifying whether suggested pronouns are okay.
#     :param suggesting_pronouns: 0,1,2 relating to gender of visual input
#     :return: pronouns
#     """
#     pronouns = None
#
#     pronoun_ok = input(f"Would you like me to refer to you as {suggesting_pronouns}? y/n \n")
#
#     if pronoun_ok == "y":
#         pronouns = suggesting_pronouns
#     else:
#         print("My apologies, I am still learning about the human world.")
#         pronouns = input("Which pronouns would you like me to use to refer to you? \n")
#
#     return pronouns

def pronoun_retrieving_script(name_gender, visual_gender):
    """
    Assumes or asks for pronouns.
    This is where the scenarios go if the pronouns were not given in the introduction.
    :param name_gender: 0,1,2 relating to gender of name
    :param visual_gender: 0,1,2 relating to gender of visual input
    :return: pronouns
    """
    # Set global variable
    pronouns = None

    # If gender of name is unknown, ask for pronouns, no suggestion
    if name_gender == 2:
        # TODO remove first print statement
        print("I cannot detect gender based on your name.")

        pronouns = input("Which pronouns would you like me to use to refer to you? ")
        self_defined=True

    # If gender of name and visual match, assume pronouns
    elif name_gender == visual_gender:
        # TODO: remove print statement
        print("The gender of your name and visual match. I will assume your pronouns.")
        self_defined=False

        # TODO: check if number coding is correct
        if name_gender == 0:
            pronouns = "he/him"
        elif name_gender == 1:
            pronouns = "she/her"

    else:
        # TODO remove first print statement
        print("There is a mismatch between the gender of your name and visual.")

        print("I have been taught that there are different ways that humans like to be referred as.")
        pronouns = input("Which pronouns would you like me to use to refer to you?")
        self_defined=True

    return pronouns, self_defined



def create_triple(name_string, pronouns_string, self_defined):
    """
    Create triple in Leolani brain format.
    :param name_string: String of name to store in Leolani brain (is this needed to form the triple
    :param pronouns_string: string of pronouns
    :return: triple in Leolani brain format
    """
    #Is this usefull?

    #pronouns_string = "/".join(list(pronouns_tuple))
    if self_defined:
        author=name_string.lower()
    else:
        author='leolani'

    statement={
            "utterance": f"{name_string.lower()} has pronouns {pronouns_string.lower()}",
            "subject": {"label": {name_string.lower()}, "type": "person"},
            "predicate": {"type": "has_pronouns"},
            "object": {"label": f"{pronouns_string.lower()}", "type": "pronouns"},
            "perspective": {"certainty": 1, "polarity": 1, "sentiment": 0},
            "author": f"{author}",
            "chat": 1,
            "turn": 1,
            "position": "0-25",
            "date": datetime.date(datetime.now())
        }
    return statement

def main():
    image_path='data/sample_data/Justin.jpg'

    # Set global variables
    name = None
    pronouns = None

    # Leolani introduces herself
    name, pronouns, self_defined= greeting_script()

    # If pronouns are not given
    if pronouns == None:
        visual_gender = get_visual_gender(image_path)
        name_gender = get_name_gender(name)

        # Run through script to extract pronouns either by asking or assuming
        pronouns, self_defined = pronoun_retrieving_script(name_gender, visual_gender)

    print(create_triple(name, pronouns, self_defined))

if __name__ == "__main__":
    main()
