import questionary
from cli.form.lokalise.lokalise_add_strings_form import get_lokalise_add_strings_form
from cli.form.lokalise.lokalise_get_strings_form import get_lokalise_strings_form
from cli.utils.configs import custom_style


def get_lokalise_menu_form():
    try:
        response = questionary.unsafe_prompt(
            {
                'type': 'select',
                'name': 'value',
                'message': 'Lokalise options:',
                'choices': ['Update translations files', 'Add keys to lokalise'],
                'style': custom_style
            }
        )
        if response['value'] == "Update translations files":
            return get_lokalise_strings_form()
        else:
            add_strings_form = get_lokalise_add_strings_form()
            return add_strings_form
    except KeyboardInterrupt:
        return -1
