import abc
import uuid
import emissor
import cltl.combot
from emissor.persistence import ScenarioStorage
from emissor.persistence.persistence import ScenarioController
from emissor.representation.scenario import Modality, Signal, Scenario, ScenarioContext, Annotation
from emissor.representation.scenario import TextSignal, ImageSignal
from cltl.combot.event.emissor import AnnotationEvent, TextSignalEvent, ImageSignalEvent
from cltl.combot.infra.time_util import timestamp_now

class LeolaniChatClient():

    def __init__(self, emissor_path:str, agent="Leolani", human="Alice"):
        """ Creates a scenario and adds signals
        params: emissor_path location on disk to store the scenarios
        returns: None
        """
        signals = {
            Modality.TEXT.name.lower(): "./text.json",
        }
        self._agent=agent
        self._human=human
        self._scenario_storage = ScenarioStorage(emissor_path)
        self._scenario_context =  ScenarioContext(agent)
        scenario_start = timestamp_now()
        self._scenario =self._scenario_storage.create_scenario(str(uuid.uuid4()), scenario_start, None, self._scenario_context, signals) 

    def _add_utterance(self, speaker_name, utterance):
        signal = TextSignal.for_scenario(self._scenario, timestamp_now(), timestamp_now(), None, utterance)
        TextSignalEvent.add_agent_annotation(signal, speaker_name)
        self._scenario.append_signal(signal)

    def _add_image(self, speaker_name, signal):
        signal = ImageSignal.for_scenario(self._scenario, timestamp_now(), timestamp_now(), None, utterance)
        ImageSignalEvent.create(signal)
        self._scenario.append_signal(signal)

        segment = MultiIndex(signal.ruler.container_id, bbox)
        annotation_person = Annotation(AnnotationType.PERSON.name, Person(str(uuid.uuid4()), name, age, gender), MeldFaceProcessor.name, int(time.time()))
        annotation_representation = Annotation(AnnotationType.REPRESENTATION.name, representation.tolist(), MeldFaceProcessor.name, int(time.time()))
        mention = Mention(str(uuid.uuid4()), [segment], [annotation_person, annotation_representation])

        signal.mentions.append(mention)
    
    def _save_scenario(self):
        self._scenario_storage.save_scenario(self._scenario)


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
