# Datasets
Download the full datasets from here https://affective-meld.github.io/.

There are in total of 1039, 114, and 280 dialogues in train, dev, and test datasets, respectively. To start small, I've randomly selected 200, 20, and 20 dialogues from the original train dataset to create a `small_dataset.json`. Again, I've also randomly selected 500, 50, and 50 dialogues from the original train dataset to create a `medium_dataset.json`.  

# Visual feature extraction from the videos.

There is a lot of information in the videos (moving pictures). However, we can’t use all of it and we have to prioritize. Therefore, we’ll first extract the information from the faces.

Facial feature extraction can be done as follows:

## Face detection
This is normally always the first step. This is to get the bounding boxes around the faces. This is implemented here: https://github.com/leolani/cltl-facedetection. The predictions on the MELD dataset are saved as json. [Here](https://drive.google.com/drive/folders/1BllPXGAOH434O6P35bKuFcVUzfTEaSxf?usp=sharing) is the link.

## Face embeddings
After cropping the face using the bounding box, we can compute their embeddings. Face recognition (i.e. trying to determine who this person is) is normally done using the embedding vectors. This will be implemented here: https://github.com/leolani/cltl-facerecognition 

## Face landmarks
The face detection I’ve implemented actually gives you five landmarks. This can be enough in some cases, but there are other landmark detectors that give you 68 or even more landmarks. Face landmarks are very useful (e.g. deep fake, avatar, etc.). But I’m not sure how relevant this is to our case. Nonetheless, I’ll implement this at https://github.com/leolani/cltl-facelandmark

## Age/Gender
As far as I understood, a lot of neural networks predict age and gender altogether. This is not a surprise since the information can be shared. This will be implemented at https://github.com/leolani/cltl-genderdetection and https://github.com/leolani/cltl-agedetection 

I’ll implement the four repos as soon as possible. As of writing this page (4th of November, 2020), I’ve implemented the first and currently working on the second.

I’ll upload the extracted features on google drive so that you can download and use them.

At CLTL, we aim to use all of the above repos for our future Leolani platform. With such given information, we believe that Leolani can better understand the world, and thus better communicate with us.


# Signal time-alignment

I’m thinking about how this can be done.

Let’s say that we are given an utterance, say, 3 seconds. Let’s assume that the fps of this video is 24. Then the number of images in this utterance is 24 fps * 3s = 72 frames.  In other words, there are 72 consecutive images in this utterance. 

The utterance comes with an audio file too. Let’s assume that the audio is mono and the sampling rate of the audio is 16000 Hz. Then the number of points is 16000 Hz * 3s = 48000.

The utterance also comes with an annotated text as well. Let’s assume that for the 3 seconds what was spoken was “Challenges are what make life interesting and overcoming them is what makes life meaningful.” If we tokenize the sentence, then it’ll give us 14 tokens. 

The three different modalities all give us different time length. Of course we can just resample them so that they can have the same time length, but there’s gotta be a better and smarter way.

