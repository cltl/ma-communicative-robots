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

The formats and classes for representing data are derived from presentations that were developed 
in various others projects and combined in the [NewsReader](www.newsreader-project.eu): the Simple Event Model (SEM, Hage et al. 2011), 
the NewsReader Annotation Format (NAF, Fokkens et al, 2014), the Grounded Annotation Framework (GAF, Fokkens et al, 2013, 2014) 
and its successor the Grounded Annotation and Source Perspective model (GRaSP, Son et al, 2016, Fokkens et al, 2017). 
The core idea behind the latter two is that we create a relation between a signal and the interpretation of that signal. 
These interpretations are seen as annotations that express a relation between a **segment** of the signal 
(e.g. a bounding box in an image or an offset position and length in a text) and some interpretation label defined in another framework. 
We use the Simple Event Model or **SEM**  to model the interpretation of situations depicted in the multimodal signal. 
These situations are represented in RDF as instances of people, objects, relations and properties. 
Annotations relate these instances to specific segments in the signals.

This README explains the data laysers and representations in more detail and is further divided into the following subsections:
<ol>
<li>Overall data view
<li>Scenario structure
<li>Context
<li>Content
</li>Annotation
</ol>

## 1. Overall data view

Figure-1 shows an overview of the different data layers in our representation. From the top, we see different layers for segments,
rulers, containers. A segment can consists of smaller segments and there are different subtypes
of segments per modality of the data. A ruler is made up of a specific unit of segments, which can be used to index a signal as a set of
segments with a particular granularity. Again, we can have subtypes of rulers for each modality. Next, we have containers for each modality.
Containers ground the data in a spatial and temporal world and can be used to define the order of segments, as in a sequence, 
or a position of regions.

A scenario inherits from both a temporal and spatial container. It is further defined with specific atttributes and the signals
of a certain modality. These signals consist of segments. Segments that are annotated are mentions. The annotation relates a segment to an interpretation.
Some of these annotations are instances in the model of the world and others are labels that represent concepts. Here we show different types of
concepts, such as tokens, faces, and named entity expressions, and types of instances, such as objects, friends and persons.

![Entity relationship diagram](/data/Datarepresentation.png "Overview of data elements and relations")
Figure-1: Overview of data elements and relations.

 
## 2. Scenario structure
We consider an interaction as a scenario. Scenarios are stored as subfolders within the data folder. 
Within a scenario folder, we store multimodal data in four media subfolders as separate files: text, video, image, audio. 
Furthermore, JSON files for each modality define the metadata and the annotations. There is one JSON file per modality.
The JSON file contain meta data on the source, creation time, the scenario it is part of, the owner, license, etc. The annotations
in the JSON file define a segment in a specific data file and the interpretation label of the segment, e.g. a person, object, an emotion,
a part-of-speech, named-entity-expressions, etc. A specific folder "rdf" contains the RDF triples extracted from the annotated signals.
For example, an utterance in a conversation may mention somebody's age, which yields an RDF triple with the person's URI as the subject, 
the has-age property and the actual age as a value.

Finally, there is a separate JSON file with meta data on the complete scenario. This scenario JSON defines the temporal and spatial ruler
within which the scenario is located (date, begin and end time, geo-location, place-name), the participants of the interaction 
(e.g. the agent and the human speaker) and any other people and objects that participate in the scene.
This scenario JSON file has the same name as the folder name of the scenario. 

**An example**
Assume our scenario folder has the name "my-first-scenario". This is how its structure could look like:

```
my-first-scenario
	my-first-scenario.json --> overall data on the scenario

	text.json -->  meta data and annotations on the conversation and segments within, typically the utterances of each turn form a unit
	video.json --> meta data and annotations of video fragments and segments within
	audio.json --> meta data and annotations of audio fragments and segments within
	image.json --> meta data and annotations of images and segments within
    
    text
        #### conversations in text
	    conversation-as-text.csv --> csv file with utterances from conversations that take place in this scenario in text format

    image
        #### stills from the video signals
        image1.jpg --> images representing stills of situations, possibly drawn from a video
	    image2.jpg
	    image3.jpg
  
    video
        #### video shoot of the scenario
        interaction-video.mpeg4 --> video with interaction, either the agent view or another camera view

    audio
        #### audio files possibly representing speech
        audio1.wav --> audio files representing sound events, possibly speech acts or utterances 
	    audio2.wav
	    audio3.wav

    rdf
        #### 
        some-triples.trig
```

## 2. Context
The file "my-first-scenario.json" describes the scenario in terms of meta data using standard data categories (e.g. Dublin core and CMDI) 
but also the 'spatial and temporal containers' within which the scenario takes place.

<ol>
    <li>Spatial container: geo-location and coordinates that define the area, possibly the name that identifies the area
    <li>Temporal container: date and begin and end time within which events take place
</ol>

The spatial and temporal containers define the primary context for interpreting data in the scenario. For example, knowing the date
and the location, a system can infer it is winter or summer, guess what the weather is like, whether it is morning or evening, or
that you birthday is soon.

In addition, the scenario can also have a specification of the participants, such as:

<ol>
    <li>Identity of the agent
    <li>Identity of the speaker
    <li>Any other people present and their spatial orientation
    <li>Objects and their spatial orientation
</ol>

Finally, the JSON file of the scenario provides an overview of all the data files in the folder and their grounding to the spatial and temporal containers. 

## 3. Content
The content of the scenario is represented by a series of files in the scenario folder representing the data in different modalities. 
In the above example, we have separate files for the conversations, a video stream of the interaction, images of scenarios, and audio files. 
Each modality has a JSON file that describes the data that contain signals and any interpretation of the signal in the form of an annotation.
Any signal is grounded in the spatial and temporal container using specific data elements in the JSON file. 

Although the data can be streamed as in video and audio, any system needs to define units within the stream to interpret states 
and changes between these states. Therefore, we can not only represent a scenario by the video but also through 
a collection of stills in the form of images taken at different time points, as a collection of audio files for speech interaction 
or as the transcribed text of the audio to represent a dialogue. 

Through the spatial and temporal grounding of each of these data files (treated as a signal), 
they can be organised through a a two dimensional matrix (T x M), where T is the temporal ruler segmenting time in Tn units and M 
is a series of modalities with data files at the time points in the ruler. 
The next example shows such a Matrix with a temporal ruler for 6 time points and 4 modalities of signals grounded to these units:

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

We assume that the video is a continuous stream from begin to end which is not cut to the time points. 
However, the other modalities fill separate slots at the time points, where we do not necessarily have data at each time point. 
The temporal ruler (the first column) aligns the different signals across the modalities. 
his temporal ruler can have any granularity, in this example it is by minutes.

## 4. Segments, rulers and containers
The maximal segment of a data file for a modality is the actual data file itself. The JSON file for that modality defines for every data file
the modality, the temporal ruler identity in which it is grounded and the start and end point of the maximal segment it represents.
Below we show the JSON structure for one **image** file, where the start and end are represented here in milliseconds.

```example
"modality": "IMAGE",
    "time": {
        "type": "TemporalRuler",
        "container_id": "test-scenario-2",
        "start": 1603139705,
        "end": 1603140000
    },
    "files": [
        "data/test-scenes/test-scenario-2/image/piek-sunglasses.jpg"
    ],
```
Within the overall segment of the grounded image file, we can define smaller spatial segments by annotation.
For images such annotations could be linked to bounding boxes defined in the image, as shown next, where the bounds
indicate the coordinates that make up this segment and two annotations are provided, one for the person identified and one
for the emotion expressed by the face:

```example
    "mentions": [
        {
            "segment": {
                "type": "MultiIndex",
                "container_id": "0c1b7ffd-d22b-41c5-a55d-0f4a16b9ad89",
                "bounds": [
                    [
                        10,
                        521
                    ],
                    [
                        15,
                        518
                    ]
                ]
            },
            "annotations": [
                {
                    "type": "PersonAnnotation",
                    "value": "leolaniWorld:piek",
                    "id": "e136ee3c-ccaa-456d-9124-bc1af60ad424#PERSON1",
                    "source": "face_recognition",
                    "confidence": 0.76,
                    "timestamp": 1604957866.524172
                }, {
                    "type": "EmotionAnnotation",
                    "value": "ANGRY",
                    "id": "e136ee3c-ccaa-456d-9124-bc1af60ad424#EMO1",
                    "source": "annotator_1",
                    "confidence": 0.76,
                    "timestamp": 1604957866.5242481
                }
            ]
        }

        .... etc....
    ]
```

We can have any number of segments with any number of annotations defined for any number of image files. 
Annotated segments are listed as mentions in the JSON file.

The JSON for **text** data has a similar structure for the data file except that we have a single CSV file with all the text utterances rather
than a separate data file for each utterance. This is just for pragmatic reasons to make it easier to process Natural Language data.
As a result of that, we separate the data by the rows and columns in the CSV file as shown in the JSON fragment below:

```example
{
    "modality": "TEXT",
    "time": {
        "type": "TemporalRuler",
        "container_id": "test_scenario",
        "start": 1603139850,
        "end": 1603149890
    },
    "files": [
        "data/test-scenes/test_scenario/text/chat1.csv#1#1"
    ],
```

We see that the file "chat1.csv" which is in the **text** folder is indexed with "#1#1", which refers to the second row and the second
column of the csv file that contains the text of an utterance (#0#0 would refer to the header and the first column). 
Other columns can be used to represent the speaker (column 0 in our example) of the utterance and the
start and end time of speaking (possibly derived from an audio file). The complete conversation for a scenario can thus 
be represented through a single CSV file with all utterances, identifiers and temporal grounding on separate rows.

Note: In the case of text, it is also possible to represent the data only in the JSON file and not separately in a CSV file.

Note: Text as data can be derived from the audio data, in which case it is a form of annotation, or it can be raw data (without audio)
for example taken from chat platforms, forums or novels.

An annotation of the above text fragment is shown below. The segment is defined by the start and end offset position in the text
utterance from row 1 and column 1 in the CSV file. The annotation of the segment shown here defines the offset range as a Token which
isolated the word "This".

```example
    "mentions": [
        {
            "segment": {
                "type": "Index",
                "container_id": "265a5bd0-a8b7-4de6-9f4d-2c4d8d200f70",
                "start": 0,
                "end": 4
            },
            "annotations": [
                {   "type": "Token",
                    "value": "This",
                    "id": "2ac58d89-76e8-41c5-8997-cd36e38fab9e#t1",
                    "source": "treebank_tokenizer",
                    "timestamp": 1604957866.557157
                }
            ]
        }
        .... etc....
    ]
```
More details on the annotations are given in the next section.

## 5. Annotations
As explained above, annotations define a relation between a segment and an interpretation. Each annotation has the following attributes:

<ul>
<li> type: kind of annotation
<li> value: the actual label, which can be a JSON structure or some defined label or identifier
<li> source: name of the software or person that created the annotation
<li> timestamp: indicate when the annotation was created</li>
<li> (OPTIONAL) id: local identifier that differentiates annotations within a JSON file</li>
</ul>

The above examples illustrate these attributes and possible values.

The id attribute holds a unique identifiers for each annotation. This allows us to build annotations on top of other annotations, as
NLP pipelines, modules typically take the output of one annotation as the input for the next annotation 
(following the layered annotation framework as defined by Ide and Romary 2007). 
For example, we can first define the tokens of a text as segments grounded through
offsets and next refer to these tokens to add another annotation. 
This is shown in the next example, in which a PersonAnnotation is given
for a segment that is defined elsewhere as the token "My":

```example
        {
            "segment": {
                "type": "Index",
                "container_id": "265a5bd0-a8b7-4de6-9f4d-2c4d8d200f70",
                "start": 0,
                "end": 1
            },
            "annotations": [
                {   "type": "Token",
                    "value": "My",
                    "id": "2ac58d89-76e8-41c5-8997-cd36e38fab9e#t1",
                    "source": "treebank_tokenizer",
                    "confidence": 0.76,
                    "timestamp": 1604957866.557157
                }
            ]
        },
        {
            "segment": {
                "type": "AtomicRuler",
                "container_id": "2ac58d89-76e8-41c5-8997-cd36e38fab9e#t1"
            },

            "annotations": [
                {
                    "type": "PersonAnnotation",
                    "value": "leolaniWorld:piek",
                    "source": "entity_linking",
                    "confidence": 0.76,
                    "timestamp": 1604957866.524172
                },
            ]
        }
```

Similarly, we can provide a whole set of segments by listing the identifiers that represent the mention of an annotation.
In the next example, we show a set of four segments that have been annotated as representing a "Claim" by a "textToTriple" module:

```example
       {
            "segment": {
                "type": "AtomicRuler",
                "container_id": "2ac58d89-76e8-41c5-8997-cd36e38fab9e#t1",
                "container_id": "2ac58d89-76e8-41c5-8997-cd36e38fab9e#t2",
                "container_id": "2ac58d89-76e8-41c5-8997-cd36e38fab9e#t3",
                "container_id": "2ac58d89-76e8-41c5-8997-cd36e38fab9e#t4",
                "container_id": "2ac58d89-76e8-41c5-8997-cd36e38fab9e#t5"
            },
            "annotations": [
                {
                    "type": "Claim",
                    "value": "leolaniWorld:piek-daughter-niqee",
                    "source": "textToTriple",
                    "confidence": 0.76,
                    "timestamp": 1604957866.524172
                }
            ]
        }
```


### 5.1 Mentions
The annotation labels can represent any type of interpretation, ranging from part-of-speech, syntactic dependencies, pixel colour, pitch, loudness,
shape, emotions, people, objects or events. Since our models need to relate interpretations across modalities, 
some of these annotations identify instances of people and objects 
depicted in the visual world. Consider the following examples: 

* "That is my son sitting next to me"
* "Sam is eating a sandwich"

An annotation of these utterances could define the tokens "my son" as making reference to a person who is a male child of me (the speaker). 
Similarly, the token "Sam" can be annotated as the name of a person. 

Similarly, we can annotate certain areas in images as representing people of certain age or gender, surrounded by objects that are annotated 
with object labels. By annotating segments in the signal with interpretation labels, we indicate that these segment **mention** things in signals.

### 5.2. Identities
It is however not enough to mark "my son" as making reference to a person or "Sam" as a named entity expression. 
We also need to link these expressions to the actual people in our shared world. 
The GAF/GRaSP framework (Fokkens et al, 2013, 2017) therefore uses so-called **grasp:denotes** and **grasp:denotesBy** relations to mentions
and identifiers in a semantic model of the world. Following Semantic Web practices and standards, individuals are represented 
through unique resource identifiers or URIs (also called IRIs). In the above example, we have seen the annotation of the Token "my" 
by making reference to the value "leolaniWorld:piek". The latter being short-cut identifier for an instance within the name-space "leolaniWorld".
Any name space and any identifier will do here. This could also have been a DBPedia URI or any other identifier in 
the Semantic Web Linked Open Data Cloud.

{
            "segment": {
                "type": "AtomicRuler",
                "container_id": "2ac58d89-76e8-41c5-8997-cd36e38fab9e#t9"
            },

            "annotations": [
                {
                    "type": "PersonAnnotation",
                    "value": "leolaniWorld:sam",
                    "source": "entity_linking",
                    "confidence": 0.76,
                    "timestamp": 1604957866.524172
                },
            ]
        }
        

Identity across these URIs establishes **co-reference** relations across different mentions. If the tokens "piek" and "my" are
annotated with the same URI they automatically become co-referential. By following the same procedure for other modalities, 
we can thus annotate visual data with similar identifiers, creating cross-modal co-reference.

### 5.3. Properties and relations as RDF triples
By using URIs for referential annotations of segments, we can also represent properties and relations of and between identified people and objects.
These properties and relations, such as 'wearing a hat", ""eating a sandwich" or "throwing a ball", can be expressed in the utterances and in images.
When an annotator (human or machine) detects these properties, the multimodal signals yield triples (in RDF format) that represent these as
interpretations of states of the (multimodal) world. Such RDF triples consist of a subject URI, a predicate or property and an object URI or value, 
as shown below (leaving out the name spaces):

```example
    :piek   :has-gender         :male
    :piek   :is-father-of       :sam
    :piek   :shows-emotion      "smile"
```

Through the referential grounding discussed in the previous section, we can use multimodal signals to generate triples expressing properties and
relations across different modalities and different data files. Shared identifiers (URIs) aggregate of these eproperties and relations
resulting in a world model over time. The triples stored in a data base (triple store) 
likewise reflect this cumulation over time, while each triple can still be grounded to a segment in a modality. By faceting the triples in time, they
also model changes of states, such as smiling first and being angry next.

The GRaSP framework considers the triples depicted in segments of any modality as claims. Different sources and different perceptions can make different claims
about the same triple relation. For example, source could dispute the gender of ":piek" or his emotion at any moment in time.

### 5.4 Claims
In our triple representation, we therefore used **named-graphs** that embed the extracted triples within "claims".
Below, we show a representation of triples in which claims are listed through URIs as well such that we can express 
properties about them and also embed world relations and properties within a named claim-graph:

```example

    leolaniWorld:piek-from-schaesberg {
	    :piek :born-in :schaesberg .
    }


    leolaniWorld:piek-from-landgraaf {
	    :piek :born-in :landgraaf .
    }

    leolaniWorld:Claims {

	leolaniWorld:piek-from-schaesberg a grasp:Statement ;
	                                  grasp:denotedBy leolaniTalk:2ac58d89-76e8-41c5-8997-cd36e38fab9e#t9 .

  	leolaniWorld:piek-from-landgraaf  a grasp:Statement ;
                                      grasp:denotedBy leolaniTalk:2ac58d89-76e8-41c5-8997-cd36e38fab9e#t45 .

    } 

    leolaniTalk:Perspectives {
        leolaniTalk:2ac58d89-76e8-41c5-8997-cd36e38fab9e#t9 
                                      a grasp:Mention ;
                                      grasp:wasAttributedTo :piek .

        leolaniTalk:2ac58d89-76e8-41c5-8997-cd36e38fab9e#t45  
                                      a grasp:Mention ;
                                      grasp:wasAttributedTo :carl.
    }

```

This RDF representation uses name spaces: **leolaniWorld** and **leolaniTalk**, that are defined in a robot platform
called **Leolani**: http://makerobotstalk.nl. The implementation is further defined in the following Github: https://github.com/cltl/pepper
  
In this example, there are two claims: one claim with the URI *leolaniWorld:piek-from-schaesberg* that embeds the triple 
that ":piek" was born in the city "schaesberg" and another claim with the URI *leolaniWorld:piek-from-landgraaf* 
which embeds the triple that he was born in "landgraaf". 
We furthermore see that these claims are instances of the class "grasp:Statement" and they
are grounded through "gaf:denotedBy" links to identifiers grouped within the "leolaniTalk:Perspectives" subgraph, where
they are defined as "mentions" and have a grasp:wasAttrubutedTo relation to the speaker.

If we return to the JSON structure for our text fragment above, we see in the last examples that we can annotate tokens with claim
identifiers that are also used in the triples that explicitly model the claims. In that way, we do not need to represent the triples
explicitly in the JSON file, but we can annotate segments through URIs that are further defined in the associated triple file.

## References
```

@incollection{ide2007towards,
  title={Towards International Standards for Language Resources Nancy Ide and Laurent Romary},
  author={Ide, Nancy and Romary, Laurent},
  booktitle={Evaluation of text and speech systems},
  pages={263--284},
  year={2007},
  publisher={Springer}
}

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
```
