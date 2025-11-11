"""
Execute tool V3 - Step-by-step execution with state-change verification.

This reimplements the event-driven state verification from the original Mahoraga agent
using a polling-based approach suitable for the client-server architecture.

All state-change detection logic is contained in this file.
"""

import time
import uuid
import asyncio
import hashlib
import json
from typing import Dict, Any, Callable, Optional, Tuple
from ..state import get_state
from ..backend_client import get_backend_client
from ..device.state_capture import get_device_state
from ..device.adb_tools import AdbTools

import logging
logger = logging.getLogger(__name__)

# Import mahoraga components for tool functions
try:
    from mahoraga.tools import Tools, describe_tools
    from mahoraga.tools.adb import AdbTools as MahoragaAdbTools
    from mahoraga.agent.context.personas import DEFAULT
    from mahoraga.agent.utils.async_utils import async_to_sync
except ImportError as e:
    print(f"Warning: Could not import mahoraga components: {e}")
    Tools = None
    describe_tools = None
    MahoragaAdbTools = None
    DEFAULT = None
    async_to_sync = None


def get_ui_state_hash(ui_state_dict: Dict[str, Any]) -> str:
    """
    Generate a stable hash of the UI state for comparison.

    Uses accessibility tree structure and package name.
    Hash will change when UI updates after an action.
    """
    def normalize_tree(tree):
        """Extract stable elements from UI tree."""
        if isinstance(tree, list):
            normalized = []
            for item in tree:
                if isinstance(item, dict):
                    element = {
                        "className": item.get("className", ""),
                        "text": item.get("text", ""),
                        "resourceId": item.get("resourceId", ""),
                        "bounds": item.get("bounds", ""),
                    }
                    normalized.append(element)

                    children = item.get("children", [])
                    if children:
                        element["children"] = normalize_tree(children)
            return normalized
        return []

    state_repr = {
        "package": ui_state_dict.get("phone_state", {}).get("package", ""),
        "tree": normalize_tree(ui_state_dict.get("a11y_tree", []))
    }

    state_json = json.dumps(state_repr, sort_keys=True)
    return hashlib.sha256(state_json.encode()).hexdigest()


def get_action_timeout(code: str) -> float:
    """
    Determine appropriate timeout based on action type.

    Returns timeout in seconds.
    """
    code_lower = code.lower()

    if "start_app" in code_lower:
        return 10.0  # App launches can be slow
    elif "tap" in code_lower or "click" in code_lower:
        return 5.0   # Screen transitions
    elif "swipe" in code_lower or "scroll" in code_lower:
        return 2.0   # Scroll animations
    elif "drag" in code_lower:
        return 2.0
    elif "input_text" in code_lower:
        return 2.0   # Text input is fast
    elif "press_back" in code_lower or "press_home" in code_lower:
        return 3.0   # Navigation
    elif "press_key" in code_lower:
        return 1.0
    else:
        return 5.0   # Default timeout


def wait_for_state_change(
    get_state_func,
    device_serial: str,
    old_state_hash: str,
    max_wait: float = 10.0,
    poll_interval: float = 0.5,
    min_wait: float = 0.3
) -> Tuple[Dict[str, Any], bytes, bool]:
    """
    Poll device until UI state changes or timeout.

    This is the core polling mechanism that replaces Mahoraga's event-driven approach.

    Returns:
        Tuple of (ui_state_dict, screenshot_bytes, state_changed: bool)
    """
    # Always wait minimum time for action to take effect
    time.sleep(min_wait)

    start_time = time.time()

    while (time.time() - start_time) < max_wait:
        # Capture current state
        ui_state_dict, screenshot_bytes = get_state_func(device_serial)
        current_hash = get_ui_state_hash(ui_state_dict)

        # Check if state changed
        if current_hash != old_state_hash:
            return ui_state_dict, screenshot_bytes, True

        # State hasn't changed - wait and try again
        time.sleep(poll_interval)

    # Timeout - state never changed
    ui_state_dict, screenshot_bytes = get_state_func(device_serial)
    return ui_state_dict, screenshot_bytes, False


def wait_for_action_effect(
    get_state_func,
    device_serial: str,
    old_ui_state: Dict[str, Any],
    executed_code: str,
    min_wait: float = 0.3,
    poll_interval: float = 0.5
) -> Tuple[Dict[str, Any], bytes, bool]:
    """
    Wait for an action to take effect on the device.

    Returns:
        Tuple of (new_ui_state_dict, screenshot_bytes, state_changed: bool)
    """
    # Check if action should change UI
    code_lower = executed_code.lower()
    if "get_state" in code_lower:
        # Action doesn't change UI - no need to wait
        time.sleep(0.1)
        return get_state_func(device_serial)[0], None, False

    # Get hash of old state
    old_hash = get_ui_state_hash(old_ui_state)

    # Determine timeout based on action type
    timeout = get_action_timeout(executed_code)

    # Poll until state changes
    new_ui_state, screenshot, changed = wait_for_state_change(
        get_state_func,
        device_serial,
        old_hash,
        max_wait=timeout,
        poll_interval=poll_interval,
        min_wait=min_wait
    )

    return new_ui_state, screenshot, changed


# ============================================================
# MAIN EXECUTION FUNCTION
# ============================================================

from ..models import SessionDTO, UIStateInfo, ChatHistoryMessage, ConfigInfo, AgentStepDTO

async def execute_v3(
    task: str,
    progress_callback: Optional[Callable[[str], None]] = None
) -> Dict[str, Any]:
    """
    Execute automation task using step-by-step backend communication.
    """
    state = get_state()
    backend = get_backend_client()

    # Check prerequisites
    if not state.is_device_connected():
        return {
            "status": "error",
            "message": "❌ No device connected. Please run 'connect' first.",
            "prerequisite": "connect"
        }

    if not state.is_configured():
        return {
            "status": "error",
            "message": "❌ Configuration incomplete. Please run 'configure' with your Quash API key.",
            "prerequisite": "configure"
        }

    if not state.portal_ready:
        return {
            "status": "error",
            "message": "⚠️ Portal accessibility service not ready. Please ensure it's enabled on the device.",
            "prerequisite": "connect"
        }

    # Get API key and config
    quash_api_key = state.config["api_key"]
    config = {
        "model": state.config["model"],
        "temperature": state.config["temperature"],
        "vision": state.config["vision"],
        "reasoning": state.config["reasoning"],
        "reflection": state.config["reflection"],
        "debug": state.config["debug"]
    }
    max_steps = state.config.get("max_steps", 15)

    # Validate API key
    validation_result = await backend.validate_api_key(quash_api_key)

    if not validation_result.get("valid", False):
        error_msg = validation_result.get("error", "Invalid API key")
        return {
            "status": "error",
            "message": f"❌ API Key validation failed: {error_msg}",
            "prerequisite": "configure"
        }

    # Check credits
    user_info = validation_result.get("user", {})
    organization_credits = validation_result.get("organization_credits", 0)

    if organization_credits <= 0:
        return {
            "status": "error",
            "message": f"❌ Insufficient credits. Current balance: ${organization_credits:.2f}",
            "user": user_info
        }

    # Progress logging helper
    def log_progress(message: str):
        if progress_callback:
            progress_callback(message)

    log_progress(f"✅ API Key validated - Credits: ${organization_credits:.2f}")
    log_progress(f"👤 User: {user_info.get('name', 'Unknown')}")
    log_progress(f"🚀 Starting task: {task}")
    log_progress(f"📱 Device: {state.device_serial}")
    log_progress(f"🧠 Model: {config['model']}")
    log_progress(f"🔢 Max steps: {max_steps}")

    # Initialize Session DTO
    session = SessionDTO(
        session_id=f"session_{uuid.uuid4().hex[:12]}",
        api_key=quash_api_key,
        task=task,
        device_serial=state.device_serial,
        config=ConfigInfo(**config),
        last_action_completed=None  # Explicitly initialize the new field
    )

    # Initialize ADB tools for executing generated code
    # Use the lightweight AdbTools from quash-mcp device module (no mahoraga dependency)
    adb_tools = None
    try:
        adb_tools = AdbTools(
            serial=state.device_serial,
            use_tcp=True,
            remote_tcp_port=8080
        )
        log_progress(f"✅ Initialized AdbTools for code execution")
    except Exception as e:
        log_progress(f"⚠️ CRITICAL: Failed to initialize AdbTools: {e}")
        return {
            "status": "error",
            "message": f"💥 Failed to initialize ADB tools: {e}",
        }

    # Code executor namespace - add tool functions so generated code can call them
    executor_globals = {
        "__builtins__": __builtins__,
    }

    # Add tool functions to executor namespace
    # Use the lightweight tool functions from adb_tools (no mahoraga dependency needed)
    if adb_tools:
        try:
            tool_functions = {
                'tap_by_index': adb_tools.tap_by_index,
                'swipe': adb_tools.swipe,
                'input_text': adb_tools.input_text,
                'press_key': adb_tools.press_key,
                'start_app': adb_tools.start_app,
                'complete': adb_tools.complete,
                'remember': adb_tools.remember,
                'list_packages': adb_tools.list_packages,
                'update_state': adb_tools.update_state,
            }

            # Add each tool function to executor globals with print wrapper
            for tool_name, tool_function in tool_functions.items():
                def make_printing_wrapper(func):
                    """Wrap a tool function to print its return value."""
                    def wrapper(*args, **kwargs):
                        result = func(*args, **kwargs)
                        # Print the result so stdout captures it
                        if result is not None:
                            print(result)
                        return result
                    return wrapper

                # Add wrapped function to globals so code can call it directly
                executor_globals[tool_name] = make_printing_wrapper(tool_function)

            log_progress(f"🔧 Loaded {len(tool_functions)} tool functions: {list(tool_functions.keys())}")
        except Exception as e:
            log_progress(f"⚠️ Warning: Could not load tool functions: {e}")
            import traceback
            log_progress(f"Traceback: {traceback.format_exc()}")

    executor_locals = {}

    start_time = time.time()

    try:
        # ============================================================
        # STEP-BY-STEP EXECUTION LOOP
        # ============================================================

        while len(session.steps) < max_steps:

            log_progress(f"🧠 Step {len(session.steps) + 1}/{max_steps}: Analyzing...")

            # 1. Capture device state and update session DTO
            try:
                ui_state_dict, screenshot_bytes = get_device_state(state.device_serial)

                session.ui_state = UIStateInfo(**ui_state_dict)

                # Update local tools with new state
                if adb_tools and "a11y_tree" in ui_state_dict and isinstance(ui_state_dict["a11y_tree"], list):
                    try:
                        a11y_tree_obj = ui_state_dict["a11y_tree"]
                        adb_tools.update_state(a11y_tree_obj)
                    except Exception as e:
                        log_progress(f"⚠️ Warning: Failed to update adb_tools state: {e}")

                if not config["vision"]:
                    screenshot_bytes = None

                current_package = ui_state_dict.get("phone_state", {}).get("package", "unknown")
                log_progress(f"📱 Current app: {current_package}")

            except Exception as e:
                log_progress(f"⚠️ Warning: Failed to capture device state: {e}")
                session.ui_state = UIStateInfo(
                    a11y_tree=[],
                    phone_state={"package": "unknown"}
                )
                screenshot_bytes = None

            # 2. Send session DTO to backend for AI decision
            step_result = await backend.execute_step(
                session=session,
                screenshot_bytes=screenshot_bytes
            )

            # Handle backend errors
            if "error" in step_result:
                log_progress(f"💥 Backend error: {step_result['message']}")
                return {
                    "status": "error",
                    "message": step_result["message"],
                    "error": step_result["error"],
                    "steps_taken": len(session.steps),
                    "tokens": None,
                    "cost": None,
                    "duration_seconds": time.time() - start_time
                }

            # CRITICAL: Update the client's session DTO with the one returned from the backend
            updated_session_data = step_result.get("updated_session")
            if updated_session_data:
                # Ensure last_action_completed field exists
                if "last_action_completed" not in updated_session_data:
                    updated_session_data["last_action_completed"] = None
                session = SessionDTO(**updated_session_data)
            else:
                # Fallback: if updated_session not returned, update locally
                new_step_data = step_result.get("new_step")
                if new_step_data:
                    new_step = AgentStepDTO(**new_step_data)
                    session.steps.append(new_step)
                assistant_response = step_result.get("assistant_response", "")
                session.chat_history.append(ChatHistoryMessage(role="assistant", content=assistant_response))

            # CRITICAL FIX: Handle plan generation responses (which have new_step=None)
            # These don't create actual steps, just show the plan
            new_step_data = step_result.get("new_step")
            if new_step_data is None and not updated_session_data:
                # Plan was generated but no step was added
                # This is normal - plan is informational only
                pass

            # Get action from backend
            action = step_result.get("action", {})
            action_type = action.get("type")
            code = action.get("code")
            reasoning = action.get("reasoning")

            # Log reasoning
            if reasoning:
                log_progress(f"🤔 Reasoning: {reasoning}")

            # CRITICAL FIX: Reset completion flag before executing
            session.last_action_completed = False

            # 3. Execute action locally (if provided)
            if code and (action_type == "execute_code" or action_type == "complete"):

                log_progress(f"⚡ Executing action...")
                log_progress(f"```python\n{code}\n```")

                old_ui_state = session.ui_state.model_dump().copy()

                try:
                    import io
                    import contextlib

                    stdout = io.StringIO()
                    stderr = io.StringIO()

                    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                        exec(code, executor_globals, executor_locals)

                    execution_output = stdout.getvalue()
                    error_output = stderr.getvalue()

                    # NOTE: Check if complete() was called in the executed code
                    # For now, we rely on the backend to tell us when tasks are complete
                    # via the action type, not through tool properties
                    session.last_action_completed = False

                    log_progress(f"⏳ Waiting for UI state to update...")
                    try:
                        new_ui_state_dict, _, state_changed = wait_for_action_effect(
                            get_device_state,
                            state.device_serial,
                            old_ui_state,
                            code,
                            min_wait=0.3,
                            poll_interval=0.5
                        )

                        if state_changed:
                            old_pkg = old_ui_state.get("phone_state", {}).get("package", "")
                            new_pkg = new_ui_state_dict.get("phone_state", {}).get("package", "")

                            if old_pkg != new_pkg:
                                log_progress(f"✅ State changed: App switched ({old_pkg} → {new_pkg})")
                            else:
                                log_progress(f"✅ State changed: UI updated")
                        else:
                            log_progress(f"⚠️ WARNING: State did NOT change after action (timeout)")
                            log_progress(f"   This might mean the action had no effect or took too long")

                    except Exception as e:
                        log_progress(f"⚠️ Error during state change detection: {e}")
                        state_changed = False
                        time.sleep(1.5)

                    feedback_parts = []

                    if execution_output:
                        feedback_parts.append(f"Action output: {execution_output.strip()}")

                    # CRITICAL FIX: Report completion status in feedback
                    if session.last_action_completed:
                        feedback_parts.append("Sub-task completed successfully (complete() was called)")
                    elif state_changed:
                        feedback_parts.append("UI state updated successfully")
                    else:
                        feedback_parts.append("WARNING: UI state did not change (action may have failed)")

                    if error_output:
                        feedback_parts.append(f"Warnings: {error_output.strip()}")

                    feedback = " | ".join(feedback_parts) if feedback_parts else "Action executed"

                    log_progress(f"✅ {feedback[:200]}")

                    session.chat_history.append(ChatHistoryMessage(
                        role="user",
                        content=f"Execution Result:\n```\n{feedback}\n```"
                    ))

                    time.sleep(0.5)

                except Exception as e:
                    error_msg = f"Error during execution: {str(e)}"
                    log_progress(f"💥 Action failed: {error_msg}")
                    session.last_action_completed = False

                    session.chat_history.append(ChatHistoryMessage(
                        role="user",
                        content=f"Execution Error:\n```\n{error_output.strip()}\n```"
                    ))

            # 4. Check if overall task is complete
            # The backend controls task completion via action.type == "complete"
            action_type = action.get("type", "")

            if action_type == "complete":
                # Backend explicitly says we're done with ALL tasks
                duration = time.time() - start_time
                log_progress(f"✅ Task completed successfully!")

                # Finalize session on backend
                finalize_result = await backend.finalize_session(session=session)
                total_tokens = finalize_result.get("total_tokens", {})
                total_cost = finalize_result.get("total_cost", 0)

                log_progress(f"💰 Usage: {total_tokens.get('total')} tokens, ${total_cost:.4f}")

                return {
                    "status": "success",
                    "steps_taken": len(session.steps),
                    "final_message": "Task completed successfully",
                    "message": f"✅ Success: Task completed",
                    "tokens": total_tokens,
                    "cost": total_cost,
                    "duration_seconds": duration
                }

            elif not code:
                log_progress("⚠️ No action code provided by backend")
                session.chat_history.append(ChatHistoryMessage(
                    role="user",
                    content="No code was provided. Please provide code to execute."
                ))

        # Max steps reached
        log_progress(f"⚠️ Reached maximum steps ({max_steps})")
        duration = time.time() - start_time
        finalize_result = await backend.finalize_session(session=session)

        return {
            "status": "failed",
            "steps_taken": len(session.steps),
            "final_message": f"Reached maximum step limit of {max_steps}",
            "message": "❌ Failed: Maximum steps reached",
            "tokens": finalize_result.get("total_tokens"),
            "cost": finalize_result.get("total_cost"),
            "duration_seconds": duration
        }

    except KeyboardInterrupt:
        log_progress("ℹ️ Task interrupted by user")
        duration = time.time() - start_time
        finalize_result = await backend.finalize_session(session=session)

        return {
            "status": "interrupted",
            "message": "ℹ️ Task execution interrupted",
            "steps_taken": len(session.steps),
            "tokens": finalize_result.get("total_tokens"),
            "cost": finalize_result.get("total_cost"),
            "duration_seconds": duration
        }

    except Exception as e:
        error_msg = str(e)
        log_progress(f"💥 Error: {error_msg}")
        duration = time.time() - start_time
        finalize_result = await backend.finalize_session(session=session)

        return {
            "status": "error",
            "message": f"💥 Execution error: {error_msg}",
            "error": error_msg,
            "steps_taken": len(session.steps),
            "tokens": finalize_result.get("total_tokens"),
            "cost": finalize_result.get("total_cost"),
            "duration_seconds": duration
        }

    finally:
        # Cleanup TCP forwarding
        if adb_tools:
            try:
                adb_tools.teardown_tcp_forward()
            except Exception as e:
                logger.warning(f"Failed to cleanup TCP forwarding: {e}")