import asyncio
import sys
import os
import json
import uuid

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from quash_mcp.tools.execute_v3 import execute_v3
from quash_mcp.state import get_state
from quash_mcp.models import SessionDTO, ConfigInfo, UIStateInfo


async def main():
    # Initialize the session state
    state = get_state()
    state.config["api_key"] = "mhg__Sacdd_AiKSJgTow49F8p9Fu-UGyi_Wd"
    state.device_serial = "emulator-5554"
    state.portal_ready = True  # Assume portal is ready for local testing

    # --- CONFIGURATION ---
    state.config["model"] = "anthropic/claude-sonnet-4"
    state.config["temperature"] = 0.2
    state.config["vision"] = False
    state.config["reasoning"] = True
    state.config["reflection"] = True
    state.config["debug"] = False
    state.config["max_steps"] = 10
    # ---------------------

    # Define the task
    # task = "Open the google search app and search for bakeries."
    # task = "Open settings."
    # task = "Open Markor app, replace the contents of 'Abhinav.txt' to Hello World! and save the file as Done.md"
    # task = "Tell me all the number drawn on the screen"
    task = "Create a file with name test.md and write Hello World! and save it in markor app"
    # task = "Tell me what you see drawn on screen"

    # Define a progress callback
    def progress_callback(message):
        print(message)

    # Create the initial session DTO
    session = SessionDTO(
        session_id=f"session_{uuid.uuid4().hex[:24]}",
        api_key=state.config["api_key"],
        task=task,
        device_serial=state.device_serial,
        config=ConfigInfo(**{k: v for k, v in state.config.items() if k in ConfigInfo.model_fields})
    )

    # Print the initial session DTO
    print("--- Initial Session DTO ---")
    print(session.model_dump_json(indent=2))
    print("---------------------------")

    # Run the execute_v3 function
    try:
        result = await execute_v3(task=task, progress_callback=progress_callback)
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())