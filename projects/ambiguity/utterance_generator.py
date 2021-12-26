import json
import os
import random
from enum import Enum


class ElementType(Enum):
    FACT = 0
    PERSON = 1


class Template:
    """Contains information relevant to constructing a templated sentence."""

    def __init__(
        self,
        elements,
        prefixes=["Here", "And here"],
        infixes=["", "By the way, ", "Oh, have I mentioned, "],
        postfixes=["."],
    ):
        self.prefixes = prefixes
        self.infixes = infixes
        self.postfixes = postfixes
        self.elements = elements


class Element:
    """Base class for objects in a scenario."""

    def __init__(self, type, data):
        self.type = type
        self.data = data


class Fact(Element):
    def __init__(self, data):
        super().__init__(type=ElementType.FACT)


class Relation:
    """Relation between two elements, typically between two people, i.e.
    mother - daughter."""

    def __init__(self, elem1, type, elem2):
        self.elem1 = elem1
        self.type = type
        self.elem2 = elem2

    def __str__(self):
        return str(self.elem1) + " --" + str(self.type) + "--> " + str(self.elem2)

    def __repr__(self):
        return "Relation " + self.__str__()

    def connect_second_person(self):
        pass


class Person(Element):
    """Abstraction for a person in a scenario."""

    def __init__(self, full_name):
        super().__init__(ElementType.PERSON, data={"full_name": full_name})

    def __str__(self):
        return self.data["full_name"]

    def __repr__(self):
        return "Person " + self.__str__()

    def connected_to(self):
        pass


RELATION_TYPES = [
    "colleague",
    "spouse",
    "sibling",
    "unmarried_partner",
    "mother",
    "father" "child" "country_of_citizenship",
]


def process_person_dict(pers):
    """Creates a Person instance out of a dictionary extracted from a JSON file."""
    person = Person(pers["full_name"][0])
    person.data["name"] = pers["name"]
    person.data["sex_or_gender"] = pers["sex_or_gender"][0]
    person.relations = []
    for relation in RELATION_TYPES:
        if pers.get(relation):
            for fname in pers.get(
                relation
            ):  # the other persons with whom the person in the photo has a relation (from RELATION_TYPES) with.
                person.relations.append(
                    Relation(person, relation, Person(fname))
                )  # this appends: e.g. Emily Waltham --spouse--> Ross Geller
    # a = Person()
    # a.relation_to =  Rel
    return person


def integrate_person(persons, person):
    """Integrate a person into the persons list by changing all relation references
    that refer to them by name to refer to them by instance reference instead.

    persons - list of persons to integrate person with
    person - person to integrate

    Returns the list of integrated persons.
    """

    # integrate person with existing persons
    for other in persons:
        if hasattr(other, "relations"):
            for relation in other.relations:
                if relation.elem2.data["full_name"] == person.data["full_name"]:
                    relation.elem2 = person
        if hasattr(person, "relations"):
            for relation in person.relations:  # integrate other persons with person
                if relation.elem2.data["full_name"] == other.data["full_name"]:
                    relation.elem2 = other

    return persons


def extract_persons(picture, from_json=False):
    """Extracts the information about all people present in a given picture.

    picture - picture data dictionary or a JSON file URI
    from_json - whether to treat picture parameter as a dictionary or a file URI

    Returns a list of Person objects."""
    if from_json:
        pic_data = json.load(open(picture))
    else:
        pic_data = picture
    persons = [process_person_dict(person) for person in pic_data["context"]["persons"]]
    for person_ix in range(len(persons)):
        persons = integrate_person(persons, persons[person_ix])
    return persons


def extract_speaker(picture, from_json=False):
    """Extracts a Person object representing the narrator in a given scenario.

    picture - picture data dictionary or a JSON file URI
    from_json - whether to treat picture parameter as a dictionary or a file URI

    Returns a Person object representing the speaker."""
    if from_json:
        pic_data = json.load(open(picture))
    else:
        pic_data = picture
    person = pic_data["context"]["speaker"]
    return process_person_dict(person)


def get_picture_dicts(directory):
    """Gets all picture data dictionaries from a directory.

    directory - directory to traverse for JSON files. The assumption is that the
      data is organized as scenario -> picture -> picture JSON.

    Returns a dictionary of dictionaries of picture data."""
    results = {}
    for picture_name in os.listdir(directory):
        for json_filename in os.listdir(os.path.join(directory, picture_name)):
            results[picture_name] = json.load(
                open(os.path.join(directory, picture_name, json_filename))
            )
    return results


GENDER_RELATION = {
    "male": {
        "spouse": "husband",
        "unmarried_partner": "boyfriend",
        "sibling": "brother",
        "father": "father",
        "mother": "mother",
        "child": "son",
        "friend": "friend",
        "colleague": "colleague",
    },
    "female": {
        "spouse": "wife",
        "unmarried_partner": "girlfriend",
        "sibling": "sister",
        "father": "father",
        "mother": "mother",
        "child": "daughter",
        "friend": "friend",
        "colleague": "colleague",
    },
}

POSSESSIVE_RELATIONS = [
    "spouse",
    "unmarried_partner",
    "sibling",
    "mother",
    "father",
    "child",
    "colleague",
    "friend",
]


class Generator:
    """Base class for generating utterances for a scenario. Maintains the conversation
    state and allows for specification of numerous parameters regarding generated
    sentences."""

    mentioned_facts = []
    mentioned_people = []
    last_person = None

    def __init__(self, persons, pictures, speaker):
        """Initialize a Generator.

        persons - list of Person objects to use when generatinng utterances.
        pictures - list of picture data dictionaries used in the scenario.
        speaker - Person object representing the speaker.

        Returns a Generator object."""
        self.persons = persons
        self.pictures = pictures
        self.speaker = speaker
        self.mentioned_facts = []
        self.mentioned_people = []

    def generate_random_utterance(
        self,
        template,
        persons=[],
        ambiguity_level=None,
        person=None,
        facts_to_mention=1,
    ):
        # print('size of mentioned facts: ', len(self.mentioned_facts))

        if person == None:
            if persons == []:
                person = random.choice(self.persons)  # picks a random person in general
            else:
                person = random.choice(persons)  # picks a random person from the photo

        if (
            len(persons) > 1
        ):  # if a photo has multiple people, introduce them appropriately
            prefix = self.introduce_multiple(persons, person, ambiguity_level)
        else:
            prefix = ""

        facts = person.relations
        # print('person.relations: ', person.relations)
        can_use_pronoun = False
        mentioned_first_time = True
        # check if person has already been mentioned
        if (
            person in self.mentioned_people
        ):  # if so, check what facts have already been mentioned
            mentioned_first_time = False
            if self.last_person == person:
                can_use_pronoun = True  # if the last person mentioned was the same as the current person, you can use pronouns
        else:
            self.mentioned_people.append(person)

        pfacts = set(self.mentioned_facts)
        novel_facts = set(facts) - pfacts  # only the facts that aren't mentioned yet

        # print('mentioned facts (pfacts):', pfacts)
        # print('facts (extracted):', facts)
        # print('novel_facts: ', novel_facts)

        self.last_person = person  # remember this is the last person we mentioned

        chosen_facts = (
            ""
            if len(novel_facts) == 0
            else random.sample(
                list(novel_facts), min(len(novel_facts), facts_to_mention)
            )
        )

        # print('chose facts: ', chosen_facts)
        # prefix = random.choice(template.prefixes)
        infix = random.choice(template.infixes)
        # print('infix: ', infix, type(infix))
        postfix = random.choice(template.postfixes)
        can_use_pronoun = True

        if chosen_facts != "":
            phrasings = []
            for i, fact in enumerate(chosen_facts):
                self.mentioned_facts.append(
                    fact
                )  # adds the fact to a list of what has already been mentioned about that person
                self.append_inverse_fact(fact)
                fact_strings = self.fact_to_str(person, can_use_pronoun, fact)[
                    ambiguity_level if i == 0 else "pronoun"
                ]
                phrasings += [(i > 0) * ", and also, ", random.choice(fact_strings)]
            # use an infix if there's more facts to come
            references = self.person_references(
                person, can_use_pronoun, not mentioned_first_time, infix=infix
            )[ambiguity_level]
            # print('phrasing: ', phrasings)
            utterance = "".join(
                [prefix, random.choice(references), *phrasings, postfix]
            )
        else:
            references = self.person_references(
                person, can_use_pronoun, not mentioned_first_time
            )[ambiguity_level]
            utterance = "".join([prefix, random.choice(references)])

        return utterance

    def introduce_multiple(self, people, key_person, ambiguity_level):
        """Introduces multiple people by referring to them either in name or as
        a group pronoun."""
        OTHER_REFS = {
            # if there's only one other person
            "single": [
                "Here is {name}. Oh, and... ",
                "Here is a picture of {name}. Also... ",
            ],
            # if there are many
            "multiple": [
                "Here are {people}. ",
                "This is a photo of {people}. ",
                "Here you can see {people}. ",
            ],
        }

        if ambiguity_level == "pronoun":  # if need be, dispatch with a pronoun
            return random.choice(INTRODUCTIONS["pronoun"])

        # otherwise process everyone in turn
        others = list(set(people) - set([key_person]))
        if len(others) == 1:
            ref = random.choice(OTHER_REFS["single"])
            result = ref.format(name=self.get_person_name(others[0]))
            others = []
        else:
            ref = random.choice(OTHER_REFS["multiple"])

            mentions = []
            for person in others:  # collect proper references for all people
                if person.data["full_name"] != key_person.data["full_name"]:
                    if person not in self.mentioned_people:
                        self.mentioned_people.append(person)
                    if ambiguity_level == "full_name":
                        mentions.append(person.data["full_name"])
                    else:
                        mentions.append(self.get_person_name(person))

            result = ref.format(people=", ".join(mentions))  # list them

        return result

    def append_inverse_fact(self, fact: Relation):
        """Placeholder for appending fact inverse to mentioned facts list. I.e.
        person1 -daughter-> person2 => person2 -mother-> person1."""
        INVERSE_RELATIONS = {  # maps the name of the relationship going the other way
            "spouse": {"male": "spouse", "female": "spouse"},
            "unmarried_partner": {
                "male": "unmarried_partner",
                "female": "unmarried_partner",
            },
            "sibling": {"male": "sibling", "female": "sibling"},
            "father": {"male": "child", "female": "child"},
            "mother": {"male": "child", "female": "child"},
            "child": {"male": "father", "female": "mother"},
            "friend": {"male": "friend", "female": "friend"},
            "colleague": {"male": "colleague", "female": "colleague"},
        }
        if fact.type in INVERSE_RELATIONS:
            inverse = INVERSE_RELATIONS[fact.type][fact.elem1.data["sex_or_gender"]]
            self.mentioned_facts.append(Relation(fact.elem2, inverse, fact.elem1))

    def get_person_name(self, person):
        """Helper function to extract a person's first name. Handles the possibility
        that the data only contained the full name."""
        try:
            name = person.data["name"][0]
        except:
            name = person.data["full_name"].split()[0]
        return name

    def person_references(self, person, can_pronoun, mentioned_before, infix=""):
        """Generates a set of valid person references, depending on whether the
        person has been mentioned, and can be refered to with a pronoun."""
        references = {None: []}
        references["full_name"] = [
            nphrase.format(name=person.data["full_name"], infix=infix)
            for nphrase in PREFIXES["name"]
        ]

        references["pronoun"] = [
            pphrase.format(
                pronoun="he" if person.data["sex_or_gender"] == "male" else "she",
                infix=infix,
            )
            for pphrase in PREFIXES["pronoun"]
        ]
        name = self.get_person_name(person)
        references["name"] = [
            nphrase.format(name=name, infix=infix) for nphrase in PREFIXES["name"]
        ]

        references[None] = (
            references["full_name"] + references["name"] + references["pronoun"]
        )
        return references

    def fact_to_str(self, person, can_pronoun, fact):
        try:
            name = person.data["name"][0]
        except:
            name = person.data["full_name"].split()[0]
        gender = person.data["sex_or_gender"]
        rel_name = GENDER_RELATION[gender][fact.type]
        rel_phrasings = self.relation_phrasings(person, fact)
        fstr = " ".join(
            [name, random.choice(rel_phrasings)]
        )  # maybe add more to this depending on the relation: a wife sounds strange
        result = {
            None: [fstr],
            "name": [fstr],
            "full_name": [
                " ".join([person.data["full_name"], random.choice(rel_phrasings)])
            ],
        }
        # print('fstr: ', fstr)
        if can_pronoun:
            result["pronoun"] = [
                " ".join(
                    [
                        "he" if person.data["sex_or_gender"] == "male" else "she",
                        random.choice(rel_phrasings),
                    ]
                )
            ]
        return result

    def relation_phrasings(self, person, rel):
        gender = person.data["sex_or_gender"]
        rel_name = GENDER_RELATION[gender][rel.type]
        other = rel.elem2.data["full_name"]
        if other == self.speaker.data["full_name"]:
            s = ""
            other = "my"
        else:
            s = "'s"
        phrasings = [
            tphrase.format(other=other, rel_name=rel_name, s=s)
            for tphrase in TYPE_PHRASINGS[rel.type]
        ]

        return phrasings


INTRODUCTIONS = {
    "pronoun": [
        "Here they are! ",
        "Oh, here they are. ",
        "Here are they. ",
        "Would you look at them. ",
    ]
}
PREFIXES = {
    "pronoun": ["Here {pronoun} is again. {infix}", "Here {pronoun} is, "],
    "name": [
        "Here's {name}. ",
        "Here's {name}! {infix}",
        "Here you see {name}. {infix}",
        "Here you see {name}. {infix}",
        "This picture shows {name}. {infix}",
        "Look, here's {name}. {infix}",
    ],
}

TYPE_PHRASINGS = {
    "spouse": ["is {other}{s} {rel_name}"],
    "friend": ["is a friend of {other}", "is {other}{s} friend"],
    "unmarried_partner": ["is {other}{s} {rel_name}", "is {other}{s} partner"],
    "sibling": ["is a {rel_name} of {other}", "is {other}'s {rel_name}"],
    "mother": ["is {other}{s} mother", "is {other}{s} mom"],
    "father": ["is {other}{s} father", "is {other}{s} dad"],
    "child": ["is {other}{s} {rel_name}"],
    "colleague": ["is a colleague of {other}", "works with {other}"],
}


def process_scenario(directory):
    """Creates an utterance generator from a directory containing a single scenario.

    directory - scenario directory. The assumed directory structure is:
      scenario -> picture -> picture JSON.

    Returns a Generator object capable of generating utterances based on information
    in a given scenario."""
    total_persons = []
    picture_jsons = get_picture_dicts(directory)
    for _, picture in picture_jsons.items():
        pic_persons = extract_persons(picture)
        total_persons += pic_persons
        speaker = extract_speaker(picture)
    gen = Generator(total_persons, picture_jsons, speaker)
    return gen


def narrate_scenario(scenario_path, ambiguities=[], people=[], facts_to_mention=[]):
    """Produces utterances to narrate an entire scenario, going picture-by-picture.

    scenario_path - path to scenario
    ambiguities - a list of ambiguities to use (one per scenario) or a single
      ambiguity level (None, 'full_name', 'name' or 'pronoun'). If a single ambiguity
      level is given instead of a list, it will be used for every scenario. If a
      list is passed, it must have the same length as the amount of pictures in the
      scenario, or be empty. If the passed list is empty, the difficulty of None
      will be used for every scenario. (default: [])
    people - list of people (one person per picture) to be mentioned and have
      facts about them listed. If empty, a random person in the picture will be
      chosen. If not empty, the list must have the same length as the amount of
      pictures. (default: [])
    facts_to_mention - list of counts of facts to mention by picture (if possible).
      If a single number, same amount of facts will be requested for each utterance.
      If a list, it must have the same length as the amount of pictures, or be
      empty. If an empty list is passed, a random number between 1 and 2 (inclusive)
      will be chosen per picture. If a single number is passed, that same amount
      of facts will be returned in every utterance (if possible). (default: [])

    Returns a dictionary of picture - utterance mappings.
    """
    generator = process_scenario(scenario_path)
    ix = 0
    narration = {}
    for picture_dir in os.listdir(scenario_path):
        for file_name in os.listdir(os.path.join(scenario_path, picture_dir)):
            if file_name.endswith(".json"):
                if type(ambiguities) == list and len(ambiguities) > 0:
                    ambiguity = ambiguities[ix]
                else:
                    ambiguity = None
                if type(people) == list and len(people) > 0:
                    person = people[ix]
                else:
                    person = None
                if type(facts_to_mention) == list and len(facts_to_mention) > 0:
                    facts = facts_to_mention[ix]
                else:
                    if type(facts_to_mention) == list:
                        facts = random.choice([1, 2])
                    else:
                        facts = facts_to_mention
                people_in_photo = extract_persons(
                    os.path.join(scenario_path, picture_dir, file_name), from_json=True
                )
                utterance = generator.generate_random_utterance(
                    Template([]), people_in_photo, ambiguity, person, facts
                )
                narration[file_name] = utterance
                ix += 1
    return narration
