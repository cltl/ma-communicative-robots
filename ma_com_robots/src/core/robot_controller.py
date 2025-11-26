'''
Main Robot Controller - Orchestrates all components
'''
from src.perception.room_classifier import RoomClassifier
from src.navigation.exploration_mapper import ExplorationMapper
from src.navigation.object_searcher import ObjectSearcher
from src.language.user_input_processor import UserInputProcessor
from src.language.text_similarity import TextSimilarity
from src.perception.image_descriptor import ImageDescriptor

class RobotController:
    def __init__(self, emissor_path, scene, use_openai=False, api_key=None):
        # TODO: Implement initialization
        pass

    def run(self):
        # TODO: Implement main pipeline
        pass
