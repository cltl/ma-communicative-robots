#  Conversational AI & Robots, 2026

Conversational AI & Robots is a master's course taught at the Vrije Universiteit Amsterdam.
We use the LEOLANI platform for interacting with agents and robots (Baier et al 2025). 
Interactions through LEOLANI are captured in the EMISSOR format (Baez et al 2022). 
[EMISSOR](https://github.com/leolani/cltl-combot/blob/main/src/cltl/combot/event/emissor.py) is a frequently used JSON structure in which interactions are stored on disk as ```scenarios``` in separate folders.
EMISSOR stores incoming streams of signals (audio, text, image) as separate data points that are aligned through a temporal ruler that is shared by the scenario.

This project shows how interactions saved in EMISSOR can be analysed and evaluated in different way:

* scoring the likelihood of turns based on the previous context using a transformer model and masked token predictions
* scoring the coherence of turns based on the previous context using a generative LLM as a judge
* scoring dialogue acts as positive, negative or neutral moves in the interaction
* scoring the emotions expressed in each turn as positive, negative or neutral moves in the interaction
* evaluating the properties of knowledge added to a knowledge graph on a positive/negative axis
* human assessment of each turn on a likert scale

For each of the above analysis, a notebook is provided that shows how one or more EMISSOR scenarios can be loaded and scored according to the method.
The result of the scoring is saved in a CSV file in an ```evaluation``` folder, where each row contains the ```turn id```, the ```speaker```, the ```utterance``` and additional values for the analysis and the scores.

The ```plots``` module has two notebooks for reading the CSV files and generating plots for each interaction that show the conversation on the X-axis as a sequence of turns and the scored analysis on the Y-axis.

The ```data``` folder contains an ```emissor``` folder with the interaction data for a few scenarios to demonstrate the notebooks.
Replace the path to your own emissor data to apply the analysis on your interactions.

## How to proceed

1. Apply any of the analyses (likelihood, coherence, dialogue act, emotion) to the scenario of your choice by adapting the path to your emissor folder and the name of your scenario to the corresponding notebook. The output is saved in a CSV file in the ```evaluation``` folder. 
2. Create a plot for any of the saved CSV file or combine CSV files in a single plot. You can use ```metrics_plotting.ipynb``` or ```plot_analysis_from_csv.ipynb``` for plotting.

You could also create your own code to create a CSV file following the same format and plot the result.

In addition to plotting the interactions with the result of the analysis, the notebooks also provide other results in each analysis notebook.

## Requirements

Clone this repository to prepare for the course:

```bash
   >git clone git@github.com:cltl/ma-communicative-robots.git
   >cd ma-communicative-robots
```

Create a virtual environment for running the code.

Using venv:
   ```bash
    python -m venv --python=3.11 evaluate
    source venv/bin/activate
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    python -m ipykernel install --user --name=evaluate
   ```

Using Conda:
```bash
    conda create -n evaluate python=3.11
    conda activate evaluate
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    python -m ipykernel install --user --name=evaluate
```

With the environment active, launch Jupyter lab from the CLI and open the notebooks

## References
Feel free to use our work but cite us:
* Baez Santamaria, S., Baier, T., Kim, T., Krause, L., Kruijt, J., & Vossen, P. (2021). EMISSOR: A platform for capturing multimodal interactions as episodic memories and interpretations with situated scenario-based ontological references. In Proceedings of the First workshop Beyond Language: Multimodal Semantic Representations in conjunction with IWCS 2022
* T. Baier, S. Báez Santamaría, P. Vossen: A modular architecture for creating multimodal embodied agents with an episodic Knowledge Graph as an explainable and controllable long-term memory, in: Dialogue & Discourse Volume 14, ed. 3, pages 25-59

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
- Thomas Baier (t.baier@vu.nl)
