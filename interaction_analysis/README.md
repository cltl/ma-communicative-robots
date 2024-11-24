# Annotation and Analysis of interactions stored in EMISSOR format
This repository explains how to analyse and evaluate agent interactions that have been captured through EMISSOR (Baez et al 2021). EMISSOR is a platform that captures an interaction as a multimodal stream of signals that are grounded in time and space. These signals are produced and perceived by agents interacting with each other and their environment. Signals can be captured by sensors (image, audio) or through chatting (text). Sensor-based signals can also represent conversations, including gestures and gaze.

Analysing and evaluating interactions is complex. This is due to the fact that every interaction is unique and impossible to reproduce, there are many different ways to interact even for a similar goal and people value different aspects of the interation. Human evaluation is still considered the best way of evaluating and analysing interaction but researchers have been searching for automatic ways as well (Deriu et al. 2021, Yeh et al. 2021).

We provide two notebooks that show how to analyse and evaluate interactions in different ways:

1. emissor_scenario_annotation.ipynb
2. emissor_scenario_evaluation.ipynb

The first notebook shows how various annotations can be added to the the sequence of signals. By adding annotations to signals, the sequence of interactions can be analysed in more details. We have annotators for text and image signals, but here focus on annotating text signals, which are the utterances of the interlocuters of a conversation. We provide annotators for dialogue act classification, sentiment/emotion annotation, natural language processing annotation and likelihood or perplexity of utterances in a sequence according to large language models.

Interactions captured in EMISSOR and annotated for various properties can be analysed and evaluated in various ways. In the second notebook, we explain a number of different ways to analyse interactions given the kind of annotations that are available. 

## Prerequisites

- create a virtual enviroment and activate it
- install the required modules through:
- pip install -r requirements.txt
- install the spaCY language model for the language of the communication:

```python -m spacy download en_core_web_sm```
  
## Types of analysis:

- statistical evaluation
- conversation plot
- likelihood evaluation
- graph based evaluation
- manual evaluation
- reference evaluation

## Reference

When using this repository please cite:

@article{santamaria2021emissor,
  title={EMISSOR: A platform for capturing multimodal interactions as Episodic Memories and Interpretations with Situated Scenario-based Ontological References},
  author={Santamaria, Selene Baez and Baier, Thomas and Kim, Taewoon and Krause, Lea and Kruijt, Jaap and Vossen, Piek},
  journal={arXiv preprint arXiv:2105.08388},
  year={2021}
}

Deriu, Jan, Alvaro Rodrigo, Arantxa Otegi, Guillermo Echegoyen, Sophie Rosset, Eneko Agirre, and Mark Cieliebak. "Survey on evaluation methods for dialogue systems." Artificial Intelligence Review 54, no. 1 (2021): 755-810

Yeh, Yi-Ting, Maxine Eskenazi, and Shikib Mehri. "A comprehensive assessment of dialog evaluation metrics." arXiv preprint arXiv:2106.03706 (2021).
and can contain signals in different modalities.
