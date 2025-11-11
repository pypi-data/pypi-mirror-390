import rich
from typing import Literal
from PyInquirer import prompt

def show_title():
    title = """
    ██╗   ██╗██╗    ███████╗███████╗████████╗██╗   ██╗██████╗
    ██║   ██║██║    ██╔════╝██╔════╝╚══██╔══╝██║   ██║██╔══██╗
    ██║   ██║██║    ███████╗█████╗     ██║   ██║   ██║██████╔╝
    ██║   ██║██║    ╚════██║██╔══╝     ██║   ██║   ██║██╔═══╝
    ╚██████╔╝██║    ███████║███████╗   ██║   ╚██████╔╝██║
    ╚═════╝ ╚═╝    ╚══════╝╚══════╝   ╚═╝    ╚═════╝ ╚═╝
    """

    rich.print(f'[green]{title}[/green]')

def ask(options: list[str], message: str = "Please choose an option:") -> int:
    questions = [
        {
            'type': 'list',
            'name': 'option',
            'message': message,
            'choices': options
        }
    ]

    answers = prompt(questions)
    selected_option = answers['option']

    return options.index(selected_option)

def show_info(message: str, type:Literal['success', 'info', 'warning', 'error'] = 'info'):
    types = {
        'success': {'color':'green', 'emoji':'✅'},
        'info': {'color':'blue', 'emoji':'❕'},
        'warning': {'color':'yellow', 'emoji':'⚠️'},
        'error': {'color':'red', 'emoji':'❌'}
    }
    color = types.get(type, {'color':'blue', 'emoji':'❕'})['color']
    emoji = types.get(type, {'color':'blue', 'emoji':'❕'})['emoji']
    rich.print(f'[{color}]{emoji} {message}[/{color}]')

def prompt_string(string: str) -> str:
    question = [
        {
            "type": "input",
            "name": "response",
            "message": string
        }
    ]
    answer = prompt(question)
    return answer["response"]

def confirm_prompt(message: str) -> bool:
    question = [
        {
            "type": "confirm",
            "name": "confirmation",
            "message": message,
            "default": True
        }
    ]
    answer = prompt(question)
    return answer["confirmation"]


if __name__ == "__main__":
    show_title()
    options = ["Start New Project", "Load Existing Project", "Exit"]
    choice = ask(options)
    rich.print(f"You selected option {choice + 1}: {options[choice]}")
    show_info("This is an informational message.", "info")
    show_info("This is a success message.", "success")
    show_info("This is a warning message.", "warning")
    show_info("This is an error message.", "error")