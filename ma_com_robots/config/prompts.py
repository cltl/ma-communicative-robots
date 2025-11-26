# OpenAI prompts
NORMALIZATION_PROMPT = '''
Rewrite this description to match AI2Thor object names:
- portrait/picture -> Painting
- couch -> Sofa
- tv -> Television
- coffee maker -> CoffeeMachine

Original: "{user_input}"

Provide only the normalized version, keep it concise.
'''

ROOM_CLASSIFICATION_PROMPT = '''
These objects are visible: {objects}

What room type is this? Answer with ONLY one of:
- kitchen
- bathroom
- bedroom
- living room
'''

OBJECT_DESCRIPTION_PROMPT = '''
Describe this object and its surroundings in detail.
Focus on:
- Object type and color
- Position (left/right, high/low, on floor/table)
- Nearby objects
- Any distinctive features
'''
