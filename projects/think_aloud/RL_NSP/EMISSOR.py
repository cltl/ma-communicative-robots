""" Filename:     EMISSOR.py
    Author(s):    Thomas Bellucci
    Description:  Wrapper around cltl-EMISSOR to incorporate the EMISSOR
                  platform into the RLChatbot defined in Chatbot.py.
    Date created: Nov. 11th, 2021
"""

import os
import sys
import time
from datetime import datetime
from random import getrandbits

import requests

sys.path.insert(0, "cltl-EMISSOR")

from emissor.persistence import ScenarioStorage
from emissor.representation.scenario import Modality, TextSignal


class EMISSOR:
    def __init__(self, speaker):
        """Sets up EMISSOR and its file structure.

        params
        str speaker: name of the speaker

        returns: None
        """
        # Set location and agents
        self.__place_id = getrandbits(8)
        self.__location = requests.get("https://ipinfo.io").json()
        self.__agent = "Leolani1"
        self.__speaker = speaker
        self.__speaker_id = self.__speaker.lower()

        # Name scenario ('-' used as ':' is forbidden in Windows filenames)
        self.__scenario_id = datetime.today().strftime("%Y-%m-%d-%H-%M-%S")

        # Set up folder structure in root directory
        root_dir = os.path.dirname(os.path.realpath(__file__))
        self.__scenario_path = os.path.abspath(os.path.join(root_dir, "scenarios"))

        if not os.path.exists(self.__scenario_path):
            os.mkdir(self.__scenario_path)
            print("Created 'scenarios' for storing scenarios", self.__scenario_path)

        # Create the scenario folder, the json files and a scenarioStorage and scenario in memory
        time_id = int(time.time() * 1e3)
        self.__storage = self.create_scenario(self.__scenario_path, self.__scenario_id)
        self.__scenario = self.__storage.create_scenario(
            self.__scenario_id, time_id, None, self.__agent
        )

    @staticmethod
    def create_scenario(scenario_path, scenario_id):
        """Creates a scenario to store text signals into.

        params
        str scenario_path: Absolute path to folder to store the scenario into
        str scenario_id:   Identifier of current scenario

        returns: ScenarioStorage object
        """
        # Create scenario storage
        storage = ScenarioStorage(scenario_path)

        # Create text signal track in './y-m-d-H-M-S/text'.
        scenario_path = os.path.abspath(os.path.join(storage.base_path, scenario_id))
        text_sig_path = os.path.abspath(
            os.path.join(scenario_path, Modality.TEXT.name.lower())
        )
        os.mkdir(scenario_path)
        os.mkdir(text_sig_path)
        print(f"Directories for {scenario_id} created in {storage.base_path}")

        return storage

    def add_text_signal(self, text):
        """Creates a text signal to be stored in EMISSOR.

        params
        str text: Text to store in the file structure

        returns: None
        """
        # Add timestamped text signal to scenario
        time_id = int(time.time() * 1e3)
        signal = TextSignal.for_scenario(
            self.__scenario.id, time_id, time_id, [], text, []
        )
        self.__scenario.append_signal(signal)

    def save(self):
        """Writes the EMISSOR file structure to disk.

        returns: None
        """
        self.__scenario.scenario.ruler.end = int(time.time() * 1e3)
        self.__storage.save_scenario(self.__scenario)
