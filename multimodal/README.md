# Multimodal
This directory includes works by Taewoon Kim (t.kim@vu.nl).

## MELD Datasets

Download the full datasets from here https://affective-meld.github.io/.

I've also created smaller datasets from the original train dataset. The mp4 videos are saved in `./smaller-dataset`, which includes 80 dialogues, which again include 789 utterances.

`dataset-large.json` has 64, 8, and 8 dialogues in its train, dev, and test dataset, respectively.

`dataset-medium.json` has 32, 4, and 4 dialogues in its train, dev, and test dataset, respectively.

`dataset-small.json` has 16, 2, and 2 dialogues in its train, dev, and test dataset, respectively.

The smaller dataset is part of the bigger dataset's train data.

## MELD Annotations

Full annotations can be found here https://github.com/declare-lab/MELD/tree/master/data/MELD

Dyadic annotations can be found here https://github.com/declare-lab/MELD/tree/master/data/MELD_Dyadic

## Visual feature extraction from the videos

Refer to this python package https://github.com/leolani/cltl-face-all. It gives you every visual feature from a given image.


## Signal time-alignment

I’m thinking about how this can be done.

Let’s say that we are given an utterance, say, 3 seconds. Let’s assume that the fps of this video is 24. Then the number of images in this utterance is 24 fps * 3s = 72 frames.  In other words, there are 72 consecutive images in this utterance. 

The utterance comes with an audio file too. Let’s assume that the audio is mono and the sampling rate of the audio is 16000 Hz. Then the number of points is 16000 Hz * 3s = 48000.

The utterance also comes with an annotated text as well. Let’s assume that for the 3 seconds what was spoken was “Challenges are what make life interesting and overcoming them is what makes life meaningful.” If we tokenize the sentence, then it’ll give us 14 tokens. 

The three different modalities all give us different time length. Of course we can just resample them so that they can have the same time length, but there’s gotta be a better and smarter way.

## Jupyter notebooks (run this locally)
* `smaller-datasets.ipynb` to reproduce the smaller datasets.

## Google colab
* WIP