#  Conversational AI & Robots, 2026

Conversational AI & Robots is a master's course taught at the Vrije Universiteit Amsterdam.
This repository has the code and data for the practical part of the course: building a conversational agent and evaluating the conversations it has with people.

We use the LEOLANI platform for interacting with agents and robots (Baier et al. 2025).
Interactions through LEOLANI are captured in the EMISSOR format (Baez et al. 2022).
[EMISSOR](https://github.com/leolani/cltl-combot/blob/main/src/cltl/combot/event/emissor.py) is a JSON structure in which interactions are stored on disk as ```scenarios``` in separate folders.
EMISSOR stores incoming streams of signals (audio, text, image) as separate data points that are aligned through a temporal ruler that is shared by the scenario.

The repository supports two ways of evaluating a conversational agent:

* **Evaluating the interaction**: conversations saved in EMISSOR are scored turn by turn, e.g. on the likelihood or coherence of each turn, its dialogue act or emotion, the knowledge it adds to a knowledge graph, or by a human judge. The scores are saved as CSV files and plotted over the conversation.
* **Evaluating the task**: an agent asks a person about their day and stores the answers as a structured description of the events of that day. The quality of the conversation is measured by how well the collected description matches a GOLD description of the same day, and by how many turns it took.

## Overview of the repository

```
ma-communicative-robots
├── README.md
├── requirements.txt
├── data
│   ├── emissor            example EMISSOR scenarios with their evaluation folders
│   ├── example_days       five GOLD descriptions of a day, with photos of some events
│   ├── collected_days     days collected by the day interviewer from a human user
│   └── simulated_days     days collected by the day interviewer from a simulated user
└── src/cltl
    ├── demo_chatbot       the day interviewer agent, a chat window and statistics of a day
    ├── simulated_user     a simulated user that plays the person of an example day
    ├── task_evaluation    evaluation of a collected day against a GOLD day
    └── emissor_evaluation turn-by-turn analyses of EMISSOR conversations and plots
```

### The modules in ```src/cltl```

Each module has its own README with the details:

| Module | What it does |
| --- | --- |
| [```demo_chatbot```](src/cltl/demo_chatbot/README.md) | A scripted agent, the **day interviewer**, that asks a user about their day, hour by hour or per part of the day, and uses an LLM to fill the events of the day from the answers. It comes with a chat window for Jupyter and a script for the statistics of a day. This is the baseline agent that you improve in the course. |
| [```simulated_user```](src/cltl/simulated_user/README.md) | A **simulated user**: an LLM that plays the person of one of the example days and answers the questions of the agent. It lets you test an agent many times without a human user. |
| [```task_evaluation```](src/cltl/task_evaluation/README.md) | The **task-based evaluation**: compares a collected day with a GOLD day on the level of events, roles and role-fillers, with precision, recall and f1, and measures the effectiveness of the communication per turn. |
| [```emissor_evaluation```](src/cltl/emissor_evaluation/README.md) | **Interaction analyses** of EMISSOR scenarios: likelihood, LLM as a judge, dialogue acts, emotions, knowledge graph metrics and human evaluation, plus notebooks for plotting and correlating the scores. |

Most modules have a Jupyter notebook that walks through the code step by step, and a Python script that can be run from the command line.

### The data

The ```data``` folder contains:

* ```emissor```: the interaction data of a few scenarios to demonstrate the EMISSOR analyses. Point the notebooks to your own EMISSOR folder to analyse your own interactions.
* ```example_days```: five GOLD descriptions of a day in somebody's life (a student, a nurse, a retiree, a developer and a baker), with 20 events each, a ```<name>_meta.json``` file with their statistics and a ```photos``` folder with photos of some of the events.
* ```collected_days```: the days collected by the day interviewer, with their statistics and evaluations.
* ```simulated_days```: the days collected by the day interviewer from a simulated user.

## Installation

### 1. Clone the repository

```bash
git clone git@github.com:cltl/ma-communicative-robots.git
cd ma-communicative-robots
```

### 2. Create a Python environment and install the requirements

The code is tested with Python 3.11. Create a virtual environment with venv or Conda and install the packages in ```requirements.txt```. The last command registers the environment as a kernel for Jupyter, so that you can select it in the notebooks.

Using venv:

```bash
python3.11 -m venv combot
source combot/bin/activate          # on Windows: evaluate\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m ipykernel install --user --name=combot
```

Using Conda:

```bash
conda create -n combot python=3.11
conda activate combot
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m ipykernel install --user --name=combot
```

```requirements.txt``` installs:

* ```torch``` and ```transformers``` for the models of the likelihood, dialogue act and emotion analyses. The models are downloaded from [huggingface.co](https://huggingface.co) the first time they are used.
* ```openai``` as the client for the local llama.cpp server, and ```ollama``` for the LLM as a judge with the ollama cloud service.
* ```emissor``` and ```cltl.combot``` from GitHub for reading and writing EMISSOR scenarios.
* ```pandas```, ```matplotlib```, ```seaborn```, ```scipy```, ```rdflib``` and ```networkx``` for the analyses and the plots.
* ```jupyter``` and ```ipywidgets``` for the notebooks and the chat window.

With the environment active, launch Jupyter from the root of the repository and select the ```evaluate``` kernel in the notebooks:

```bash
jupyter lab
```

The scripts are run as modules from the root of the repository, e.g. ```python -m src.cltl.demo_chatbot.day_interviewer```.

### 3. Install llama.cpp

The day interviewer, the simulated user and the LLM as a judge use an LLM that runs on your own computer with [llama.cpp](https://github.com/ggml-org/llama.cpp). llama.cpp is not a Python package: it is a program, ```llama-server```, that serves a model in the GGUF format through an API that is compatible with the OpenAI API. The Python code talks to it with the ```openai``` client installed by ```requirements.txt```, so you do not need to install ```llama-cpp-python```.

Install llama.cpp in one of the following ways (see the [installation instructions](https://github.com/ggml-org/llama.cpp/blob/master/docs/install.md) for more options):

* macOS or Linux with [Homebrew](https://brew.sh): ```brew install llama.cpp```
* Windows: ```winget install llama.cpp```
* any platform: download a prebuilt binary for your system from the [releases page](https://github.com/ggml-org/llama.cpp/releases) and add the folder with ```llama-server``` to your ```PATH```
* build it from source, see [building llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md)

Check the installation with:

```bash
llama-server --version
```

### 4. Start the llama.cpp server

Start the server in a separate terminal before you run the agent, the simulated user or the LLM as a judge, and keep it running:

```bash
llama-server -hf Qwen/Qwen2.5-7B-Instruct-GGUF:Q4_K_M --port 8080 -c 4096
```

* ```-hf``` downloads the model from huggingface.co the first time (about 4.7 GB) and keeps it in a cache for the next time. Use ```-m <file>.gguf``` instead to serve a GGUF model that you downloaded yourself. Other models can be found on [huggingface.co](https://huggingface.co/models?library=gguf). A 7B model with the ```Q4_K_M``` quantisation needs about 6 GB of memory; take a smaller model such as ```Qwen/Qwen2.5-3B-Instruct-GGUF:Q4_K_M``` if your computer has less.
* ```--port 8080``` is the port that the code expects: the address of the server is ```http://localhost:8080/v1``` (```LLAMA_CPP_URL``` in the notebooks, ```--url``` in the scripts).
* ```-c 4096``` is the size of the context in tokens.

The server is ready when it prints that it is listening on port 8080. You can check that it works with:

```bash
curl http://localhost:8080/v1/models
```

The server serves the model it was started with, the code asks the server for its name. To change the model, stop the server with ```Ctrl+C``` and start it again with another model.

### 5. Optional: ollama cloud

The notebook ```llm_as_a_judge_ollama_cloud.ipynb``` uses a bigger model in the [ollama cloud service](https://ollama.com/cloud) instead of llama.cpp. It needs an API key, see the [README of emissor_evaluation](src/cltl/emissor_evaluation/README.md#coherence-with-an-llm-as-a-judge).

## How to proceed

1. Follow the installation above and start the llama.cpp server.
2. Talk to the day interviewer in ```src/cltl/demo_chatbot/day_interviewer.ipynb``` about one of the example days and evaluate the collected day with ```src/cltl/task_evaluation/day_evaluation.ipynb```, or let a simulated user do the talking in ```src/cltl/simulated_user/simulated_day_interview.ipynb```.
3. Analyse your conversations turn by turn with the notebooks in ```src/cltl/emissor_evaluation``` and plot the results.
4. Improve the agent and measure whether it collects better days in fewer turns.

## References

Feel free to use our work but cite us:

* Baez Santamaria, S., Baier, T., Kim, T., Krause, L., Kruijt, J., & Vossen, P. (2021). EMISSOR: A platform for capturing multimodal interactions as episodic memories and interpretations with situated scenario-based ontological references. In Proceedings of the First workshop Beyond Language: Multimodal Semantic Representations in conjunction with IWCS 2022
* T. Baier, S. Báez Santamaría, P. Vossen: A modular architecture for creating multimodal embodied agents with an episodic Knowledge Graph as an explainable and controllable long-term memory, in: Dialogue & Discourse Volume 14, ed. 3, pages 25-59

## Troubleshooting

* **The agent cannot reach the llama.cpp server**: check that ```llama-server``` is running in another terminal on port 8080 and that ```curl http://localhost:8080/v1/models``` answers.
* **```ModuleNotFoundError: No module named 'src'```**: run the scripts from the root of the repository, and select the ```evaluate``` kernel in the notebooks.
* **A model from huggingface does not download**: check your internet connection, or download the model yourself and pass the path to your local copy.

For other problems, see the GitHub issue tab. If you can't find what you want, feel free to raise an issue. We are pretty responsive.

## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
1. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
1. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
1. Push to the Branch (`git push origin feature/AmazingFeature`)
1. Open a Pull Request

## Authors

- Piek Vossen (piek.vossen@vu.nl)
- Thomas Baier (t.baier@vu.nl)
