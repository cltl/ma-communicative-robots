# emissor_evaluation: analysing conversations in EMISSOR

This module analyses and evaluates conversations that are saved in the [EMISSOR](https://github.com/leolani/emissor) format, such as the interactions with the LEOLANI platform. Each analysis scores the conversation turn by turn, saves the scores in a CSV file and can be plotted over the conversation, so that you can see where a conversation goes well and where it goes wrong.

| Folder | Analysis | Notebook | Score |
| --- | --- | --- | --- |
| ```likelihood``` | likelihood of each turn given the previous context, with a masked language model | ```likelihood_analysis.ipynb``` | ```llh``` (0 to 1) |
| ```llm_as_judge``` | coherence of each agent response, judged by a generative LLM | ```llm_as_a_judge_llama_cpp.ipynb```, ```llm_as_a_judge_ollama_cloud.ipynb``` | ```llm_coherence``` (0 to 1) |
| ```dialogue_act``` | dialogue act of each turn, as a positive, negative or neutral move | ```dialogue_act_analysis.ipynb``` | ```da_score``` (-5 to +5) |
| ```emotion``` | emotion and sentiment of each turn | ```emotion_analysis.ipynb``` | ```emotion_score``` (-5 to +5), ```sentiment_score``` (-1 to 1) |
| ```graph``` | properties of the episodic knowledge graph built from the conversation | ```graph_analysis.ipynb``` | graph metrics per turn |
| ```human``` | human assessment of each turn on a Likert scale | ```manual_evaluation.ipynb``` | 1 to 5 per criterion |
| ```plots``` | plots of the scores over the turns of a conversation | ```plot_analysis_from_csv.ipynb```, ```plot_analysis_from_annotation.ipynb```, ```metrics_plotting.ipynb``` | |
| | correlation between the scores of different analyses | ```correlate.ipynb``` | |
| ```emissor``` | helper functions to read scenarios, text signals and image signals | | |

## EMISSOR scenarios

EMISSOR stores each interaction as a **scenario** in its own folder, named with the identifier of the scenario. The folder has a scenario JSON file and the signals of the interaction: text, images and audio, aligned on a shared temporal ruler. The text signals are the turns of the conversation, each with an identifier and the speaker. A scenario can also have an ```rdf``` folder with the knowledge extracted from the conversation as ```.trig``` files.

The folder ```data/emissor``` has three example scenarios. To analyse your own interactions, set the ```EMISSOR``` variable in a notebook to the folder with your scenarios and ```SCENARIO``` to the identifier of the scenario. Some notebooks process all scenarios in the folder with ```SCENARIOS = get_scenario_ids(EMISSOR)```.

The helper functions in ```emissor/```:

* ```emissor_util.py```: ```get_text_signals_from_a_scenario``` loads the text signals of a scenario and ```get_speaker_from_text_signal``` gets the speaker of a turn
* ```text_signal.py``` and ```image_signal.py```: get the annotations of a signal, such as the dialogue act, emotion, likelihood, faces, objects and identities
* ```scenario_check.py```: checks whether a scenario folder has a scenario file, text, images and RDF

## The CSV format

Every analysis saves its scores in the ```evaluation``` subfolder of the scenario as ```<scenario_id>_<analysis>_evaluation.csv```, separated by ```;```. Each row is a turn, with the columns:

* ```Turn```: the identifier of the text signal of the turn
* ```Speaker```: the speaker of the turn, e.g. ```LEOLANI``` or ```SPEAKER```
* ```Response```: the utterance
* one or more columns with the scores and other values of the analysis

For example, for the LLM as a judge:

```
Turn;Speaker;Response;llm_coherence;llm_explanation
763b7c2a-...;LEOLANI;What's up? Do you want to talk to me John?;0.0;
368658d4-...;SPEAKER;Yes;0.6;The response is a follow-up question that ...
```

You can write your own analysis that produces a CSV file in the same format and plot or correlate it in the same way. The [task evaluation](../task_evaluation/README.md) of the day interviewer also saves its turn evaluation in this format.

## The analyses

### Likelihood

```likelihood/likelihood_analysis.ipynb``` scores how likely each turn is given the previous turns, following the reference-free USR metric (Mehri & Eskenazi 2020). Each word of the turn is masked in turn and a masked language model predicts it from the context and the rest of the turn; the likelihood ```llh``` is the average probability of the actual words, where a word that is not among the top predictions counts as 0. The CSV also has ```model_turn```, the turn with the most probable tokens, and ```max_llh```, the likelihood of that turn, which is the upper ceiling of the model.

The model is ```google-bert/bert-base-uncased``` by default and is downloaded from huggingface.co the first time. You can replace it with another masked language model, e.g. ```FacebookAI/roberta-base```, or with a local copy of the USR model.

Output: ```<scenario_id>_likelihood_evaluation.csv```, and ```all_scenarios_likelihood_evaluation.csv``` in the ```EMISSOR``` folder.

### Coherence with an LLM as a judge

The LLM-as-a-judge notebooks ask a generative LLM to give a coherence score from 0.0 to 1.0 to each response of the agent given the previous turns, with an explanation. The prompt takes into account that the agent can be proactive and ask questions to the user as well.

* ```llm_as_a_judge_llama_cpp.ipynb``` uses a local model served by llama.cpp. Start the server before running the notebook, see the [installation in the main README](../../../README.md#3-install-llamacpp). The address of the server is set in ```LLAMA_CPP_URL```, ```http://localhost:8080/v1``` by default. Output: ```<scenario_id>_llm_judge_llama_cpp_evaluation.csv```.
* ```llm_as_a_judge_ollama_cloud.ipynb``` uses a bigger model, ```gpt-oss:120b```, in the [ollama cloud service](https://ollama.com/cloud). It needs an API key, which you can get from [docs.ollama.com/cloud](https://docs.ollama.com/cloud#authentication); usage is free but limited per hour and per week. Put the key in a text file and set ```path``` in the notebook to that file, and never commit the key to git. Output: ```<scenario_id>_llm_judge_evaluation.csv```.

Both files have the columns ```llm_coherence``` and ```llm_explanation```.

### Dialogue acts

```dialogue_act/dialogue_act_analysis.ipynb``` tags every turn with one of the 23 dialogue acts of MIDAS (Yu & Yu 2021), such as ```open_question_factual```, ```pos_answer```, ```opinion``` or ```nonsense```, given the previous turn. The tagger is ```MidasDialogTagger``` in ```midas_classifier.py``` with the model ```CLTL/midas-da-xlmroberta``` from huggingface.co.

Each dialogue act also gets a score from -5 to +5 in ```da_score```, which tells how positive the dialogue act is for the conversation. The scores come from the scales ```DIALOGUE_ACT_NEG_SCALE```, ```DIALOGUE_ACT_NEUTRAL_SCALE``` and ```DIALOGUE_ACT_POS_SCALE``` in ```midas_classifier.py```; change them to change the scoring.

Output: ```<scenario_id>_dialogue_act_evaluation.csv```.

### Emotions

```emotion/emotion_analysis.ipynb``` tags every turn with the emotions of GO Emotions (Demszky et al. 2020), 27 emotion categories plus neutral, with the model ```bhadresh-savani/bert-base-go-emotion``` from huggingface.co. The GO emotions are also mapped to the six Ekman emotions and to a sentiment. For each turn, the CSV has the strongest GO emotion, Ekman emotion and sentiment with their scores, an ```emotion_score``` from -5 to +5 for how positive or negative the GO emotion is (the scales are in ```emotion_types.py```) and a ```sentiment_score``` from -1 to 1.

Output: ```<scenario_id>_emotion_evaluation.csv```.

### Knowledge graph metrics

```graph/graph_analysis.ipynb``` scores the conversation on the episodic knowledge graph that the agent builds from it. It needs a scenario with an ```rdf``` folder with the ```.trig``` files of the conversation. For each turn, the graph so far is loaded and measured with three groups of metrics:

* **group A**, ```graph_measures.py```: mathematical properties of the graph, such as the number of nodes and edges, the average degree, the centrality entropy and the sparseness
* **group B**, ```ontology_measures.py```: properties of the ontology, such as the number of classes, properties and instances
* **group C**, ```brain_measures.py```: properties of the episodic knowledge, such as the number of triples, claims, perspectives, mentions, sources and conflicts

The full list of metrics is in ```constants.py```, the notebook selects some of them. ```map_rdf_files.py``` maps the ```.trig``` files to the turns of the conversation and saves the mapping as ```turn_to_trig_file.json``` in the scenario folder.

Output: ```<scenario_id>_graph_evaluation.csv``` and a plot per metric in the ```evaluation``` folder. It can also be run from the root of the repository:

```bash
python -m src.cltl.emissor_evaluation.graph.graph_evaluation --emissor-path data/emissor --scenario 2ad0c8b9-4e62-4f11-809c-57bf76487f95
```

### Human evaluation

```human/manual_evaluation.ipynb``` creates a spreadsheet ```<scenario_id>_manual_evaluation.csv``` for the human evaluation of a conversation, with the criteria of the Ninth Dialog System Technology Challenge ([DSTC9 track 3](https://dstc9.dstc.community)): ```Overall Human Rating```, ```Engaging```, ```Specific```, ```Relevant```, ```Correct```, ```Understandable``` and ```Coherent```, and a column for a reference response. Score each system response on each criterion from 1 (lowest, bad) to 5 (highest, flawless), using integers only. The criteria are explained in ```human/DSCT9-track3-Annotation Questionairre.pdf```.

## Plotting the scores

The ```plots``` folder has three notebooks:

* ```plot_analysis_from_csv.ipynb``` plots a CSV file as a timeline with ```create_timeline_image_from_csv``` in ```plot_interaction.py```: the turns of the conversation on the X-axis, with their number, speaker and utterance, and the score on the Y-axis. Each data point is labelled with its score, and with ```label_column``` you can add another value to the label, e.g. the dialogue act (```dialogue_act```) or the emotion (```go_emotion```). ```create_stacked_timeline_image_from_csvs``` plots all CSV files of a scenario under each other in one image and ```create_combined_timeline_image_from_csvs``` as lines in one plot, so that the analyses can be compared turn by turn.
* ```plot_analysis_from_annotation.ipynb``` plots the annotations that are stored in the EMISSOR scenario itself, such as the likelihood, sentiment and emotions, with ```create_timeline_image```, including the images of the conversation.
* ```metrics_plotting.ipynb``` uses the ```Plotter``` in ```metrics_plotting.py``` to plot how the scores develop over the turns for many conversations at once, with a line for each conversation, or all metrics of one scenario in one plot.

The plots are saved as PNG files in the ```evaluation``` folder of the scenario, or in a ```plots``` folder in the ```EMISSOR``` folder for ```metrics_plotting```. Both scripts can also be run from the root of the repository, e.g.:

```bash
python -m src.cltl.emissor_evaluation.plots.plot_interaction --emissor-path data/emissor --scenario b387db06-934e-405b-9d4e-f7e5c27b440a --csv data/emissor/b387db06-934e-405b-9d4e-f7e5c27b440a/evaluation/b387db06-934e-405b-9d4e-f7e5c27b440a_likelihood_evaluation.csv --score llh
python -m src.cltl.emissor_evaluation.plots.metrics_plotting data/emissor likelihood llm_judge
```

Run them with ```--help``` for all options.

## Correlating the scores

```correlate.ipynb``` joins the CSV files of different analyses of the same conversation on the ```Turn``` column and computes the correlations between their scores with the **Pearson**, **Kendall** or **Spearman** method, e.g. between the human ratings, the LLM-as-a-judge coherence and the likelihood. The correlations are saved as ```<scenario_id>_correlations.csv``` with a heatmap in the ```evaluation``` folder. Make sure that the score columns of the files have different names.

## How to proceed

1. Run any of the analyses on the scenario of your choice by setting ```EMISSOR``` and ```SCENARIO``` in the notebook. The scores are saved as CSV files in the ```evaluation``` folder of the scenario.
2. Plot a CSV file, or combine CSV files in a single plot, with the notebooks in ```plots```.
3. Correlate the scores of different analyses with ```correlate.ipynb```, e.g. to find out which automatic score agrees best with your human evaluation.

## References

* Mehri, S., & Eskenazi, M. (2020). USR: An unsupervised and reference free evaluation metric for dialog generation. arXiv preprint arXiv:2005.00456.
* Yu, D., & Yu, Z. (2021). MIDAS: A dialog act annotation scheme for open domain human-machine spoken conversations. In Proceedings of EACL 2021.
* Demszky, D., Movshovitz-Attias, D., Ko, J., Cowen, A., Nemade, G., & Ravi, S. (2020). GoEmotions: A dataset of fine-grained emotions. In Proceedings of ACL 2020.
* Bavaresco, A., Bernardi, R., Bertolazzi, L., Elliott, D., Fernández, R., et al. (2025). LLMs instead of human judges? A large scale empirical study across 20 NLP evaluation tasks. In Proceedings of ACL 2025.
