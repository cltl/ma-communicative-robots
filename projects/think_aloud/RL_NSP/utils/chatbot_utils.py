""" Filename:     chatbot_utils.py
    Author(s):    Thomas Bellucci
    Description:  Utility functions used by the Chatbot in Chatbot.py.
    Date created: Nov. 11th, 2021
"""


def capsule_for_query(capsule):
    """Casefolds the triple stored in a capsule so that entities match
    with the brain regardless of case.

    params
    dict capsule: capsule containing a triple

    returns: capsule with casefolded triple
    """
    for item in ["subject", "predicate", "object"]:
        if capsule[item]["label"]:
            capsule[item]["label"] = capsule[item]["label"].lower()
    return capsule


def triple_for_capsule(triple):
    """Helper function to prepare a triple for a capsule.

    params
    dict triple: triple with multiple type candidates

    returns: triple with a single type
    """
    subject_type = []
    object_type = []
    predicate_type = []

    if triple["subject"]["type"]:
        subject_type = triple["subject"]["type"][0]
    if triple["predicate"]["type"]:
        predicate_type = triple["predicate"]["type"][0]
    if triple["object"]["type"]:
        object_type = triple["object"]["type"][0]

    capsule_triple = {
        "subject": {"label": triple["subject"]["label"], "type": subject_type},
        "predicate": {"label": triple["predicate"]["label"], "type": predicate_type},
        "object": {"label": triple["object"]["label"], "type": object_type},
    }
    return capsule_triple
