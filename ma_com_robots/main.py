'''
AI2-THOR Object Locator - Main Entry Point
'''

from src.core.robot_controller import RobotController
from config.settings import Config
import os

def main():
    print("\n" + "="*60)
    print("     AI2-THOR OBJECT LOCATOR - GROUP PROJECT")
    print("="*60 + "\n")

    # Initialize robot
    robot = RobotController(
        emissor_path=Config.EMISSOR_DATA_PATH,
        scene="FloorPlan28",
        use_openai=Config.USE_OPENAI,
        api_key=Config.OPENAI_API_KEY
    )

    try:
        # Run interaction
        robot.run()

    except KeyboardInterrupt:
        print("\n\nInterrupted by user")

    finally:
        # Print summary
        print(f"\n{'='*60}")
        print("INTERACTION SUMMARY")
        print(f"{'='*60}")
        print(f"Physical actions: {robot.action_count}")
        print(f"Dialogue turns: {robot.dialogue_count}")
        print(f"Success: {robot.found_object}")
        print(f"Scenario: {robot.leolani_client._scenario_path}")
        print(f"{'='*60}\n")

if __name__ == "__main__":
    main()
