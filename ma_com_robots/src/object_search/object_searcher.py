from typing import List, Dict, Tuple
from ai2thor.controller import Controller


class ObjectSearcher:
    
    def __init__(self, controller: Controller):

        self.controller = controller
        self.found_objects = []
        self.search_history = []
        self.action_count = 0
        self.dialogue_log = []
    
    def search_from_position(self, 
                            position: Dict, 
                            target_object_type: str,
                            strategy: str = "adaptive") -> List[Dict]:

        print(f"\nStarting {strategy} search for {target_object_type}")
        print(f"   Position: ({position['x']:.2f}, {position['z']:.2f})")
        
        if strategy == "minimal":
            return self._minimal_search(position, target_object_type)
        elif strategy == "thorough":
            return self._thorough_search(position, target_object_type)
        else:  # adaptive
            return self._adaptive_search(position, target_object_type)
    
    def _minimal_search(self, position: Dict, target_type: str) -> List[Dict]:
        # Teleport to position
        self.controller.step(action="Teleport", position=position, rotation=0)
        self.action_count += 1
        self._log_action("Teleport", position)
        
        found = []
        rotations = [0, 90, 180, 270]
        
        for i, rot in enumerate(rotations):
            if i > 0:
                self.controller.step(action="RotateRight")
                self.action_count += 1
                self._log_action("RotateRight", rot)
            
            # Check what's visible
            event = self.controller.last_event
            for obj in event.metadata["objects"]:
                if obj["visible"] and obj["objectType"] == target_type:
                    # Avoid duplicates
                    if not any(f['object_id'] == obj['objectId'] for f in found):
                        found.append({
                            'object_id': obj['objectId'],
                            'object_type': obj['objectType'],
                            'position': obj['position'],
                            'rotation': rot,
                            'distance': obj.get('distance', 0),
                            'strategy_used': 'minimal'
                        })
        
        print(f" Minimal search complete: {len(found)} {target_type}(s) found with {self.action_count} actions")
        return found
    
    def _thorough_search(self, position: Dict, target_type: str) -> List[Dict]:
        """
        Thorough search: 360° rotation + vertical search.
        
        Best for: When objects might be high (on walls) or low (on floor)
        Actions: 1 teleport + 3 rotations + 8 look up/down = 12 actions
        """
        self.controller.step(action="Teleport", position=position, rotation=0)
        self.action_count += 1
        self._log_action("Teleport", position)
        
        found = []
        
        for i in range(4):  # 4 rotations
            if i > 0:
                self.controller.step(action="RotateRight")
                self.action_count += 1
                self._log_action("RotateRight", i * 90)
            
            # Check straight ahead
            self._check_visible_objects(target_type, found, rotation=i*90)
            
            # Look up
            self.controller.step(action="LookUp")
            self.action_count += 1
            self._log_action("LookUp", "checking high objects")
            self._check_visible_objects(target_type, found, rotation=i*90, vertical='up')
            
            # Look back down to horizontal
            self.controller.step(action="LookDown")
            self.action_count += 1
            self._log_action("LookDown", "reset to horizontal")
        
        print(f" Thorough search complete: {len(found)} {target_type}(s) found with {self.action_count} actions")
        return found
    
    def _adaptive_search(self, position: Dict, target_type: str) -> List[Dict]:

        found = self._minimal_search(position, target_type)
        
        if found:
            print(f"Found objects with minimal search - no additional actions needed")
            return found
        
        print(f"Nothing found in minimal search - checking vertical angles")
        
        # Look up at current rotation
        self.controller.step(action="LookUp")
        self.action_count += 1
        self._log_action("LookUp", "adaptive expansion")
        self._check_visible_objects(target_type, found, vertical='up')
        
        if found:
            # Reset view
            self.controller.step(action="LookDown")
            self.action_count += 1
            print(f"Adaptive search complete: {len(found)} {target_type}(s) found with {self.action_count} actions")
            return found
        
        # Still nothing - rotate and look up at other angles
        for i in range(1, 4):
            self.controller.step(action="RotateRight")
            self.action_count += 1
            self._log_action("RotateRight", f"adaptive rotation {i}")
            
            self._check_visible_objects(target_type, found, rotation=i*90, vertical='up')
            
            if found:
                break
        
        self.controller.step(action="LookDown")
        self.action_count += 1
        
        print(f"Adaptive search complete: {len(found)} {target_type}(s) found with {self.action_count} actions")
        return found
    
    def _check_visible_objects(self, target_type: str, found: List[Dict], 
                               rotation: int = 0, vertical: str = 'horizontal'):
        event = self.controller.last_event
        for obj in event.metadata["objects"]:
            if obj["visible"] and obj["objectType"] == target_type:
                if not any(f['object_id'] == obj['objectId'] for f in found):
                    found.append({
                        'object_id': obj['objectId'],
                        'object_type': obj['objectType'],
                        'position': obj['position'],
                        'rotation': rotation,
                        'vertical': vertical,
                        'distance': obj.get('distance', 0)
                    })
    
    def search_multiple_positions(self, 
                                  positions: List[Dict], 
                                  target_type: str,
                                  max_positions: int = 3) -> Tuple[List[Dict], int]:
 
        for i, pos in enumerate(positions[:max_positions]):
            print(f"\n🔍 Searching position {i+1}/{min(len(positions), max_positions)}")
            found = self.search_from_position(pos, target_type, strategy="adaptive")
            
            if found:
                return found, i
        
        return [], -1
    
    def describe_object(self, obj: Dict) -> str:
        description_parts = []
        
        # Basic type
        description_parts.append(f"a {obj['object_type']}")
        
        pos = obj['position']
        description_parts.append(f"at position ({pos['x']:.1f}, {pos['z']:.1f})")
        
        if 'distance' in obj and obj['distance'] > 0:
            description_parts.append(f"about {obj['distance']:.1f}m away")
        
        if obj.get('vertical') == 'up':
            description_parts.append("mounted high (on wall or shelf)")
        elif obj.get('vertical') == 'down':
            description_parts.append("on the floor or low surface")
        
        rotation = obj.get('rotation', 0)
        directions = {0: "ahead", 90: "to the right", 180: "behind", 270: "to the left"}
        if rotation in directions:
            description_parts.append(directions[rotation])
        
        return " ".join(description_parts)
    
    def get_search_summary(self) -> Dict:
        return {
            'total_actions': self.action_count,
            'objects_found': len(self.found_objects),
            'action_history': self.search_history,
            'efficiency': (
                self.action_count / len(self.found_objects) 
                if self.found_objects else self.action_count
            )
        }
    
    def _log_action(self, action_type: str, details):
        self.search_history.append({
            'action': action_type,
            'details': details,
            'total_actions': self.action_count
        })
    
    def reset(self):
        self.action_count = 0
        self.found_objects = []
        self.search_history = []
        self.dialogue_log = []
    
    def get_action_count(self) -> int:
        """Get total actions taken"""
        return self.action_count


# Test code
if __name__ == "__main__":
    import prior
    dataset = prior.load_dataset("procthor-10k")
    house = dataset["train"][15]
    controller = Controller(
        scene=house, 
        visibilityDistance=2, 
        width=750, 
        height=750
    )
    
    event = controller.step(action="GetReachablePositions")
    positions = event.metadata["actionReturn"]
    searcher = ObjectSearcher(controller)
    
    # Test 1: Minimal search
    
    print("TEST 1: MINIMAL SEARCH FOR PAINTING")
    
    searcher.reset()
    results = searcher.search_from_position(
        positions[10], 
        "Painting", 
        strategy="minimal"
    )
    print(f"\nResults: {len(results)} painting(s) found")
    print(f"Actions: {searcher.get_action_count()}")
    
    # Test 2: Adaptive search
    
    print("TEST 2: ADAPTIVE SEARCH FOR CHAIR")
    
    searcher.reset()
    results = searcher.search_from_position(
        positions[5], 
        "Chair", 
        strategy="adaptive"
    )
    print(f"\nResults: {len(results)} chair(s) found")
    print(f"Actions: {searcher.get_action_count()}")
    
    for i, obj in enumerate(results):
        print(f"   {i+1}. {searcher.describe_object(obj)}")
    
    # Test 3: Multiple position search
    
    print("TEST 3: SEARCH MULTIPLE POSITIONS FOR BED")
    
    searcher.reset()
    test_positions = positions[0:5]
    found, found_at = searcher.search_multiple_positions(
        test_positions, 
        "Bed", 
        max_positions=3
    )
    print(f"\nResults: {len(found)} bed(s) found")
    if found_at >= 0:
        print(f"Found at position {found_at + 1}")
    else:
        print(f"Not found in first 3 positions")
    print(f"Total actions: {searcher.get_action_count()}")
    
    # Summary
    
    print("SEARCH SUMMARY")
    
    summary = searcher.get_search_summary()
    print(f"Total actions across all tests: {summary['total_actions']}")
    print(f"Objects found: {summary['objects_found']}")
    
    controller.stop()
    print("\nTesting complete!")