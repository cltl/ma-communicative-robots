import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config import SEARCH_STRATEGIES

from typing import Dict, List, Optional


class SearchCoordinator:

    def __init__(self, room_mapper, object_searcher):
        self.room_mapper = room_mapper
        self.object_searcher = object_searcher
        self.communication_log = []
        self.total_actions = 0
        self.max_positions = SEARCH_STRATEGIES['max_positions_per_room']
        self.default_strategy = SEARCH_STRATEGIES['default']

    def find_object(self, target_object: str, room_type: str,
                    context_objects: List[str] = None) -> Dict:
        self._communicate(f"Searching for {target_object} in {room_type}")

        candidate_rooms = self._find_matching_rooms(room_type)

        if not candidate_rooms:
            self._communicate(f"No {room_type} found in house")
            return {'success': False, 'reason': 'room_not_found'}

        self._communicate(f"Found {len(candidate_rooms)} {room_type}(s)")

        best_room = self._select_best_room(candidate_rooms, context_objects)

        self._communicate(f"Searching in {best_room['type']} (ID: {best_room['id']})")

        results = self._search_in_room(best_room, target_object)

        if results['found']:
            self._communicate(f"Found {len(results['objects'])} {target_object}(s)!")
        else:
            self._communicate(f"No {target_object} found")

        return {
            'success': results['found'],
            'objects': results['objects'],
            'room': best_room,
            'total_actions': self.total_actions,
            'communications': len(self.communication_log)
        }

    def _find_matching_rooms(self, room_type: str) -> List[Dict]:
        normalized = room_type.lower().replace(' ', '_')
        matching_rooms = []

        if hasattr(self.room_mapper, 'room_classifications'):
            for room_id, room_info in self.room_mapper.room_classifications.items():
                if normalized in room_info['type'].lower():
                    matching_rooms.append({
                        'id': room_id,
                        'type': room_info['type'],
                        'data': room_info
                    })

        return matching_rooms

    def _select_best_room(self, candidates: List[Dict],
                          context_objects: List[str] = None) -> Dict:
        if len(candidates) == 1:
            return candidates[0]

        if not context_objects:
            return candidates[0]

        best_score = -1
        best_room = candidates[0]

        for room in candidates:
            score = 0
            room_objects = room['data'].get('objects', {})

            for obj in context_objects:
                if obj in room_objects:
                    score += room_objects[obj]

            if score > best_score:
                best_score = score
                best_room = room

        return best_room

    def _search_in_room(self, room: Dict, target_object: str) -> Dict:
        positions = self._get_room_positions(room)

        if not positions:
            return {'found': False, 'objects': []}

        start_pos = positions[0]

        if hasattr(self.object_searcher, 'reset'):
            self.object_searcher.reset()

        found_objects = self.object_searcher.search_from_position(
            start_pos,
            target_object,
            strategy=self.default_strategy
        )

        if hasattr(self.object_searcher, 'get_action_count'):
            self.total_actions += self.object_searcher.get_action_count()

        if not found_objects and len(positions) > 1:
            self._communicate("Trying additional positions...")

            for pos in positions[1:self.max_positions]:
                if hasattr(self.object_searcher, 'reset'):
                    self.object_searcher.reset()

                found_objects = self.object_searcher.search_from_position(
                    pos,
                    target_object,
                    strategy=self.default_strategy
                )

                if hasattr(self.object_searcher, 'get_action_count'):
                    self.total_actions += self.object_searcher.get_action_count()

                if found_objects:
                    break

        return {
            'found': len(found_objects) > 0,
            'objects': found_objects
        }

    def _get_room_positions(self, room: Dict) -> List[Dict]:
        if 'positions' in room['data']:
            return room['data']['positions']

        if hasattr(self.room_mapper, 'data'):
            return [d['position'] for d in self.room_mapper.data
                    if d.get('cluster') == room['id']]

        return []

    def _communicate(self, message: str):
        self.communication_log.append({
            'message': message,
            'actions_so_far': self.total_actions
        })
        print(f"Robot: {message}")

    def reset_metrics(self):
        self.metrics = {
            'total_actions': 0,
            'total_communications': 0,
            'rooms_visited': 0,
            'objects_found': 0
        }

    def get_metrics(self) -> Dict:
        return {
            'total_actions': self.total_actions,
            'total_communications': len(self.communication_log),
            'action_per_communication': (
                self.total_actions / len(self.communication_log)
                if self.communication_log else 0
            )
        }
