# ComBots-Ethics
Small Github for the stand-alone pronoun extraction project, based on a simple greeting script
In this script the system, "Leolani" introduces herself and states her pronouns. 
The person interacting is then asked to introduce themselves and by the end of the script their pronouns are stored.

## Files:
File  | Description
------------- | -------------
README.md | This readme file
pronoun_extraction_script.py | The file that will hold the final script and will provide a demo of the system
pseudo_code.py  | Gives a general overview of the defined functions and their defined outputs
run_tests.py | Script to compare the system with a visual baseline system based on a test csv
toy_example_pronoun_detection.py | The first toy example of the NameAPI workings
text_to_pronouns.py | Script to extract the pronouns out of a greeting sentence, including some examples

## API key:
The project makes use of the NameAPI.org API. A key can be obtained here: https://www.nameapi.org/en/register/

## Data:
The data folder contains a sample csv file that shows our data stucture and a subfolder with pictures mentioned in that csv file. The full dataset will not be shared due to it containing sensitive information, but it was collected from several tv-shows ("Hij is een zij", "Are you the one?", "Genderquake"), from social media, via VU pride via a questionnaire, and extended with fake data in the form of pictures with a gender neutral name.

## Dependencies
### cltl-face-all
The system works with the cltl-face-all system, which can be found here: https://github.com/leolani/cltl-face-all/tree/master/cltl_face_all
### Python libraries
* Pandas
* Numpy
* Request
* Nltk
* Datetime
* OpenCV
* Tensorflow
* Pytorch

## Authors
Merel de Groot (m.n.m.de.groot@student.vu.nl)

Quirine Smit (q.t.s.smit@student.vu.nl)
