import questionary

from cli.utils.configs import custom_style


def ask_for_notification_body():
    try:
        message = f'Notification body: (optional)'
        body = questionary.unsafe_prompt(
            {
                'type': 'text',
                'name': 'value',
                'message': message,
                'style': custom_style
            }
        )
        return body['value']
    except KeyboardInterrupt:
        return -1


