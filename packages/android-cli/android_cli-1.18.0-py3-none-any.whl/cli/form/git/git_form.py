import questionary
from prompt_toolkit.styles import Style

from cli.utils.configs import custom_style


def get_git_menu_form():
    try:
        type_choices = [
            'Create BRANCH ',
            'Create PR'
        ]

        result = questionary.unsafe_prompt(
            {
                'type': 'select',
                'name': 'value',
                'message': 'What do you want to do?',
                'choices': type_choices,
                'style': custom_style
            }
        )

        if result['value'] == type_choices[0]:
            return "BRANCH"
        else:
            return "PR"
    except KeyboardInterrupt:
        return -1
