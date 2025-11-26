import abc
import uuid
import numpy as np
from enum import Enum, auto
from dataclasses import dataclass
from typing import Generic, TypeVar, List, Optional
import time
import os
import cltl.combot
from camera import Bounds, CameraResolution, Object, Image
from emissor.persistence import ScenarioStorage
from emissor.persistence.persistence import ScenarioController
from emissor.representation.container import MultiIndex
from emissor.representation.scenario import Modality, Signal, Scenario, ScenarioContext, Annotation, Mention
from emissor.representation.scenario import TextSignal, ImageSignal
from cltl.combot.event.emissor import AnnotationEvent, TextSignalEvent, ImageSignalEvent, Agent
from cltl.combot.infra.time_util import timestamp_now
from typing import Optional


class Action(Enum):
    MoveAhead = auto()
    MoveBack = auto()
    MoveLeft = auto()
    MoverRight = auto()
    RotateRight =auto()
    RotateLeft = auto()
    LookUp =auto()
    LookDown =auto()
    Crouch = auto()
    Stand = auto()
    Teleport = auto()
    TeleportFull = auto()
    Look = auto()

# @dataclass
# class ApplicationContext(ScenarioContext):
#     speaker: Agent


@dataclass
class ApplicationContext(ScenarioContext):
    agent: Agent
    speaker: Agent

class LeolaniChatClient():

    def __init__(self, emissor_path:str, agent="Leolani", human="Alice"):
        """ Creates a scenario and adds signals
        params: emissor_path location on disk to store the scenarios
        returns: None
        """
        signals = {
            Modality.TEXT.name.lower(): "./text.json",
            Modality.IMAGE.name.lower(): "./image.json",
        }
        self._agent= Agent(name=agent, uri=f"http://cltl.nl/leolani/world/{agent.lower()}")
        self._human= Agent(name=human, uri=f"http://cltl.nl/leolani/world/{human.lower()}")
        self._scenario_storage = ScenarioStorage(emissor_path)
        self._scenario_context =  ApplicationContext(self._agent, self._human)
        scenario_start = timestamp_now()
        self._scenario_id = str(uuid.uuid4())
        self._scenario_controller =self._scenario_storage.create_scenario(self._scenario_id, scenario_start, None, self._scenario_context, signals)
        self._scenario_path = os.path.join(emissor_path, self._scenario_id)
        self._image_path = os.path.join(self._scenario_path, "image")
        if not os.path.exists(self._image_path):
            os.mkdir(self._image_path)

    def _add_utterance(self, speaker_name, utterance):
        signal = TextSignal.for_scenario(self._scenario_controller, timestamp_now(), timestamp_now(), None, utterance)
        TextSignalEvent.add_agent_annotation(signal, speaker_name)
        self._scenario_controller.append_signal(signal)

    def _add_action(self, action:Action):
        signal = TextSignal.for_scenario(self._scenario_controller, timestamp_now(), timestamp_now(), None, action.name)
        TextSignalEvent.add_agent_annotation(signal, "ACTION")
        self._scenario_controller.append_signal(signal)

    def _add_image(self, objectName, objectType, bounds, image):
        imageFilePath = os.path.join(self._image_path, objectName+".jpg")
        image.save(imageFilePath)
        # TODO SYSTEM_VIEW is the angle of the camera, this is for Leolain
        # TODO resolution of the camera needs to be chosen
        SYSTEM_VIEW = Bounds(-0.55, -0.41 + np.pi / 2, 0.55, 0.41 + np.pi / 2)
        resolution = CameraResolution.VGA

        # TODO image as numpy array is needed, depth array if available
        image_array = np.zeros((resolution.height, resolution.width, 3), dtype=np.uint8)
        depth_array = np.zeros((resolution.height, resolution.width), dtype=np.uint8)
        image = Image(image_array, SYSTEM_VIEW.to_diagonal(), depth_array)
        signal = ImageSignal.for_scenario(self._scenario_controller.id, timestamp_now(), timestamp_now(), imageFilePath, image.bounds.to_diagonal())
        # Bounds() takes x_0, x_1, y_0, y_1 as arguments, to_diagonal converts it to x_0, y0, x_1, y_1 
        # Dummy bounding box for the segment, to be replaced by more real bounding box
        segment = MultiIndex(signal.ruler.container_id, Bounds(bounds['x']-1, bounds['x']+1, bounds['y']-1,bounds['y']+1).to_diagonal())
        annotation_data = {}
        label_annotation = Annotation('ObjectType', objectType, "Ai2Thor", int(time.time()))
        name_annotation = Annotation('ObjectIdentity',objectName, "Ai2Thor", int(time.time()))
        mention = Mention(str(uuid.uuid4()), [segment], [label_annotation, name_annotation])
        signal.mentions.append(mention)
        self._scenario_controller.append_signal(signal)

    def _save_scenario(self):
        scenario_end = timestamp_now()
        self._scenario_controller.scenario.ruler.end = scenario_end
        self._scenario_storage.save_scenario(self._scenario_controller)


if __name__ == "__main__":
    emissor_path = "./emissor"
    human = "Alice"
    agent="Leolani"
    leolaniClient = LeolaniChatClient(emissor_path=emissor_path, agent=agent, human=human)
    utterance = "Hello world"
    leolaniClient._add_utterance(agent, utterance)
    utterance = "Hello agent"
    leolaniClient._add_utterance(human, utterance)
    leolaniClient._save_scenario()    
