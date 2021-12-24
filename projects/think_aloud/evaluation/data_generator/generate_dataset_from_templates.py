import random

PAIRED_OPTIONS = {
    "[VERB] [VERB-OBJ]": [
        "read [READABLE]",
        "drink [DRINKABLE]",
        "eat [FOOD]",
        "bake [FOOD]",
        "grab [OBJECT]",
        "buy [OBJECT]",
        "play sports",
    ],
    "[VERBS] [VERBS-OBJ]": [
        "reads [READABLE]",
        "drinks [DRINKABLE]",
        "eats [FOOD]",
        "bakes [FOODS]",
        "grabs [OBJECT]",
        "buys [OBJECT]",
    ],
    "[GERUND] [GERUND-OBJ]": [
        "reading [READABLE]",
        "walking [ANIMAL]",
        "cleaning [OBJECT]",
        "baking [FOODS]",
        "watching movies",
    ],
}

SINGLE_OPTIONS = {
    "[NAME]": ["Mike", "Thomas", "James", "Serena", "Alex", "Bob", "Charlie"],
    "[FOOD]": ["banana", "sandwich", "hamburger", "tomato", "cookie"],
    "[FOODS]": ["food", "bananas", "pasta", "sushi", "dessert", "cakes"],
    "[DRINKABLE]": ["drink", "cola", "beer", "glass of water", "juice", "water"],
    "[ACT]": ["talk", "fly", "run", "go", "shoot", "exercise", "swim"],
    "[ACTIVITY]": [
        "talking",
        "reading",
        "exercising",
        "walking",
        "swimming",
        "running",
        "learning",
    ],
    "[OBJECT]": [
        "laptop",
        "chair",
        "bottle",
        "camera",
        "robot",
        "cup",
        "tree",
        "book",
        "car",
    ],
    "[OBJECTS]": [
        "laptops",
        "chairs",
        "drinks",
        "cameras",
        "robots",
        "trees",
        "books",
        "car",
    ],
    "[READABLE]": ["book", "newspaper", "story", "paper"],
    "[READABLES]": ["books", "newspapers", "stories", "papers"],
    "[KIN]": ["mother", "father", "brother", "sister", "nephew", "cousin", "friend"],
    "[ABSTRACT]": ["sports", "football", "fashion", "coffee", "money"],
    "[MOVIE]": ["the Titanic", "the Lion King", "Star Wars", "Toy Story", "Jumanji"],
    "[ANIMALS]": ["people", "dogs", "cats", "birds", "horses", "spiders", "rabbits"],
    "[ANIMAL]": ["human", "dog", "cat", "bird", "horse", "spiders", "rabbit"],
    "[HUMAN]": ["person", "human", "man", "woman", "child", "adult"],
    "[EVENT]": ["birthday", "graduation", "party", "honeymoon", "wedding"],
    "[CITY]": ["Amsterdam", "London", "Berlin", "Paris", "Rome", "Athens"],
    "[COUNTRY]": ["the Netherlands", "England", "Germany", "France", "Italy", "Greece"],
    "[LOCATION]": ["room", "university", "building", "house", "kitchen"],
    "[LOCATION-PROP]": ["fountain", "cinema", "restroom", "skyline"],
    "[COLOR]": ["blue", "red", "green", "black", "brown", "purple"],
    "[NUMBER]": ["two", "three", "four", "five", "six", "all"],
    "[QUALITY]": [
        "beautiful",
        "healthy",
        "gorgeous",
        "happy",
        "polite",
        "brave",
        "scary",
    ],
    "[INSTITUTION]": ["university", "school", "college"],
    "[PROFESSIONS]": [
        "teacher",
        "accountant",
        "barber",
        "waiter",
        "pilot",
        "athlete",
        "artist",
    ],
}


def generate_dataset(path, out, iters):
    """Generates a dataset of conversations from a file of templates.

    params
    str path:  path to template file
    str out:   path to store dataset into
    int iters: number of random instances of each template to generate

    returns: None
    """
    lines = set()
    for _ in range(iters):

        with open(path, "r") as file:
            for line in file:

                line = line.strip()

                # Fill pairs of slots (to solve verb agreement)
                for slot_pair, slot_pair_values in PAIRED_OPTIONS.items():
                    slot1, slot2 = slot_pair.split(" ")
                    if slot1 in line and slot2 in line:
                        pair_values = random.choice(slot_pair_values).split(" ")
                        line = line.replace(slot1, pair_values[0])
                        line = line.replace(slot2, pair_values[1])

                # Do left over slots
                for slot, slot_values in SINGLE_OPTIONS.items():
                    if slot in line:
                        line = line.replace(slot, random.choice(slot_values))

                lines.add(line)

    with open(out, "w") as file:
        file.write("\n".join(list(lines)))


if __name__ == "__main__":
    generate_dataset("templates.txt", "eval_contexts2.txt", iters=5)
