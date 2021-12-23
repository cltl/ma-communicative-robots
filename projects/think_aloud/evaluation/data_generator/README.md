## Usage

In order to generate a dataset such as `eval_contexts.txt`, run `generate_dataset_from_templates.py` using one of the following commands:

<b>Windows:</b>

`$ py -3 generate_dataset_from_templates.py`

<b>Ubuntu:</b>

`$ python3 generate_dataset_from_templates.py`

This will take the dialogue templates in `templates.txt` and will create a text file called `eval_contexts2.txt` in which all templates are populated.

To evaluate our systems, also run `collect_brain_responses.py` using the generated dataset as an argument to generate the needed brain responses for the repliers:

`$ py -3 collect_brain_responses.py --eval_data=eval_contexts2.txt`

<b>Ubuntu:</b>

`$ python3 collect_brain_responses.py --eval_data=eval_contexts2.txt`
