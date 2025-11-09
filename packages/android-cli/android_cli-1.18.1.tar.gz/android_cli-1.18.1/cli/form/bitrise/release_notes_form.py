import questionary


def get_release_notes_form():
    try:
        release_notes = questionary.unsafe_prompt(
            {
                'type': 'text',
                'name': 'value',
                'message': 'Write the release notes, separated by commas:',
                'default': '',
                'validate': lambda val: 'You should add one release note at least' if not validate_release_note(
                    val) else True
            }
        )
        return release_notes['value'].replace(',', '\n')
    except KeyboardInterrupt:
        return -1


def validate_release_note(value):
    if value:
        return True
    else:
        return False
