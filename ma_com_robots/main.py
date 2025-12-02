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
    
    print("COMMUNICATIVE ROBOT SEARCH SYSTEM")
    

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
        print("  - Room mapper (Timo)")
        room_mapper = RoomMapper(controller)
        room_mapper.initialize_house_map()

        print("  - Object searcher (Mohammed)")
        object_searcher = ObjectSearcher(controller)

        coordinator = SearchCoordinator(room_mapper, object_searcher)

        
        print("SEARCH: Painting in living room")
        

        result = coordinator.find_object(
            target_object='Painting',
            room_type='living room',
            context_objects=['Sofa', 'ArmChair', 'Television']
        )

        
        print("RESULTS")
        
        print(f"Success: {result['success']}")
        print(f"Objects found: {len(result.get('objects', []))}")

        if result.get('objects'):
            print("\nFound objects:")
            for i, obj in enumerate(result['objects'], 1):
                pos = obj['position']
                print(f"  {i}. {obj['object_type']} at ({pos['x']:.1f}, {pos['z']:.1f})")

        metrics = coordinator.get_metrics()
        print(f"\nPERFORMANCE")
        print(f"  Physical actions: {metrics['total_actions']}")
        print(f"  Communications: {metrics['total_communications']}")

        if metrics['total_actions'] > 0:
            reduction = ((95 - metrics['total_actions']) / 95) * 100
            print(f"  Improvement: {reduction:.1f}% vs traditional")

        controller.stop()
        print("\nComplete!")
        return 0

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
