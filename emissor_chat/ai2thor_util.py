from ai2thor.controller import Controller
import numpy as np

actions = ["find", "describe", "move", "go", "forward", "back", "left", "right", "open", "close"]

def getdistance(coord1, coord2):
    distance = np.sqrt((coord2['x'] - coord1['x'])**2 
                    + (coord2['y'] - coord1['y'])**2 
                    + (coord2['z'] - coord1['z'])**2)
    return distance

def search_for_object_in_view(objectType, event):
    found = []
    for object1 in event.metadata['objects']:
        if object1['objectType'].lower()==objectType.lower():
            coord1 = object1['position']
            closest = 100
            closest_object = None
            for object2 in event.metadata['objects']:
                if not object1['name']==object2['name']:
                    coord2 = object2['position']
                    distance = getdistance(coord1, coord2)
                    if distance>0 and distance<closest:
                        closest = distance
                        closest_object= object2
            found.append((object1, closest, closest_object))
    return found

def search_for_object(objectType, event, controller):
    found = search_for_object_in_view(objectType, event)
    rotate =0
    while not found and rotate<4:
        event = controller.step("RotateLeft")
        found = search_for_object_in_view(objectType, event)
        rotate += 1
    if not found:
        print("I could not find it. Shall I move?")
    else:
        print("I found ", len(found), " of those.")
        for f in found:
            print(f[0]['objectType'], f[1], ' pixels away from ', f[2]['objectType'])
            affordances = get_true_properties(f[0])
            print("These are its properties:", affordances)
    return found
            
def what_do_you_see(event):
    print("I see ", len(event.metadata['objects']), " things here.")
    for object in event.metadata['objects']:
        print(object['objectType'])
        if object['moveable']:
            print("\tI can move you")
        if object['openable']:
            print("\tI can open you")
        if object['breakable']:
            print("\tI can break you")
            
def get_true_properties(object):
    affordances = []
    for key in object.items():
        if key[1]==True:
            affordances.append(key[0])
            #print("Shall I ", key[0], " it?")
    return affordances


def what_i_can_do():
    print("I can do the following:", actions)        

        
def do_action(controller, w1, w2):
    event = None
    found_objects = []
    try:
        event = controller.step("RotateLeft")
        if event:
            if w1.lower()=="find":
                found_objects = search_for_object(w2, event, controller)
            elif w1.lower()=="describe":
                what_do_you_see(event)

            elif w1.lower()=="move" or w1.lower()=="go":
                if w2.lower()=="forward":
                    event = controller.step("MoveAhead")
                elif w2.lower()=="back":
                    event = controller.step("MoveBack")
                elif w2.lower()=="left":
                    event = controller.step("RotateLeft")
                elif w2.lower()=="right":
                    event = controller.step("RotateRight")
    except:
        print("Could not move.")

    if not event:
        print("Cannot do that!")
    return found_objects

def process_instruction(event, prompt):
    words = prompt.split()
    if words[0].lower() in actions:
        found_objects = do_action(event, words[0].lower(), words[-1].lower())
    else:
        print("Sorry I do not get that.")
        