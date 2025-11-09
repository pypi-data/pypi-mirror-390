import subprocess
import uuid
import json

from cli.entities.git import Git
from cli.entities.jira import Jira
from cli.entities.setting import Settings
from cli.form._form_confirm import confirm_question
from cli.form.git._pull_request_form import form_pull_request
from cli.utils.shell import Shell
from cli.utils.ui import UI


def create_new_pull_request():
    has_changes = Git().has_changes()
    actual_branch = Git().get_current_branch()
    repository_name = Git().get_repository_name()

    if has_changes is True:
        UI().clear()
        UI().pheader(f"Create new PR", actual_branch)
        UI().perror('You have changes, please commit or stash them')
        return

    # if Settings().isBloquedBranch():
    #     UI().clear()
    #     UI().pheader(f"Create new PR", actual_branch)
    #     UI().perror(f'You cannot create a commit on bloqued branch <y>{actual_branch}</y>')
    #     return

    UI().clear()
    UI().pheader(f"Create new PR", actual_branch)
    UI().pline()
    UI().ptext(f"│  This process will create new <y>PR</y>")
    UI().ptext(f"│  from <y>[{actual_branch}]</y>")
    UI().pline()
    UI().ptext('<g>Pull request:</g>')

    newPR = form_pull_request()
    if newPR == -1:
        return

    confirm = confirm_question()
    if confirm == -1 or confirm is False:
        return

    UI().ptext('\n<g>Pushing Branch</g>')
    Shell().run(['git', 'push', 'origin', Git().get_current_branch()])

    UI().ptext('\n<g>Creating pull request...</g>')
    if Settings().config['use_uuid_token_for_pull_request']:
        client_request_token = str(uuid.uuid4())
    else:
        client_request_token = Git().get_current_branch()

    source_reference = f"{Git().get_current_branch()}"
    title = newPR['title']
    description = newPR['details']
    jira_taks = newPR['task']
    jira_key = newPR['jira_key']
    repository_name = Git().get_repository_name()
    cmd = [
        "aws", "codecommit", "create-pull-request",
        "--region", Settings().config['aws_region'],
        "--profile", Settings().config['aws_profile'],
        "--title", title,
        "--description", description,
        "--client-request-token", client_request_token,
        "--targets", f"repositoryName={repository_name},sourceReference={source_reference}"
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:

        data = json.loads(result.stdout)
        pull_request_id = data['pullRequest']['pullRequestId']
        print('')
        UI().ptext('<g>SUCCESS</g> Pull request created successfully')
        UI().ptext(
            f'<gray>PR URL</gray>: \n<y>https://{Settings().config["aws_region"]}.console.aws.amazon.com/codesuite/codecommit/repositories/{repository_name}/pull-requests/{pull_request_id}/details?region={Settings().config["aws_region"]}</y>')

        Jira().update_pr_field(jira_key,
                               f'https://{Settings().config["aws_region"]}.console.aws.amazon.com/codesuite/codecommit/repositories/{repository_name}/pull-requests/{pull_request_id}/details?region={Settings().config["aws_region"]}')

        PRs = jira_taks.replace(' ', '').split(",")
        if len(PRs) > 1:
            for _PR in PRs:
                __PR = _PR.replace('#', '')
                UI().ptext(f'<gray>JIRA TASK</gray>: \n<y>https://astropayglobal.atlassian.net/browse/{__PR}</y>')
        else:
            _PR = PRs[0].replace('#', '')
            UI().ptext(f'<gray>JIRA TASK</gray>: \n<y>https://astropayglobal.atlassian.net/browse/{_PR}</y>')
        UI().pcontinue()
    else:
        print('')
        UI().ptext('<r>ERROR: create pull request</r>')

        if result.stderr.find('Unable to locate credentials') != -1:
            UI().ptext('- Check your aws credentials')

        if result.stderr.find('IdempotencyParameterMismatchException') != -1:
            UI().ptext('- Maybe you have already created a PR with the same title')

        print(result.stderr)
        UI().pcontinue()
