import questionary
import re

from cli.entities.setting import Settings
from cli.utils.configs import custom_style


def valid_pr_branch(value):

    if not value:
        return True

    pattern = r'^[a-zA-Z0-9]+-[0-9]+(?:_[a-zA-Z0-9]+-[0-9]+)*$'
    return bool(re.match(pattern, value))


def valid_branch_description(s):
    # Validar longitud
    if len(s) < 3 or len(s) > 60:
        return "Must be at least 3 characters long and less than 20 characters long."

    # Validar espacios en blanco
    if " " in s:
        return "Must not contain spaces."

    # Validar que no empiece ni termine con '-'
    if s.startswith('-') or s.endswith('-'):
        return "Must not start or end with '-'."

    # Validar que solo tenga '-' como caracter especial
    if not re.match("^[a-zA-Z0-9-]*$", s):
        return "Must only contain alphanumeric characters and '-'."

    # Validar que no tenga dos '-' seguidos
    if "--" in s:
        return "Must not contain two consecutive '-'."

    # Validar que solo permita lowercase a
    if not re.match("^[a-z-]*$", s):
        return "Must only contain lowercase characters."

    return True


def form_new_branch_from_release_branch():
    try:
        type_choices = Settings().config['branch_setting']['types']
        type_filtered_choices = [
            choice for choice in type_choices if choice['enabled']]
        branch_type = questionary.unsafe_prompt(
            {
                'type': 'select',
                'name': 'type',
                'message': 'Branch Type?',
                'choices': type_filtered_choices,
                'style': custom_style
            }
        )
    except KeyboardInterrupt:
        return -1

    try:
        default_issue = ''
        if branch_type['type'] == 'feature':
            default_issue = 'PR-'
        elif branch_type['type'] == 'fix':
            default_issue = 'BUG-'

        branch_issue_task = questionary.unsafe_prompt(
            {
                'type': 'text',
                'name': 'issue-task',
                'message': 'Issues Task e.g. PR-123?',
                'default': default_issue,
                'validate': lambda val: 'Invalid format. Ej. NPR-1/PR-1/PR-1_PR-2...' if not valid_pr_branch(val) else True,
                'style': custom_style
            },
        )
    except KeyboardInterrupt:
        return -1

    try:
        branch_description = questionary.unsafe_prompt(
            {
                'type': 'text',
                'name': 'description',
                'message': 'Branch description?',
                'validate': valid_branch_description
            },
        )
    except KeyboardInterrupt:
        return -1

    _branchType = branch_type['type']
    _branchIssueTask = ''
    if branch_issue_task['issue-task']:
        _branchIssueTask = f"/{branch_issue_task['issue-task']}"

    _branchDescription = f"/{branch_description['description']}"

    commit_message = f"{_branchType}{_branchIssueTask}{_branchDescription}"
    return commit_message
