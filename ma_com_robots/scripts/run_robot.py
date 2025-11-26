#!/usr/bin/env python3
'''Main entry point for robot'''
import sys
sys.path.append('..')

from src.core.robot_controller import RobotController
from config.settings import Config
import os

def main():
    robot = RobotController(
        emissor_path=Config.EMISSOR_DATA_PATH,
        scene="FloorPlan28",
        use_openai=Config.USE_OPENAI,
        api_key=Config.OPENAI_API_KEY
    )

    print("\n" + "="*50)
    print("AI2-THOR OBJECT LOCATOR")
    print("="*50 + "\n")

    robot.run()

if __name__ == "__main__":
    main()
