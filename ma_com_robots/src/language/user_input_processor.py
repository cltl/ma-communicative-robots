'''
User Input Processor - Normalizes user descriptions to AI2Thor format
'''
class UserInputProcessor:
    def __init__(self, use_openai=False, api_key=None):
        self.use_openai = use_openai
        self.api_key = api_key

        # AI2Thor naming mappings
        self.term_mappings = {
            'portrait': 'Painting',
            'picture': 'Painting',
            'couch': 'Sofa',
            'tv': 'Television',
            # TODO: Add more mappings
        }

    def normalize_description(self, user_input):
        '''Normalize user terms to match AI2Thor names'''
        # TODO: Implement normalization
        # Can use GPT-4o-mini or rule-based
        pass

    def extract_object_and_room(self, user_input):
        '''Extract target object type and room type'''
        # TODO: Implement extraction
        pass

    def confirm_with_user(self, extracted_info):
        '''Generate confirmation message'''
        # TODO: Implement
        pass
