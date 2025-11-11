from .constants import SYSTEM_PROMPT_CLONE, SYSTEM_PROMPT_CREATE_STYLE_MD
from .tools import get_website_css, get_website_screenshot
from ...ui import ask, prompt_string, show_info,  confirm_prompt
from rich import print as pprint
from ...tools import load_settings, call_agent
import os
import webbrowser
import tempfile

def clone_ui():
  settings = load_settings()
  url = prompt_string("What is the url of the website you want to clone the UI from? ")
  pprint("Good choice! Now, let us work.")
  show_info("Fetching CSS data from the website...")
  css = get_website_css(url)
  show_info("Getting a screenshot from the website...")
  path = get_website_screenshot(url)
  show_info("Done! Now, cloning it with your AI tool.", 'success')

  css_file = tempfile.NamedTemporaryFile(mode='w', suffix='.css', delete=False)
  css_file.write(css)
  css_file.close()

  additional_instructions = ""
  if settings['developer']:
    additional_instructions = "\n\n" + prompt_string("Add here additional instructions we should give to the LLM, such as specific stack to use, best practices etc. (Optional)")
  show_info("Calling the agent to clone the UI... This might take several minutes.", 'info')
  final_prompt = SYSTEM_PROMPT_CLONE.format(css_file.name) + additional_instructions

  try:
    call_agent(final_prompt, screenshot=path)
  finally:
    try:
      os.unlink(css_file.name)
    except:
      pass

  if not os.path.exists("website.html"):
    show_info("Website.html does not exist. Something went wrong with the agent.", 'error')
  else:
    webbrowser.open("website.html")
  continue_prompt = confirm_prompt("Can we go on, or do you want to refine the page?")
  while continue_prompt != True:
    show_info("Let's refine the page then.", 'success')
    refinement_instructions = prompt_string("What changes do you want to make to the cloned UI?")
    call_agent(refinement_instructions, continue_latest_chat=True)
    webbrowser.open("website.html")
    continue_prompt = confirm_prompt("Does it look good now?")
    if continue_prompt == True:
      show_info("Great! UI cloning process finished.", 'success')
      break
  show_info("Creating style.md file. This might take some minutes.", 'info')
  call_agent(SYSTEM_PROMPT_CREATE_STYLE_MD, continue_latest_chat=True)
  show_info("Done!", 'success')

if __name__ == "__main__":
  clone_ui()