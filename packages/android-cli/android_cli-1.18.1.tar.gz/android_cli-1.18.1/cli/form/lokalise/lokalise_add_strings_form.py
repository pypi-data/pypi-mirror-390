import questionary
from cli.entities.lokalise import Lokalise
from cli.utils.configs import custom_style


def get_lokalise_add_strings_form():
    try:
        response = questionary.unsafe_prompt(
            {
                'type': 'select',
                'name': 'value',
                'message': 'Do you want add the keys in strings_aux.xml to lokalise?',
                'choices': ['Yes', 'No'],
                'style': custom_style
            }
        )
        if response['value'] == "Yes":
            return Lokalise().create_keys()
        else:
            return -1
    except KeyboardInterrupt:
        return -1
