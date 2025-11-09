import questionary

from cli.entities.setting import Settings
from cli.form._form_confirm import confirm_question
from cli.utils.configs import custom_style


def ask_for_firebase_id():
    firebase_id = Settings().config['firebase_id']

    if firebase_id:
        confirm = confirm_question(message=f"Use this firebase id:\n {firebase_id}")
        if confirm:
            return firebase_id
        else:
            return firebase_id_form()
    else:
        return firebase_id_form()


def firebase_id_form():
    try:
        message = f'Firebase id:'
        firebase_id = questionary.unsafe_prompt(
            {
                'type': 'text',
                'name': 'value',
                'message': message,
                'validate': lambda val: 'Firebase id cannot be empty' if not validate_firebase_id(
                    val) else True,
                'style': custom_style
            }
        )
        Settings().config['firebase_id'] = firebase_id['value']
        Settings().save()
        return firebase_id['value']
    except KeyboardInterrupt:
        return -1


def validate_firebase_id(value):
    if value:
        return True
    else:
        return False
