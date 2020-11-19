# Multimodal
This directory includes works by Taewoon Kim (t.kim@vu.nl).

## MELD Datasets

Download the full datasets from here https://affective-meld.github.io/.

There are in total of 1039, 114, and 280 dialogues in train, dev, and test datasets, respectively. 

To start small, I've randomly selected 200, 20, and 20 dialogues from the original train dataset to create a `small_dataset.json`. 

Again, I've also randomly selected 500, 50, and 50 dialogues from the original train dataset to create a `medium_dataset.json`.

I've created a list of videos, `vids-dyadic.json`, where only dyadic conversations took place. There are 20, 15, and 19 dialogues, each of which has 99, 81, and 78 utterances, respectively. The video files are saved in `dyadic-dataset`.

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
* `dyadic-extraction.ipynb` to find the dyadic videos.
* `copy-dyadic-videos.ipynb` to copy the dyadic videos.

## Google colab
