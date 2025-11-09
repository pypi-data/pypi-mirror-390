from cli.entities.git import Git
from cli.entities.setting import Settings
from cli.form._form_confirm import confirm_question
from cli.form.git._new_branch_form import form_new_branch_from_release_branch
from cli.utils.shell import Shell
from cli.utils.ui import UI


def create_new_branch_from_release_branch():
    settings = Settings().config
    has_changes = Git().has_changes()
    release_branch = settings['branch_setting']['release_branch']
    current_branch = Git().get_current_branch()

    UI().clear()
    UI().pheader(f"Create branch from [{release_branch}]")
    UI().pline()
    UI().ptext(f"│  This process will create new <y>branch</y> ")
    UI().ptext(f"│  from <y>[{release_branch}]</y>")
    if has_changes is True:
        UI().ptext('│  <y>WARNING:</y> You have changes')
    UI().pline()

    UI().ptext('<g>New Branch</g>')
    branch_name = form_new_branch_from_release_branch()
    if branch_name == -1:
        return

    UI().pline()
    if release_branch != current_branch:
        UI().ptext(f"<gray>run</gray> git checkout <y>{release_branch}</y>")

    UI().ptext(f"<gray>run</gray> git pull origin <y>{release_branch}</y>")
    UI().ptext(f"<gray>run</gray> git checkout -b <y>{branch_name}</y>")

    UI().pline()
    confirm = confirm_question()
    if confirm == -1 or confirm is False:
        return
    else:
        UI().pline()
        if release_branch != current_branch:
            UI().ptext(f'<g>running</g> <gray>git checkout {release_branch}</gray>')
            run_checkout = Shell().run(['git', 'checkout', release_branch])
            if run_checkout != 0:
                UI().perror('Error on git checkout')
                return

        UI().ptext(f'<g>running</g> <gray>git pull origin {release_branch}</gray>')
        run_pull = Shell().run(['git', 'pull', 'origin', release_branch])
        if run_pull != 0:
            UI().perror('Error on git pull')
            return

        UI().ptext(f'<g>running</g> <gray>git checkout -b {branch_name}</gray>')
        run_pull = Shell().run(['git', 'checkout', '-b', branch_name])
        if run_pull != 0:
            UI().perror('Error on git pull')
            return

        UI().psuccess('Branch created successfully')
