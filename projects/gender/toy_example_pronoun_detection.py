import random # Only for the example to get a random gender
import requests
NAMEAPI_KEY=
url = ("http://api.nameapi.org/rest/v5.3/genderizer/persongenderizer?"
    f"apiKey={NAMEAPI_KEY}"
)

def get_visual_gender(image=None):
	#TODO: Implement Tae's visual gender package
	'''This should become Tae's Visial Gender detection'''
	return random.random() # Randomly assigning a gender float

def check_gender_name(name):
	'''
	Code from https://www.nameapi.org/index.php?id=215 & https://juliensalinas.com/en/REST_API_fetching_go_golang_vs_python/
	Connects to the NAMEAPI to query the gender of a given name. 
	It returns a dict with the gender of the name and the confidence in this gender.
	Possible gender outcomes: FEMALE, MALE, NEUTRAL, UNKNOWN

	Gender neutral names are mapped to unknown.
	If the query errors, it will print an error message

	param name: the first name of the person conversing with Leolanie
	type name: string

	returns: int (1 for male, 2 for female, 3 for unknown)

	'''
	# Dict of data to be sent to the RESTapi of NameAPI.org:
	payload = {
		"context":{
			"priority" : "REALTIME",
			"properties": []
		},
		"inputPerson": {
			"type": "NaturalInputPerson",
			"personName": {
				"nameFields": [
					{
						"string": f"{name}",
						"fieldType": "GIVENNAME"
					}]
			},
			"gender": "UNKNOWN"
		}
	}

# Proceed, only if no error:
	try:
    # Send request to NameAPI.org by doing the following:
    # - make a POST HTTP request
    # - encode the Python payload dict to JSON
    # - pass the JSON to request body
    # - set header's 'Content-Type' to 'application/json' instead of
    #   default 'multipart/form-data'
		resp = requests.post(url, json=payload)
		resp.raise_for_status()
    # Decode JSON response into a Python dict:
		resp_dict = resp.json()
		name_gender=resp_dict['gender']
		if name_gender == 'NEUTRAL':
			name_gender='UNKNOWN'
		name_gender_conf=resp_dict['confidence']
		return name_gender, name_gender_conf
	except requests.exceptions.HTTPError as e:
		print("Bad HTTP status code:", e)
	except requests.exceptions.RequestException as e:
		print("Network error:", e)



def gender_name_match(name, gender):
	#TODO: implement match script
	'''
	Checks if the gender of the name and gender of the visual data match
	'''
	name_gender, name_gender_conf=check_gender_name(name)
	if name_gender != 'Unknown':
		print('Needs to be implemented')
	return (name_gender)


def create_tuple(name, pronouns):
	# TODO: Implement tuple creation
	'''Returns the rdf-tuple for the Leolani brain'''
	object=name
	predicate= 'has_pronouns'
	subject=pronouns
	print(object, predicate, subject)



def main():
	name= input("Hi, my name is Leolani. My pronouns are she/her. Who are you?\nYour name: ")
	#name="Merel"
	#Bad way to do this, but it is assumed that the Leolani name detection could be directly accessed for the name
	if ' ' in name:
		given_name=name.split()[0]
	else:
		given_name=name

	pronouns=gender_name_match(given_name, gender)

	print(pronouns)



if __name__ == "__main__":
    # execute only if run as a script
    main()
