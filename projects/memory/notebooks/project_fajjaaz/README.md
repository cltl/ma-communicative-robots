The semantic_only.ipynb runs two different ways of using semantic memories to predict answers.
The first model only creates prompts using semantic memories and the question.
The second model first loops over the all the episodic memories in the json file and counts for each object how many times they appear at a certain location.
So now for example if the capacity of the memory is 4, this model can get the 4 most frequent locations for the object that is being asked and use that in a prompt.
The prompts now consists of episodic memories, semantic memories created from the episodic memories and the question.
