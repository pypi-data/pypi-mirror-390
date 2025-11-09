import questionary

from cli.utils.configs import custom_style


def ask_for_notification_title():
    try:
        message = f'Notification title: (optional)'
        title = questionary.unsafe_prompt(
            {
                'type': 'text',
                'name': 'value',
                'message': message,
                'style': custom_style
            }
        )
        return title['value']
    except KeyboardInterrupt:
        return -1


