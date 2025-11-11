SYSTEM_PROMPT_CLONE = """
Help me rebuild that exact same UI in a single html file as website.html. I will provide you with a CSS file at @{} and a screenshot. You will clone the website on the screenshot, not create a similar one with the folder's context. Clone all the texts and elements from the screenshot's page, and recreate it pixel-perfect. Ensure you use the exact same colors and fonts as the original website. Remember: your function is to CLONE THAT UI, NOT CREATE A NEW ONE IN THE SAME STYLE. Copy all the texts, buttons, position and etc. both your html file and the screenshot should look the exact same.
"""

SYSTEM_PROMPT_CREATE_STYLE_MD = """
Great, now help me generate a detailed style guide, based on the html file you just wrote. Then, create a file called style.md, where you will document the style system used in the project. Analyze the html file and extract all relevant style information to create a comprehensive style guide for the project.

In style guide, you must include the following part:
- Overview

- Color pallette

- Typography (Pay attention to font weight, font size and how different fonts have been used
together in the project)

- Spacing System

In style guide, you must include the following part:
- Overview

- Color pallette

- Typography (Pay attention to font weight, font size and how different fonts have been used
together in the project)

- Spacing System

- Component Styles

- Shadows & Elevation

- Animations & Transitions

- Border Radius

- Opacity & Transparency

- Common Tailwind CSS Usage in Project

— Example component reference design code

- And so on...

In a word, Give detailed analysis and descriptions to the project style system, and don't miss any
important details.
"""