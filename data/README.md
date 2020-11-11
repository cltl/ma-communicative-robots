# Multimodal Interaction Data Representation (MIDR)

We propose a generic and simple structure for representing multimodal interaction data. 
This data can be derived from human-human, human-agent and agent-agent interactions, 
where agents can be robots or virtual agents. Our motivation for doing this is that 
it can be used to hold, combine and share data across many different experiments and allows to compare these.

This README explains the data folder in this repository, which illustrates how to structure data.
This data can be rendered by interacting systems that record the interaction and it can be annotated 
with interpretations (by people and/or systems). In the **representation** module of this repository, 
we provide python classes that represent the data elements, which are used to create and load data. 
We also provide a basic annotation tool for creating and annotating scenarios. 
In the future, we will release here public data sets used in other experiments converted to our proposed format.
This data can also be loaded and annotated.

## 1. Overall data view

(./Datarepresentation.png)
">Entity relationship diagram</img>

## 1. Scenario structure
We consider an interaction as a scenario. Scenarios are stored as subfolders within the data folder. 
Within a scenario folder, we store multimodal data in media folders, where each data 
The data consists of a series of folders, each folder representing a single scenario with multimodal 
data files and JSON files that contain meta data on the data files and annotations of units within the multimodal data.

Each scenario contains data files for 4 possible modalities and a single corresponding JSON file 
that contains the meta data and the annotations for all units in that modality. 
Furthermore, there is a separate JSON file with the meta data on the complete scenario. 
This JSON file has the same name as the folder name of the scenario.

Assume our scenario folder has the name "my-first-scenario". This is how the data structure could look like:

```
my-first-scenario
	my-first-scenario.json --> overall data on the scenario

	text.json --> meta data and annotations on the conversation and each unit within the conversations, usually the utterances of each turn
	video.json
	audio.json
	image.json
    
    text
        #### conversations in text
	    conversation-in-text.csv --> csv file with utterances from conversations that take place in this scenario

    image
        #### stills from the video signals
        image1.jpg --> images representing stills of situations, possibly drawn from the video
	    image2.jpg
	    image3.jpg
  
    video
        #### video shoot of the scenario
        interaction-video.mpeg4 --> video with the interaction

    audio
        #### audio files possibly representing speech
        audio1.wav --> audio files representing sound events, possibly speech acts or utterances 
	    audio2.wav
	    audio3.wav

    rdf
        #### 
        some-triples.trig
        more-triples.trig
```

## 2. Context
The file "my-first-scenario.json" describes the scenario in terms of meta data using standard data categories (e.g. Dublin core and CMDI) but also the 'spatial and temporal containers' within which the scenario takes place.

<ol>
    <li>Spatial container: geo-location and coordinates that define the area, possibly the name that identifies the area
    <li>Temporal container: date and begin and end time within which events take place
</ol>

The spatial and temporal containers define the primary context for interpretating any data in the scenario. In addition, the scenario can also have a specification of the participants, such as:

<ol>
    <li>Identity of the agent
    <li>Identity of the speaker
    <li>Any other people present and their spatial orientation
    <li>Objects and their spatial orientation
</ol>

In addition to the meta data, the JSON file of the scenario provides an overview of all the data files in the folder and their grounding to the spatial and temporal containers. These data files represent all the recorded signals in the scenario as its content. Each of these content files is further described in specific JSON files.

## 3. Content
The content of the scenario is represented by a series of files in the scenario folder representing the data in different modalities. In the above example, we have separate files for the conversations, a video stream of the interaction, images of scenarios, and audio files. Each modality has a JSON file that describes the data that contain signals and any interpretation of the signal in the form of an annotation. Any signal is grounded in the spatial and temporal container using specific data elements in the JSON file. 

Although the data can be streamed as in video and audio, any system needs to define units within the stream to interpret states and changes between these states. Therefore, we can not only represent a scenario by the video but also through a collection of stills in the form of images taken at different time points, as a collection of audio files for speech interaction or as the transcribed text of the audio to represent a dialogue. 

Through the spatial and temporal grounding of each of these data files (treated as a signal), they can be organised through a a two dimensional matrix (T x M), where T is the temporal ruler segmenting time in Tn units and M is a series of modalities with data files at the time points in the ruler. The next example shows such a Matrix with a temporal ruler for 6 time points and 4 modalities of signals grounded to these units:

```
time | video | audio | text  | image |
-------------------------------------
1:02 | ...   |       |       |       |
1:03 | ...   | wav   |       | jpg   |
1:04 | ...   |       | utter | jpg   |
1:05 | ...   | wav   | utter |       |
1:06 | ...   |       |       | jpg   |
1:07 | ...   | wav   | utter |       |
```

We assume that the video is a continuous stream from begin to end which is not cut to the time points. However, the other modalities fill separate slots at the time points, where we do not necessarily have data at each time point. The temporal ruler (the first column) aligns the different signals across the modalities. This temporal ruler can have any granularity, in this example it is by minutes.

## 4. Segments, rulers and containers

## 5. Annotations

In addition to the modality data files, we have JSON files for each modality with annotations and meta data. Meta data captures the type of modality, quality, ownership, source identifiers, etc. The annotations relate a segment from the media file or signal to an interpretation. In the case of text, these segments are defined by offsets in the text source file. In the case of images, these are box coordinates in the image file.

The complete conversation for a scenario can be represented through a single CSV file with all utterances, identifiers and temporal grounding on separate rows. The JSON file describes each utterance within the CSV and provides the spatial and temporal grounding within the scenario. In addition, the content of the utterance is annotated by a series of labels related to the tokens from text, whereas the tokens are grounded through offsets (following a layer annotation approach).


### 5.1 Mentions
The annotation labels can represent any type of interpretation, ranging from emotions, people, objects or events. Since our models need to relate interpretations across modalities, some of these annotations identify instances of people and objects depicted in the visual world. Consider the following examples: 

* "That is my son sitting next to me"
* "Sam is eating a sandwich"

An annotation of these utterances could define the tokens "my son" as making reference to a person who is a male child of me (the speaker). Similarly, the token "Sam" can be annotated as the name of a person. 

Similary, we can annote certain areas in images as representing people of certain age or gender, surrounded by objects that are annotated with object labels. By annotating segments in the signal with interpretation labels, we indicate the mention of things in signals.

### 5.2. Identities
It is however not enough to mark "my son" as making reference to a person or "Sam" as a named entity expression. We also need to link these expressions to the actual people in our shared world. For this, we follow the GAF/GRaSP framework (Fokkens et al, 2013, 2017) that makes a distinction between mentions in texts and a representation of the invidiuals these mentions refer to. Individuals are represented through unique resource identifiers or URIs following Semantic Web standards. Since both "my son" and "Sam" refer to the same URI, they thus become coreferential.

By following the same procedure for other modalities, we thus can ground the text mentions to visual coordinates, such as a box segment in an image, which is labeled as a person with an age and gender but also annoted with the URI representing the same individual.

### 5.3. Properties and relations as RDF triples
On top of the people and objects depicted or mentioned, there may be particular relations expressed, such as "eating" the sandwich or "throwing" a ball. Such relations and properties can be seen as states of events and can be annotated as well although their identity is more difficult to establish and represent by a URI. Within our model, we represent the mentioning of these relations and properties through RDF triples, where identified people and objects fill the subject and object positions and the relations and properties form the predicates. Likewise, the expression "my son" is eventually mapped to the following triples:

```
    :my-uri   parent-of   :sam
    :sam      gender      male
    :sam      son-of      :my-uri
```

The JSON annotations will also include such triples as the result of interpreting the signals to explicit knowledge that is stored in triple store.

## References

@inproceedings{fokkens2014naf,
  title={NAF and GAF: Linking linguistic annotations},
  author={Fokkens, Antske and Soroa, Aitor and Beloki, Zuhaitz and Ockeloen, Niels and Rigau, German and Van Hage, Willem Robert and Vossen, Piek},
  booktitle={Proceedings 10th Joint ISO-ACL SIGSEM Workshop on Interoperable Semantic Annotation},
  pages={9--16},
  year={2014}
}

@article{fokkensnaf,
  title={NAF: the NLP Annotation Format Technical Report NWR-2014-3},
  author={Fokkens, Antske and Soroa, Aitor and Beloki, Zuhaitz and Rigau, German and van Hage, Willem Robert and Vossen, Piek and Donostia, Basque Country}
}

@inproceedings{fokkens2013gaf,
  title={GAF: A grounded annotation framework for events},
  author={Fokkens, Antske and Van Erp, Marieke and Vossen, Piek and Tonelli, Sara and Van Hage, Willem Robert and Serafini, Luciano and Sprugnoli, Rachele and Hoeksema, Jesper},
  booktitle={Workshop on Events: Definition, Detection, Coreference, and Representation},
  pages={11--20},
  year={2013}
}

@inproceedings{van2016grasp,
  title={GRaSP: A Multilayered Annotation Scheme for Perspectives},
  author={van Son, Chantal and Caselli, Tommaso and Fokkens, Antske and Maks, Isa and Morante, Roser and Aroyo, Lora and Vossen, Piek},
  booktitle={Proceedings of the Tenth International Conference on Language Resources and Evaluation (LREC'16)},
  pages={1177--1184},
  year={2016}
}

@article{van2011design,
  title={Design and use of the Simple Event Model (SEM)},
  author={Van Hage, Willem Robert and Malais{\'e}, V{\'e}ronique and Segers, Roxane and Hollink, Laura and Schreiber, Guus},
  journal={Journal of Web Semantics},
  volume={9},
  number={2},
  pages={128--136},
  year={2011},
  publisher={Elsevier}
}

