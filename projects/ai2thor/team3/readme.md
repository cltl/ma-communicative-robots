# Communicative-Robots
## AI2-THOR Environment Interaction Agent

This repository contains the code for an AI agent designed to navigate and interact within the AI2-THOR environment. The agent leverages Google Colab's computational resources and integrates with AI2-THOR's modules to perform a series of actions, including movement and object recognition, guided by user input.

## Setup and Configuration

- The virtual environment is set up using the AI2-THOR framework.
- A server utilizing Google Colab's resources is created for running the simulation.
- The AI agent is equipped with movement-controlling functions to navigate within the environment.

## Movement Functions

The agent has several movement functions, allowing it to:
- Rotate in place to survey the environment from various angles (`right_side`, `front_right_side`, `left_side`, etc.).
- Move forward in the direction it's facing with the `front_side` function.
- Teleport to random or specific reachable points using `teleport_randomly` and `move_to_closest_point` functions.

## Classification and Decision Making

- A logistic regression model is trained on room classification data to predict the type of location based on textual descriptions.
- Room views are generated and captioned, and these captions are used to match the agent's location with a user's description.

## Interaction Flow

- User input is processed, and actions are performed based on similarity scores between the environment's state and the user's description.
- The agent follows a decision-making process to identify objects within the environment, as illustrated in the flowchart ![AI2-THOR Interaction Flowchart](https://github.com/Mohammed-majeed/Communicative-Robots/blob/main/AI2Thor_graph.png).
