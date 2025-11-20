In this package you find to code to annotate EMISSOR data. These annotations can give insight into the quality of the interaction.

1. Installation

The next preparations should be done in a terminal before launching the notebook. 

Open a terminal and do the following preparations:

1.1. Define a Python venv or Conda environment. Here we use annotate as the name for the environment:

```
>python -m venv annotate
>conda create -n annotate
```

Activate the environment. See the documentation how to activate. 
After activation the terminal prompt should be prefixed with (annotate).
Upgrade pip in the new environment.
```
(annotate)>pip install --upgrade pip
```
1.2. Install the necessary packages: 

With annotate activated install the requirements:

```
(annotate)>pip install -r requirements.txt
```

1.3. Download the spaCy language module:
The linguistic annotator uses spaCy for which we need to download a language module in our annotate environment:

```
(annotate)>python -m spacy download en_core_web_sm
```

1.4. Add jupyter to your environment

To make sure that Jupyter will know the annotate environment, we need to do the following:

(annotate)>python -m ipykernel install --user --name=annotate

1.5. Launch Jupter in the annotate environment and open this notebook:

```
(annotate)>jupyter lab
```

2. From the command line:

Instead of using the notebook, you can also run the scripts from the command line to annotate any EMISSOR scenario. 
Annotate your scenarios in your emissor folder:

### CLTL/midas-da-xlmroberta
(annotate)>python annotate_emissor_conversation_with_dialogue_acts.py --emissor "./data/emissor" --scenario 14a1c27d-dfd2-465b-9ab2-90e9ea91d214 --model_path CLTL/midas-da-xlmroberta --model_name MIDAS

## AnasAlokla/multilingual_go_emotions
(annotate)>python annotate_emissor_conversation_with_emotions.py --emissor "./data/emissor" --scenario 14a1c27d-dfd2-465b-9ab2-90e9ea91d214 --model_path AnasAlokla/multilingual_go_emotions --model_name GO

(annotate)>python annotate_emissor_conversation_with_llm_likelihood.py --emissor "./data/emissor"

(annotate)>python annotate_emissor_conversation_with_text_mentions.py --emissor "./data/emissor"

