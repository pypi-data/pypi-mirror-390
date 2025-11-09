

import questionary

from cli.utils.configs import custom_style


def confirm_question(message='Do you want to confirm?', inverse=False):
    try:
        choices = ['Yes', 'No']
        if inverse is True:
            choices = ['No', 'Yes']
        confirm = questionary.unsafe_prompt([
            {
                'type': 'select',
                'name': 'confirm',
                'message': f'{message}',
                'choices': choices,
                'style': custom_style
            }])

        if confirm['confirm'] == 'Yes':
            return True
        if confirm['confirm'] == 'No':
            return False

    except KeyboardInterrupt:
        return -1
