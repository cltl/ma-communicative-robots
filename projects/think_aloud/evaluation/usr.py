""" Filename:     USR.py
    Author(s):    Thomas Bellucci
    Description:  Re-implementation of the USR dialogue evaluation framework. This implementation is limited
                  to the MCtx score computed by USR as this metric is most meaningful in the context of the project.
    Date created: Dec. 4th, 2021
"""

import numpy as np
import torch
from transformers import (RobertaConfig, RobertaForSequenceClassification,
                          RobertaTokenizer)


class USR:
    def __init__(self, path=None):
        """Load pretrained and finetuned RoBERTa model for ctx.

        params
        str path: path to stored model or None

        returns: None
        """
        self.__config = RobertaConfig.from_pretrained("adamlin/usr-topicalchat-ctx")
        self.__tokenizer = RobertaTokenizer.from_pretrained(
            "adamlin/usr-topicalchat-ctx"
        )

        if path is not None:
            self.__model = RobertaForSequenceClassification.from_pretrained(
                path, config=self.__config
            )
        else:
            self.__model = RobertaForSequenceClassification.from_pretrained(
                "adamlin/usr-topicalchat-ctx", config=self.__config
            )

        self.__device = (
            torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
        )
        self.__model.to(self.__device)

    def MCtx(self, context, response):
        """Scores an input consisting of a (context, response) pair using RoBERTa.

        params
        str context:  the context strings
        sre response: response to the context

        returns: score
        """
        # Concatenates and encodes context-response pair
        input_sequence = context + " [SEP] " + response
        inputs = self.__tokenizer(input_sequence, return_tensors="pt")

        inputs["input_ids"] = inputs["input_ids"].to(self.__device)
        inputs["attention_mask"] = inputs["attention_mask"].to(self.__device)

        # Feeds encoded input through network
        outputs = self.__model(**inputs)
        logits = outputs.logits.detach().cpu().numpy()

        # Returns the softmax score of the positive class, i.e. P(y=1|context, response)
        outputs = np.exp(logits) / np.sum(np.exp(logits))
        return outputs[0][1]
