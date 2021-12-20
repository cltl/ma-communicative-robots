""" Filename:     main.py
    Author(s):    Thomas Bellucci
    Description:  This file contains the interaction loop for the Chatbot defined in chatbots.py. By
                  typing 'plot' the chatbot will plot a graph with learnt thought statistics (if mode='RL')
                  and 'quit' ends the interaction.
    Date created: Nov. 11th, 2021
"""

import argparse
from chatbots import Chatbot


def main(args):
    """ Runs the main interaction loop of the chatbot.
    """
    # Sets up chatbot with a Lenka-, RL- or NSPReplier
    chatbot = Chatbot(args.speaker, args.mode, args.savefile)
    print('\nBot:', chatbot.greet)

    # Interaction loop
    while True:
        say = input('\nYou: ')

        if say == 'quit':
            break

        if say == 'plot':
            chatbot.replier.thought_selector.plot()
            continue

        print('\nBot:', chatbot.respond(say))

    # Farewell + update savefile
    print('\nBot:', chatbot.farewell)
    chatbot.close()
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--speaker', default='john', type=str,
                        help="Name of the speaker (e.g. 'john')")
    parser.add_argument('--mode', default='RL', type=str, choices=['RL', 'NSP', 'Lenka'],
                        help="Thought selection method: {'RL', 'NSP', 'Lenka'}")
    parser.add_argument('--savefile', default='reinforcement_learning/thoughts.json', type=str,
                        help='Path to BERT for NSP (--method=NSP) or RL JSON (--method=RL)')
    args = parser.parse_args()
    print('\nUsing mode=%s with %s and speaker %s.\n' % (args.mode, args.savefile, args.speaker))

    main(args)
    

    
