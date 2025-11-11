from .ui import ask, show_info, show_title, prompt
from rich import print as pprint
from .constants import SETTINGS_PATH
import os, json, time

def onboard():
  info = {}
  show_info("Let's get everything set up for you.", "info")
  pprint("[bold]Question 1:[/bold]")
  answer = ask(message="Do you know what you're doing? (are you a developer?)" ,
      options=[
        "Yes, I am.",
        "No, I'm a vibe coder."
      ])
  info["developer"] = answer == 0
  pprint("\n[bold]Question 2:[/bold]")
  match ask(message="What vibe coding tool do you use?", options=[
    "Claude code",
    "Github copilot",
    "Codex",
    "Other"
  ]):
      case 0:
        info['cli'] = "claude"
      case 1:
        info["cli"] = "copilot"
      case 2:
        info["cli"] = "codex"
      case _:
        pprint("Well, you are cooked 🤣.\nJust kidding. Well, you will have to get into the source code and edit the code to use your tool's cli syntax. Good luck!")
        show_info("Tip: by default, it will use claude's syntax!", 'info')
        info["cli"] = "claude"
  pprint("\n[bold]Question 3:[/bold]")
  show_info("Our app uses playwright to get screenshots from websites during the UI cloning process.")
  answer = prompt(questions=[
    {
      "type": "input",
      "name": "browser_path",
      "message": "What is the browser's executable path? (chromium-based, please!)"
    }
  ])
  info["browser_path"] = answer["browser_path"]
  settings_dir = os.path.dirname(SETTINGS_PATH)
  os.makedirs(settings_dir, exist_ok=True)
  with open(SETTINGS_PATH, "w") as file:
      file.write(json.dumps(info))
  pprint("\n :tada: Done! Enjoy the app.")
  time.sleep(3)
  os.system('cls' if os.name == 'nt' else 'clear')




if __name__ == "__main__":
  onboard()