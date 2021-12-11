# imports

"""
Things to think about
Which way are we defining the genders? (How does Tae do it?)
Suggestion
Male: 0
Female: 1
Unknown/Neutral/Both: 2

"""

def get_visual_gender(image_filepath):
    """
    Reads image
    Load Tae's gender-age code.
    Extract gender & confidence.
    Translate gender and confidence to Male, Female, Unknown/Neutral (0,1,2)
    # Maybe we need a function to read the image file path to the format needed for Tae's module

    :param image_filepath: string to filepath
    :return: 0,1,2 for male, female, unknown
    """

def get_name_gender(name_string):
    """
    Use (harvard) api.
    Translate result to 0,1,2 for gender coding.
    :param name_string: The name as a string (not sure about capitalisation)
    :return: 0,1,2 for male, female, unknown
    """

def greeting_script():
    """
    Script where Leolani introduces herself and asks who are you

    :return: tuple(name, pronouns) or tuple(name, None)
    """

def pronoun_retrieving_script(name_gender, visual_gender):
    """
    Assumes or asks for pronouns.
    This is where the scenarios go if the pronouns were not given in the introduction.
    :param name_gender: 0,1,2 relating to gender of name
    :param visual_gender: 0,1,2 relating to gender of visual input
    :return: pronouns
    """

def create_triple(name_string, pronouns_string):
    """
    Create triple in Leolani brain format.
    Probably something like: LeolaniWorld:Quirine, property:has_pronouns, value:she/her.
    # How do we store the pronouns? Options: tuple of strings ("she", "her"), string "she/her", int 0, 1 or 2 (but then its a predefined finite set.

    :param name_string: String of name to store in Leolani brain (is this needed to form the triple
    :param pronouns_string: string of pronouns
    :return: triple in Leolani brain format
    """

def store_triple(triple_object):
    """
    Store triple object in folder and file
    :param triple_object:
    :return: nothing, saved triple in correct location
    """

def main():
    triple_file = "somefolder/somefile.someformat"  # Location of where to store triple
    name = None
    pronouns = None

    # Leolani introduces herself and asks who are you. Assume name will be given. Pronouns might be given.
    name, pronouns = greeting_script()

    # If pronouns are not given
    if pronouns == None:
        # Extract gender based on visual input and name
        visual_gender = get_visual_gender(image_filepath)
        name_gender = get_name_gender(name_string)

        # Run through script to extract pronouns either by asking or assuming
        pronouns = pronoun_retrieving_script(name_gender, visual_gender)

    # if for some reason the system breaks or there is a leak then use they them pronouns

    if pronouns == None:
        pronouns = "they/them"

    # Adapt to Leolani format
    triple_object = create_triple(name, pronouns)

    store_triple(triple_object, triple_file)