import os

def check_scenario_data(scenario_folder, scenario):
    HAS_SCENARIO = False
    HAS_TEXT = False
    HAS_IMAGE = False
    HAS_RDF = False
    if not os.path.exists(scenario_folder):
        print("Cannot locate the scenario folder:", scenario_folder)
    else:
        for f in os.listdir(scenario_folder):
            #print(f)
            if f==scenario+'.json':
                HAS_SCENARIO=True
            if (scenario+'.json').endswith(f):
                HAS_SCENARIO=True
            elif f=='text.json':
                HAS_TEXT=True
            elif f=='image.json':
                HAS_IMAGE=True
            elif f=='rdf':
                HAS_RDF=True
    return HAS_SCENARIO, HAS_TEXT, HAS_IMAGE, HAS_RDF
