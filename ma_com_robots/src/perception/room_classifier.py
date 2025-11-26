# Room classification
'''
Room Classifier - Determines room type and verifies room instance
'''
class RoomClassifier:
    def __init__(self, controller, use_openai=False, api_key=None):
        self.controller = controller
        self.use_openai = use_openai
        self.api_key = api_key

    def classify_room_type(self):
        '''Classify current room type based on visible objects'''
        # TODO: Implement
        pass

    def verify_room_instance(self, user_description):
        '''Check if we're in the correct room instance'''
        # TODO: Implement
        pass

    def get_visible_objects(self):
        '''Get all visible object types'''
        # TODO: Implement
        pass
