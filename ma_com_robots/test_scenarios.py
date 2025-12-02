#!/usr/bin/env python3
import sys
from pathlib import Path

project_root = Path(__file__).parent
src_path = project_root / 'src'

sys.path.insert(0, str(project_root))
sys.path.insert(0, str(src_path))

from integration.coordinator import SearchCoordinator
from object_search.object_searcher import ObjectSearcher
from room_mapping.room_mapper import RoomMapper

import prior
from ai2thor.controller import Controller

try:
    from config import AI2THOR_CONFIG
except:
    AI2THOR_CONFIG = {
        'visibilityDistance': 2,
        'width': 750,
        'height': 750,
        'default_house_id': 15
    }


def main():
    print("=" * 70)
    print("COMMUNICATIVE ROBOT - MULTI-SCENARIO TEST")
    print("=" * 70)
    
    try:
        house_id = AI2THOR_CONFIG['default_house_id']
        print(f"\nLoading house {house_id}...")
        
        dataset = prior.load_dataset("procthor-10k")
        house = dataset["train"][house_id]
        
        controller = Controller(
            scene=house,
            visibilityDistance=AI2THOR_CONFIG['visibilityDistance'],
            width=AI2THOR_CONFIG['width'],
            height=AI2THOR_CONFIG['height']
        )
        
        print("\nInitializing components...")
        room_mapper = RoomMapper(controller)
        room_mapper.initialize_house_map()
        
        object_searcher = ObjectSearcher(controller)
        
        # Test scenarios
        scenarios = [
            ('Painting', 'living_room', ['Sofa', 'ArmChair', 'Television']),
            ('Knife', 'kitchen', ['CounterTop', 'Fridge', 'StoveBurner']),
            ('Pillow', 'bedroom', ['Bed', 'Dresser', 'Cabinet']),
            ('Box', 'living_room', ['ArmChair', 'Window'])
        ]
        
        all_results = []
        
        for target, room, context in scenarios:
            print(f"\n{'='*70}")
            print(f"SCENARIO: {target} in {room}")
            print(f"{'='*70}")
            
            # New coordinator per scenario for clean metrics
            coordinator = SearchCoordinator(room_mapper, object_searcher)
            
            result = coordinator.find_object(
                target_object=target,
                room_type=room,
                context_objects=context
            )
            
            metrics = coordinator.get_metrics()
            
            print(f"\nRESULTS:")
            print(f"  Success: {result['success']}")
            print(f"  Actions: {metrics['total_actions']}")
            print(f"  Communications: {metrics['total_communications']}")
            
            if metrics['total_actions'] > 0:
                reduction = ((95 - metrics['total_actions']) / 95) * 100
                print(f"  Improvement: {reduction:.1f}% vs traditional")
            
            all_results.append({
                'target': target,
                'room': room,
                'success': result['success'],
                'actions': metrics['total_actions'],
                'comms': metrics['total_communications']
            })
        
        # Summary
        print("\n" + "=" * 70)
        print("SUMMARY OF ALL SCENARIOS")
        print("=" * 70)
        
        total_success = sum(1 for r in all_results if r['success'])
        avg_actions = sum(r['actions'] for r in all_results) / len(all_results)
        avg_comms = sum(r['comms'] for r in all_results) / len(all_results)
        
        print(f"\nSuccess rate: {total_success}/{len(scenarios)} ({total_success/len(scenarios)*100:.1f}%)")
        print(f"Average physical actions: {avg_actions:.1f}")
        print(f"Average communications: {avg_comms:.1f}")
        
        print("\nIndividual Results:")
        for i, r in enumerate(all_results, 1):
            status = "SUCCESS" if r['success'] else "FAILED"
            print(f"  {i}. [{status}] {r['target']} in {r['room']}: {r['actions']} actions, {r['comms']} comms")
        
        controller.stop()
        print("\nAll scenarios complete!")
        return 0
        
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
