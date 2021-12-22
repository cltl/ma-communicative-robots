# Text generation system for creating utterances narrating a photo book #

This is the code for the group supervised by Jaap. The only thing you technically need to run it is a working Python 3.7.12 installation (3.7 in general should work).

To generate the data that the utterance generator consumes you'll need to install the requirements of Jaap's generator. The instructions can be found at https://github.com/jaapkruijt/photobook-generation. In our experience, you need specific versions of some of the packages. These seem to do the trick:

* folium==0.2.1
* imgaug==0.2.6
* numpy==1.19

You'll also need to use a special `pip install` command for emissor:

`pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple emissor`

After this, you can clone Jaap's repo:
`git clone https://github.com/jaapkruijt/photobook-generation.git`

## Generator usage ##

You need to make sure that the data to be used is organized exactly as Jaap's repo demonstrates. In other words, it needs to be in the form:
`
scenario\
	|
	|-picture_1\
	|	|
	|	picture_name.json
	|
	|-picture_2\
	|	|...
	...
`

In other words, a scenario is a directory, and every picture is a sub-directory, and every picture's (abstracted) data is in JSON file in that picture's sub-directory.


Assuming this is the case, to use this generator, technically, the only thing you need to do is
`import utterance_generator`

Then you can call
`utterance_generator.narrate_scenario('./photobook-generation/data/scenario_1/')`

and you'll get a dictionary mapping pictures to utterances to be spoken while presenting them. This is just a shortcut of creating a Generator manually and running it over every picture's JSON file.

The `narrate_scenario` function takes multiple arguments that let you specify how to generate the sentences. Please see `utterance_generator_usage.ipynb` for an idea of how to use the components.

## But why not transformers? ##

This is explained in the report, but to see why transformers don't work well for this task, see `transformer_problems.ipynb`. Basically, they don't let you control the output in the way that you'd likely want for this use case.
