import questionary

from cli.utils.configs import custom_style


def get_code_gen_menu_form():
    try:
        type_choices = [
            'Create Screen', 'Create Module'
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
            return "SCREEN"
        else:
            return "MODULE"
    except KeyboardInterrupt:
        return -1
