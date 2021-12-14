""" Filename:     chatbots.py
    Author(s):    Thomas Bellucci
    Description:  Implementation of the Chatbot based on a Leolani backend.
                  The implementation uses the knowledge extraction modules
                  of Leolani for parsing, the Brain for storage/querying
                  of triples and modified LenkaRepliers for phrasing.                   
    Date created: Nov. 11th, 2021
"""

import os
from datetime import date
from pathlib import Path
from pprint import pprint
from random import choice

# Set up Java PATH (required for Windows)
os.environ["JAVAHOME"] = "C:/Program Files/Java/jre1.8.0_311/bin/java.exe"

from cltl.brain.long_term_memory import LongTermMemory
from cltl.brain.utils.helper_functions import brain_response_to_json
from cltl.combot.backend.api.discrete import UtteranceType
from cltl.reply_generation.data.sentences import (GOODBYE, GREETING, SORRY,
                                                  TALK_TO_ME)
# Pip-installed ctl repositories
from cltl.triple_extraction.api import Chat, UtteranceHypothesis
from EMISSOR import EMISSOR
# Modified reply_generation
from repliers import LenkaReplier, NSPReplier, RLReplier
from utils.chatbot_utils import capsule_for_query, triple_for_capsule


class Chatbot:
    def __init__(self, speaker, mode, savefile=None):
        """Sets up a Chatbot with a Leolani backend.

        params
        str speaker:  name of speaker
        str mode:     method used to select thoughts: ['Lenka', 'RL', 'NSP']
        str savefile: path to NSP model or utilities file needed by the replier.

        returns: None
        """
        # Set up Leolani backend modules
        self.__address = "http://localhost:7200/repositories/sandbox"
        self.__brain = LongTermMemory(
            address=self.__address, log_dir=Path("logs"), clear_all=True
        )
        self.__chat = Chat(speaker)
        self.__emissor = EMISSOR(speaker)

        self.__mode = mode
        self.__savefile = savefile
        self.__turns = 0

        if mode == "RL":
            self.__replier = RLReplier(self.__brain, savefile)
        elif mode == "NSP":
            self.__replier = NSPReplier(None, savefile)
        elif mode == "Lenka":
            self.__replier = LenkaReplier(None, None)
        else:
            raise Exception("unknown replier mode %s (choose RL, NSP or Lenka)" % mode)

    def close(self):
        """Ends interaction and writes all learnt thought utility files
        (if method='RL') and EMISSOR files to disk.

        returns: None
        """
        # Writes EMISSOR structure and (optionally) a utilities JSON to disk
        if self.__savefile and self.__mode == "RL":
            self.__replier.thought_selector.save(self.__savefile)
        self.__emissor.save()

    @property
    def replier(self):
        """Provides access to the replier."""
        return self.__replier

    @property
    def greet(self):
        """Generates a random greeting."""
        string = choice(GREETING) + " " + choice(TALK_TO_ME)
        self.__emissor.add_text_signal(string)
        return string

    @property
    def farewell(self):
        """Generates a random farewell message."""
        string = choice(GOODBYE)
        self.__emissor.add_text_signal(string)
        return string

    def __parse(self, input_):
        """Takes an input utterance from the user and returns a capsule
        with which to store and/or query the Brain.

        params
        str input_:  input of the user

        returns:  capsule dict with utterance and context
        """
        self.__turns += 1

        # Extract triple from input string
        self.__chat.add_utterance([UtteranceHypothesis(input_, 1.0)])
        self.__chat.last_utterance.analyze()
        utt = self.__chat.last_utterance

        if utt.triple is None:  # Parsing failure?
            return None

        # Create capsule from parse
        capsule = {
            "chat": 1,
            "turn": self.__turns,
            "author": self.__chat.speaker,
            "utterance": utt.transcript,
            "utterance_type": utt.type,
            "position": "{}-{}".format(0, len(utt.transcript) - 1),
            "context_id": 247,
            "date": date.today(),
            "place": "Piek's office",
            "place_id": 106,
            "country": "Netherlands",
            "region": "North Holland",
            "city": "Amsterdam",
            "objects": [],
            "people": [],
        }

        # Add triple and perspectives to capsule
        capsule.update(triple_for_capsule(utt.triple))
        if utt.perspective is not None:
            capsule["perspective"] = utt.perspective

        print("\nCAPSULE")
        pprint(capsule)
        print()
        return capsule

    def respond(self, input_, return_br=False):
        """Parses the user input (to extract triples and perspectives), queries
        and/or updates the brain and returns a reply by consulting the replier.

        params
        str input_:     input utterance of the user, e.g. a response to a Thought
        bool return_br: whether to return to brain response alongside the reply

        returns: reply to input
        """
        capsule = self.__parse(input_)
        self.__emissor.add_text_signal(input_)

        # ERROR
        say, brain_response = None, None
        if capsule is None:
            say = choice(SORRY) + " I could not parse that. Can you rephrase?"

        # QUESTION
        elif capsule["utterance_type"] == UtteranceType.QUESTION:
            # Query Brain -> try to answer
            brain_response = self.__brain.query_brain(capsule_for_query(capsule))
            brain_response = brain_response_to_json(brain_response)

            if isinstance(self.__replier, RLReplier):
                self.__replier.reward_thought()

            say = self.__replier.reply_to_question(brain_response)

        # STATEMENT
        elif capsule["utterance_type"] == UtteranceType.STATEMENT:
            # Update Brain -> communicate a thought
            brain_response = self.__brain.update(
                capsule, reason_types=True, create_label=True
            )
            brain_response = brain_response_to_json(brain_response)

            if isinstance(self.__replier, RLReplier):
                self.__replier.reward_thought()

            say = self.__replier.reply_to_statement(brain_response)

        self.__emissor.add_text_signal(say)

        if return_br:
            return say, brain_response
        return say
