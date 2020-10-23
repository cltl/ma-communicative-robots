Multimodal Interaction Data Representation (MIDR)

This data folder contains test data for multimodal interaction systems with robots and virtual agents. This data can be rendered by interacting system that record the interaction and it can be annotated with interpretations.

The data consists of a series of folders, each folder representing a single scenario with multimodal data files and JSON files that contain meta data on the data files and annotations of units within the multimodal data.

Scenario structure

Each scenario contains data files for 4 possible modalities and a single corresponding JSON file that contains the meta data and the annotations for all units in that modality. Furthermore, there is a separate JSON file with the meta data on the complete scenario. This JSON file has the same name as the folder name of the scenario.

Assume our scenario folder has the name "my-first-scenario". This is how the data structure could look like:



my-first-scenario
	my-first-scenario.json --> overall data on the scenario
	conversation-in-text.csv --> csv file with utterances from conversations that take place in this scenario
	conversation-in-text.json --> meta data and annotations on the conversation and each unit within the conversations, usually the utterances of each turn
	interaction-video.mpeg4 --> video with the interaction
	interaction-video.json
	image1.jpg
	image2.jpg
	image3.jpg
	images.json
	audio1.wav
	audio2.wav
	audio3.wav
	audion.json


