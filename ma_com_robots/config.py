"""
Project Configuration
"""

AI2THOR_CONFIG = {
    'visibilityDistance': 2,
    'width': 750,
    'height': 750,
    'default_house_id': 15
}


''''
'minimal' = Only 360° (4 actions)
'adaptive' = 360° + vertical (4-8 actions)
'thorough' = All (12 actions)
'''

SEARCH_STRATEGIES = {
    'default': 'thorough',
    'max_positions_per_room': 3,
    'enable_vertical_search': True
}


ROOM_SIGNATURES = {
    'kitchen': ['Microwave', 'Fridge', 'StoveBurner', 'Sink'],
    'bathroom': ['Toilet', 'Bathtub', 'Shower'],
    'bedroom': ['Bed', 'Pillow', 'Dresser'],
    'living_room': ['Sofa', 'Television', 'ArmChair'],
}

PERFORMANCE_TARGETS = {
    'max_actions': 15,
    'min_communication_efficiency': 0.70
}
