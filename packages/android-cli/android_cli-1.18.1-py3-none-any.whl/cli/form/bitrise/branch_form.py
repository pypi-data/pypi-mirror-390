import questionary

from cli.entities.git import Git
from cli.utils.configs import custom_style


def get_branch_form():
    current_branch = Git().get_current_branch()
    branch = False

    if current_branch:
        try:
            choices = ["Yes", "No"]
            message = f"Is {current_branch} the correct branch?"
            response = questionary.unsafe_prompt(
                {
                    'type': 'select',
                    'name': 'value',
                    'message': message,
                    'choices': choices,
                    'style': custom_style
                }
            )
            if response['value'] == "Yes":
                return current_branch
            else:
                remote_branches = Git().get_branches()
                if remote_branches:
                    return get_remote_branch_select_form(remote_branches)
                else:
                    return get_branch_input_form()
        except KeyboardInterrupt:
            return -1
    else:
        remote_branches = Git().get_branches()
        if remote_branches:
            return get_remote_branch_select_form(remote_branches)
        else:
            return get_branch_input_form()


def get_branch_input_form():
    try:
        branch = questionary.unsafe_prompt(
            {
                'type': 'text',
                'name': 'value',
                'message': 'Which branch (develop)?:',
                'default': '',
                'validate': lambda val: 'Branch name cannot be empty' if not validate_branch_name(
                    val) else True
            }
        )
        return branch['value']
    except KeyboardInterrupt:
        return -1


def get_remote_branch_select_form(remote_branches):
    try:
        choices = remote_branches
        branch = questionary.unsafe_prompt(
            {
                'type': 'select',
                'name': 'value',
                'message': "Select the branch:",
                'choices': choices,
                'style': custom_style
            }
        )
        return branch['value']
    except KeyboardInterrupt:
        return -1


def validate_branch_name(value):
    if value:
        return True
    else:
        return False
