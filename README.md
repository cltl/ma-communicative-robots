# Communicative Robots, 2024

Communicative Robots is a master's course taught at VU Amsterdam.

This year's branch is `2024`, which is the default branch of this repo. If you want to see others years, take a look at the other branches.

## Prerequisites

1. python 3.9 or higher. Running in a virtual environment (e.g., conda, virtualenv, etc.) is highly recommended so that you don't mess up with the system python.

2.

   ```
    python -m venv venv
    source venv/bin/activate
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    pip install jupyter
   ```

## Emissor

We use EMISSOR to capture interactions. EMISSOR is a frequently used JSON structure in which interactions are stored in disk as ```scenarios```` in separate folders.
EMISSOR stores signals for each modality: audio, text, image as separate data points that are aligned through a temporal ruler that is shared by the scenario. 
The alignment is stored in a separate JSON for each modality. The interpretation of signals is stored as annotations in the JSON file as well, e.g. named entities mentioned in text, people and objects detected in images.

In *emissor_chat* you find notebooks that demonstrate how you can connect chatbots with emissor to capture the interaction.

## Interaction analysis

In *interaction_analysis* you find code and notebooks for:

1. augmenting text conversations with named entity, dialogue act and emotion annotations
2. structural analysis of interactions stored in EMISSOR
3. graph analysis of EMISSOR in case the interaction is combined with an episodic Knowledge Graph
4. reference evaluation using BLUE, ROUGE, METEOR and BERTScore

## Episodic Knowledge Graph

In *episodic_knowledge_graph*, you find code and notebooks that demonstrate how knowedge and be pushed and retrieved from an episodic Knowledge Graph
optimized for capturing interactions.

## Leolani

In *leolani_text_to_ekg*, you find the files and instructions how to run ```Leolani``` in chatonly mode through a docker image. In this mode it extracts triples and emotions from
the Knowledge Graph and pushes these to the episodic Knowlege Graph (eKG). New information will prompt the eKG to reflect on this knowlege and formulate a response.
This keeps the interaction going. You can also ask questions to find out what the *agent* knows.

## Troubleshooting

The best way to find and solve your problems is to see in the github issue tab. If you can't find what you want, feel free to raise an issue. We are pretty responsive.

## Contributing

Contributions are what make the open source community such an amazing place to be learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
1. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
1. Run `make style && make quality` in the root repo directory, to ensure code quality.
1. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
1. Push to the Branch (`git push origin feature/AmazingFeature`)
1. Open a Pull Request

## Authors

- Piek Vossen (piek.vossen@vu.nl)
- Annika Kniele (a.kniele@vu.nl)
- Selene Baez Santamaria (s.baezsantamaria@vu.nl)
- Thomas Baier (t.baier@vu.nl)
