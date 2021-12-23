## Usage

To generate a dataset such as the `eval_contexts.txt` used for the evaluation, run `generate_dataset_from_templates.py` using one of the following commands:

<b>Windows:</b>

`$ py -3 generate_dataset_from_templates.py`

<b>Ubuntu:</b>

`$ python3 generate_dataset_from_templates.py`

This will take the dialogue templates in `templates.txt` and will create a text file called `eval_contexts2.txt` in which all templates are populated randomly with different topics, names, etc.

To evaluate our systems, also run `collect_brain_responses.py` using the generated dataset as an argument to generate the needed brain responses for the repliers:

<b>Windows:</b>

`$ py -3 collect_brain_responses.py --eval_data=eval_contexts2.txt`

<b>Ubuntu:</b>

`$ python3 collect_brain_responses.py --eval_data=eval_contexts2.txt`
