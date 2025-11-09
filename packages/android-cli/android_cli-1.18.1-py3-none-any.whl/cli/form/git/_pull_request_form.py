import re
import questionary

from cli.entities.git import Git
from cli.form._form_confirm import confirm_question
from cli.utils.editor import get_multiline_input
from cli.utils.ui import UI


def valid_jira_task(value):
    if not value:
        return True

    pattern = r'^(NPR|BUG|PR)-[1-9]\d{0,4}$'
    return bool(re.match(pattern, value))


def get_jira_key(branch):
    regex = r'/([A-Za-z]+-\d+)/'

    matches = re.search(regex, branch)

    if matches:
        return matches.group(1)
    else:
        return None


def form_pull_request():
    result = None

    try:
        jira_key = get_jira_key(Git().get_current_branch())
        form_task = questionary.unsafe_prompt(
            {
                'type': 'text',
                'name': 'task',
                'message': 'JIRA Task?',
                'default': f"{jira_key}",
                'validate': lambda val: 'Invalid format. Ej. PR-123 or PR-123, PR-321' if not valid_jira_task(
                    val) else True
            }
        )
    except KeyboardInterrupt:
        return -1

    try:
        form_title = questionary.unsafe_prompt(
            {
                'type': 'text',
                'name': 'title',
                'message': 'Title?',
                'default': f'[{jira_key}] ',
            }
        )
    except KeyboardInterrupt:
        return -1

    try:
        default_description = ''
        if default_description == '':
            add_description = confirm_question('Add description?')
        else:
            UI().ptext(f"<gray>?</gray> <bold>Description:</bold>")
            for line in default_description.split("\n"):
                UI().ptext(f"<y>{line}</y>")
            add_description = confirm_question('Edit description?')

        if add_description:
            form_description = get_multiline_input(default_description)
            form_description = '\n'.join([line for line in form_description.split('\n') if line.strip() != ''])
            if form_description != '':
                form_description = f"{form_description}"
            else:
                form_description = ''
        else:
            form_description = default_description

    except KeyboardInterrupt:
        return -1

    try:
        form_notes = questionary.unsafe_prompt(
            {
                'type': 'text',
                'name': 'notes',
                'message': 'Notes (optional)?',
            }
        )
    except KeyboardInterrupt:
        return -1

    result_title = form_title['title']
    result_details = f"## {form_title['title']}"
    if form_task['task']:
        PRs = form_task['task'].replace(' ', '').split(",")

        if len(PRs) > 1:
            result_details += f"\n\n**JIRA TASKs**:"
            for _PR in PRs:
                __PR = _PR.replace('#', '')
                result_details += f" [{_PR}](https://astropayglobal.atlassian.net/browse/{__PR})"
        else:
            __PR = form_task['task'].replace('#', '')
            result_details += f"\n\n**JIRA TASK**: [{form_task['task']}](https://astropayglobal.atlassian.net/browse/{__PR})"

    if form_description:
        _description_title = f"\n\n### Description: \n"
        _description = ''
        for line in form_description.split("\\n"):
            if line.startswith("Closes:") or line.startswith("Fixes:"):
                continue
            _description += f"\n{line}"

        if _description:
            result_details += "\n\n---" + _description_title + _description

    if form_notes['notes']:
        _notes_title = f"\n\n### Notes: \n"
        _notes = ''
        for line in form_notes['notes'].split("\\n"):
            _notes += f"\n{line}"

        if _notes:
            result_details += "\n\n---" + _notes_title + _notes

    print('')
    UI().pline()
    UI().ptext(f"<gray>Title: </gray> <y>{form_title['title']}</y>")
    UI().ptext("<gray>Details:</gray>")
    print(result_details)
    UI().pline()

    result = {
        'title': result_title,
        'details': result_details,
        'task': form_task['task'] if form_task['task'] else '0',
        'jira_key': get_jira_key(Git().get_current_branch())
    }
    return result
