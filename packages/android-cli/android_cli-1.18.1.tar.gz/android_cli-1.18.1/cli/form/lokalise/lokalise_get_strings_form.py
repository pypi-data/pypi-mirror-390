import questionary
from cli.entities.lokalise import Lokalise
from cli.utils.configs import custom_style


def get_lokalise_strings_form():
    try:
        response = questionary.unsafe_prompt(
            {
                'type': 'select',
                'name': 'value',
                'message': 'Get translations from lokalise?',
                'choices': ['Yes', 'No'],
                'style': custom_style
            }
        )
        if response['value'] == "Yes":
            return Lokalise().generate_translations_files()
        else:
            return -1
    except KeyboardInterrupt:
        return -1
