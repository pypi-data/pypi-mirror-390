import questionary

from cli.utils.configs import custom_style


def ask_for_notification_deeplink():
    try:
        message = f'Notification deeplink:'
        deeplink = questionary.unsafe_prompt(
            {
                'type': 'text',
                'name': 'value',
                'default': 'apcmobile://astrocoins',
                'message': message,
                'style': custom_style
            }
        )
        return deeplink['value']
    except KeyboardInterrupt:
        return -1


