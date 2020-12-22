# Focus on one dataset

We don't have enough time to try all existing datasets. We'll focus on the one dataset, MELD (TV sitcom friends dataset). Go to the [repo](https://affective-meld.github.io/) and download both raw and feature data. Going through the raw data will give you better understanding of multimodal emotion recognition in conversations.

# Different types of modalities

There are three modaltiies in the data. They are audio, visual, and text. Using all of the three modalities for the utterance-level emotion/sentiment classification is not easy. We can think of 7 different scenarios of the combination of the modalities as input data.

1. Audio only
2. Visual only
3. Text only
4. Audio and visual
5. Audio and text
6. Visual and text
7. Audio, visual, and text

The master students are not required to extract the visual features from the visual data. The TA ([Taewoon Kim](https://tae898.github.io/)) will do it (i.e. face, age, and gender), as this should be part of [the leolani platform](https://github.com/leolani/cltl-combot) anyways. The other two projects (Jaap's and Lea's) can take advantage of the visual features if they wish.

# Reproducing the existing work

Although reproducing the existing state of the art is always a good first step, it's not so easy with our given task. The SOTA uses many different features and some of them are simply saved as pickle binary files. Therefore it's not required to reproduce the SOTA. We can still come up with our own simple models and experiment with our own test data, which will be created altogether.
