import questionary

from cli.utils.configs import custom_style


def ask_for_notification_action():
    try:
        message = f'Notification action:'
        body = questionary.unsafe_prompt(
            {
                'type': 'text',
                'name': 'value',
                'default': 'TRUSTED_DEVICE',
                'message': message,
                'style': custom_style
            }
        )
        return body['value']
    except KeyboardInterrupt:
        return -1


