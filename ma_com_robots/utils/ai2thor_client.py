from ai2thor.controller import Controller
from leolani_client import Action
import numpy as np
from PIL import Image

ACTIONS = ["find", "describe", "move", "go", "turn", "forward", "back", "left", "right", "open", "close", "look"]
DIRECTIONS = ["up", "down", "forward", "back", "left", "right"]
OBJECTS = ["alarmclock", "apple", "applesliced", "armchair", "baseballbat", "basketball", "bathtub", "bathtubbasin", "bed", "blinds", "book", "boots", "bottle", "bowl", "box", "bread", "breadsliced", "butterknife", "cabinet", "candle", "cart", "cd", "cellphone", "chair", "cloth", "coffeemachine", "coffeetable", "countertop", "creditcard", "cup", "curtains", "desk", "desklamp", "dishsponge", "diningtable", "drawer", "dresser", "egg", "faucet", "floorlamp", "footstool", "fork", "fridge", "garbagecan", "handtowel", "handtowelholder", "houseplant", "kettle", "keychain", "knife", "ladle", "laptop", "laundryhamper", "laundryhamperlid", "lettuce", "lettucesliced", "lightswitch", "microwave", "mirror", "mug", "newspaper", "ottoman", "painting", "pan", "papertowel", "pen", "pencil", "peppershaker", "pillow", "plate", "plunger", "poster", "pot", "potato", "potatosliced", "remotecontrol", "safe", "saltshaker", "scrubbrush", "shelf", "showercurtain", "showerdoor", "showerglass", "showerhead", "sidetable", "sink", "sinkbasin", "soapbar", "soapbottle", "sofa", "spatula", "spoon", "spraybottle", "statue", "stoveburner", "stoveknob", "teddybear", "television", "tennisracket", "tissuebox", "toaster", "toilet", "toiletpaper", "toiletpaperhanger", "tomato", "tomatosliced", "towel", "towelholder", "tvstand", "vase", "watch", "wateringcan", "window", "winebottle"]

class Ai2ThorClient:

    def __init__(self):
        """
        returns: None
        """
        self._answers =[]
        self._actions=[]
        self._perceptions=[]
        self._controller = Controller()
        #self._controller.renderInstanceSegmentation = True
        self._controller.renderObjectImage = True
        self._controller.agentMode = "arm"
        self._event = None

    def getdistance(self, coord1, coord2):
        distance = np.sqrt((coord2['x'] - coord1['x'])**2
                        + (coord2['y'] - coord1['y'])**2
                        + (coord2['z'] - coord1['z'])**2)
        return distance

    def search_for_object_in_view_near(self, objectType):
        found = []
        for object1 in self._event.metadata['objects']:
            if object1['objectType'].lower()==objectType.lower():
                print('object1', object1)
                coord1 = object1['position']
                closest = 100
                closest_object = None
                for object2 in self._event.metadata['objects']:
                    if not object1['name']==object2['name']:
                        coord2 = object2['position']
                        distance = self.getdistance(coord1, coord2)
                        if distance>0 and distance<closest:
                            closest = distance
                            closest_object= object2
                found.append((object1, closest, closest_object))
        return found

    def search_for_object_in_view(self, objectType):
        found = []
        for obj in self._event.metadata['objects']:
            if obj['objectType'].lower()==objectType.lower():
                #coord = self._event.instance_detections2D.get(obj['name'])
                #print(coord)
                coord = obj['position']
                image = Image.fromarray(self._controller.last_event.frame)
                found.append((obj, objectType, coord, image))
        return found
        
    def search_for_object(self, objectType):
        answer = ""
        found = self.search_for_object_in_view(objectType)
        rotate =0
        while not found and rotate<4:
            self._event = self._controller.step(Action.RotateRight.name)
            found = self.search_for_object_in_view(objectType)
            rotate += 1
        if not found:
            answer = "I could not find it. Should I move?"
        else:
            answer = "I found %s instances of type %s in my view" % (len(found), objectType) 
            for f,objectType, coord, _ in found:
                answer += "\n"+f['name'] +" at " + str(coord)
                # affordances = self.get_true_properties(f)
                # answer += "These are its properties:"
                # for affordance in affordances:
                #     print(affordance)
        return answer, found

    def what_do_you_see(self):
        answer =  "I see %s things there.\n" % (len(self._event.metadata['objects']))
        for obj in self._event.metadata['objects']:
            answer += obj['objectType']+"\n"
            if obj['moveable']:
                answer += "\tI can move it.\n"
            if obj['openable']:
                answer += "\tI can open it.\n"
            if obj['breakable']:
                answer +="\tI can break it.\n"
        return answer

    def get_true_properties(self, object):
        affordances = []
        for key in object.items():
            if key[1]==True:
                affordances.append(key[0])
        return affordances

    def what_i_can_do(self):
        answer =  "I can do the following:", str(ACTIONS)
        return answer

    def do_action(self, actionWord:str, objectWord:str, directionWord: str):
        answer = ""
        found_objects = []
        if actionWord=="find" and objectWord:
            answer, found_objects = self.search_for_object(objectWord)
            self._actions.append(Action.Look)

        elif actionWord=="describe":
            answer = self.what_do_you_see()
            
        elif actionWord=="look" and directionWord:
            if directionWord.lower()=="up":
                self._event =self._controller.step(Action.LookUp.name)
                self._actions.append(Action.LookUp)
            elif directionWord.lower()=="down":
                self._event = self._controller.step(Action.LookDown.name)
                self._actions.append(Action.LookDown)
                
        elif actionWord=="move" or actionWord=="go" or actionWord=="turn":
            if directionWord=="forward":
                self._event =self._controller.step(Action.MoveAhead.name)
                self._actions.append(Action.MoveAhead)
            elif directionWord=="back":
                self._event = self._controller.step(Action.MoveBack.name)
                self._actions.append(Action.MoveAhead)
            elif directionWord=="left":
                self._event = self._controller.step(Action.RotateLeft.name)
                self._actions.append(Action.RotateLeft)
            elif directionWord=="right":
                self._event = self._controller.step(Action.RotateRight.name)
                self._actions.append(Action.RotateRight)

        return answer, found_objects

    def process_instruction(self, prompt):
        #print('OBJECTS', self._controller.event.metadata["objects"])
        self._answers =[]
        self._actions = []
        self._perceptions = []
        answer = ""
        words = prompt.split()
        actionWord = None
        objectWord = None
        directionWord = None
        for word in words:
            if word.lower() in ACTIONS:
                actionWord = word.lower()
                break
        for word in words:
            if word.lower() in OBJECTS:
                objectWord = word.lower()
                break
        for word in words:
            if word.lower() in DIRECTIONS:
                directionWord = word.lower()
                break
        if actionWord:
            self._event = self._controller.step(Action.MoveAhead.name)
            answer, found_objects = self.do_action(actionWord=actionWord, objectWord=objectWord, directionWord=directionWord)
            if answer:
                self._answers.append(answer)
            if found_objects:
                self._perceptions.extend(found_objects)
        else:
            answer = "Sorry I do not get that:"+words[0]
            self._answers.append(answer)


if __name__ == "__main__":
    AGENT = "AI2Thor"
    HUMAN = "Human"
    ai2ThorClient = Ai2ThorClient()
    utterance = input(HUMAN+"> ")
    while not (utterance.lower() == "stop" or utterance.lower() == "bye"):
            ai2ThorClient.process_instruction(utterance)
            for utterance in ai2ThorClient._answers:
                print(AGENT+">"+str(utterance))
            utterance = input(HUMAN+"> ")
    ai2ThorClient._controller.stop()