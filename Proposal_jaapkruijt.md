<!-- Copy and paste the converted output. -->

<!-----
NEW: Check the "Suppress top comment" option to remove this info from the output.

Conversion time: 0.4 seconds.


Using this Markdown file:

1. Paste this output into your source file.
2. See the notes and action items below regarding this conversion run.
3. Check the rendered output (headings, lists, code blocks, tables) for proper
   formatting and use a linkchecker before you publish this page.

Conversion notes:

* Docs to Markdown version 1.0β29
* Thu Oct 29 2020 04:11:39 GMT-0700 (PDT)
* Source doc: Project description combot course
----->



## Project description Communicative Robots


## Jaap Kruijt: From dialogue to kinship and back


#### Background

Many inferences over relations that come natural to us humans, are very hard for robots to compute. A deceptively simple example can be found in kinship (family) relations. Although these present no real problem for humans, robots have great difficulty understanding and disambiguating the meaning of kinship terms. How can the robot learn the difference between a brother and a sister, and a brother and a cousin? What distinguishes a sister from a step sister, and who exactly are the parents of each of them? Which relations are symmetric (i.e. sibling) and which aren’t (i.e. parent/child)? In this project we will investigate these problems the robot faces and work on a system that can compute (simple) kinship relations.


#### Methodology

In order to have an accurate representation of family relations, the robot needs to have entries for these relations in its _ontology._ The ontology defines the relations between objects or persons. This definition can take various forms. In the Leolani platform, relations are defined as rdf triples. At this moment, an accurate ontology for kinship does not exist in the leolani platform. In this project, we can choose in what way we want to define kinship relations. To bridge the gap between the spoken utterances and the reasoning over this utterance, we could then use a _lexicon_, which defines exactly which words relate to what entry in the ontology. Finally, a system needs to be in place which takes natural language input and reasons over the utterances to define the relationships in the robot brain. You could of course also choose another method, such as an end-to-end system which directly relates utterances to relations through training. The model that we design should be tested on a dataset. A possible dataset could be the MELD dataset which contains annotated dialogues from episodes of _Friends_.


#### What will we work on?

As I have only quite recently started on my PhD, the project is still very much open to ideas. I have outlined a couple of ideas varying in difficulty which we could focus on:



*   The first step is to simply have an accurate representation of kinship. Showing the robot a picture of a woman and stating “This is my sister” should lead to an inference over this utterance, where the person in the picture is assigned the appropriate gender and the robot understands that you and the woman in the picture have the same parents.
*   A second step would be to introduce ambiguity or uncertainty. Showing the robot a picture of two women and stating: “They are my mother and grandmother” requires multimodal input where age and gender information is extracted from the visual input and combined with the utterances to assign the persons in the picture their respective relation to the speaker. 
*   Another way in which uncertainty could be introduced is through missing information. Take the utterance “This is my step sister”. For a sister, the robot should compute that you and your sister have the same parents. For a step sister, only one parent is shared. We don’t know whether the shared parent is the mother or the father. Does the robot need to know? How can it form an accurate representation in its brain without this information? Should the robot ask for this missing information?
*   Finally, so far we’re only focusing on language _understanding_. We could rate the robot’s performance by comparing its output to a ‘gold standard’ family tree which we designed ourselves. Another option is to also let the robot _generate_ utterances which we can use to judge its performance. This presents an additional problem: how exactly should the robot talk about the family relations? Preferably, the robot should say “This is your great aunt” instead of saying “This is the sister of the parent of your parent”. The last one is more informative to the robot, whereas the first one is what we humans want to hear. 


#### Relation with Lea’s and Tae’s project

In Tae’s project you will work on age and gender detection from visual data. This information is crucial in distinguishing between a brother and a sister, or a mother and a grandmother. Lea’s project on the other hand aims to avoid assuming gender. This means that the robot should not infer gender from visual data only but rather wait for explicit confirmation of gender before assigning it.


#### Literature

A few pointers to possible ontologies/datasets:

_Sumo ontology:_

Niles, I., and Pease, A.  2001.  Towards a Standard Upper Ontology.  In Proceedings of the 2nd International Conference on Formal Ontology in Information Systems (FOIS-2001), Chris Welty and Barry Smith, eds, Ogunquit, Maine, October 17-19, 2001.

[https://dl.acm.org/doi/pdf/10.1145/505168.505170?casa_token=KYfiFwhoER4AAAAA:R9z6UdNmRI0Y3585a71KNmX3WDCHRHkx7BwtwKO5Yp43iXaPoofyHRD9QZFK38TbZFn5jpZX4O4pSw](https://dl.acm.org/doi/pdf/10.1145/505168.505170?casa_token=KYfiFwhoER4AAAAA:R9z6UdNmRI0Y3585a71KNmX3WDCHRHkx7BwtwKO5Yp43iXaPoofyHRD9QZFK38TbZFn5jpZX4O4pSw)

_MELD dataset:_

S. Poria, D. Hazarika, N. Majumder, G. Naik, E. Cambria, R. Mihalcea. MELD: A Multimodal Multi-Party Dataset for Emotion Recognition in Conversation. ACL 2019.

[https://arxiv.org/pdf/1810.02508.pdf](https://arxiv.org/pdf/1810.02508.pdf) 
