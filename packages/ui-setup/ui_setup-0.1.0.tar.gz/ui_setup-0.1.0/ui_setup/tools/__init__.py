from ..constants import SETTINGS_PATH
import json
import subprocess
import tempfile
import os

def load_settings():
    try:
      with open(SETTINGS_PATH, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError("Settings file not found. Please run the setup process.")
    except json.JSONDecodeError:
        raise ValueError("Error decoding JSON from settings file. Maybe you changed it manually?")

def call_agent(question:str, screenshot:str|None=None, model:str="claude-sonnet-4.5", continue_latest_chat:bool=False):
    settings = load_settings()
    command = [settings.get('cli')]
    match settings['cli']:
        case "codex":
            command.extend(["exec", "--full-auto"])
            if screenshot:
                command.extend(["-i", screenshot])
            if continue_latest_chat:
                command.extend(["resume", "--last"])
        case "copilot":
            if screenshot:
                question += f"\n\nScreenshot: @{screenshot}"
            command.extend(["-p", question, "--allow-all-tools"])
            if continue_latest_chat:
                command.append("--continue")
        case "claude":
            command.extend(["-p", "--allowedTools", "Bash,Read", "--permission-mode", "acceptEdits"])
            if screenshot:
                question += f"\n\nScreenshot: @{screenshot}"
            if continue_latest_chat:
                command.append("--continue")
    if settings['cli'] != "copilot":
        command.append(question)
    print(command)
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = process.communicate()
    if process.returncode != 0:
        raise RuntimeError(f"Agent command failed: {error.decode().strip()}")
    return output.decode().strip()

