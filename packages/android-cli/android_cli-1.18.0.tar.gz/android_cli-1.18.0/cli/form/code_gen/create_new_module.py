import os
import re

import questionary

from cli.utils.code_templates.module.build_gradle_template import create_build_gradle
from cli.utils.code_templates.module.consumer_rules_pro_template import create_consumer_rules
from cli.utils.code_templates.module.git_ignore_tempate import create_gitignore
from cli.utils.code_templates.module.manifest_template import create_manifest
from cli.utils.code_templates.module.navigation_template import create_navigation
from cli.utils.code_templates.module.proguard_rules_pro_template import create_proguard_rules
from cli.utils.code_templates.module.update_app_gradle import update_app_gradle
from cli.utils.code_templates.module.update_navigation_home import update_navigation_home
from cli.utils.code_templates.module.update_settings_gradle import update_settings_gradle
from cli.utils.ui import UI


def valid_module_name(value):
    if not value:
        return True

    pattern = r'^[a-zA-Z]+(?:-[a-zA-Z]+)*$'
    return bool(re.match(pattern, value))


def _print_header():
    UI().clear()
    UI().pheader(f"Create new module")
    UI().pline()
    UI().ptext(f"│  Working directory:")
    UI().ptext(f"│  {os.getcwd()}")
    UI().pline()


def _new_module_form():
    new_module = questionary.unsafe_prompt([
        {
            'type': 'input',
            'name': 'name',
            'message': f'Enter module name',
            'validate': lambda val: 'Invalid format. Ej. web-view' if not valid_module_name(val) else True,
        }])["name"]
    src_main_path = os.path.join("feature", new_module, "src", "main")

    namespace_name = new_module.replace("-", "_")

    kotlin_path = os.path.join(src_main_path, "kotlin", "com", "astropaycard", "android", "feature", namespace_name)
    res_navigation_path = os.path.join(src_main_path, "res", "navigation")

    os.makedirs(kotlin_path, exist_ok=True)
    os.makedirs(res_navigation_path, exist_ok=True)

    return new_module, namespace_name


def create_new_module():
    initial_path = os.getcwd()

    UI().clear()
    _print_header()
    new_module, namespace_name = _new_module_form()

    features_path = os.getcwd()
    os.chdir("app")
    update_app_gradle(new_module)
    os.chdir(os.path.join("src", "main", "res", "navigation"))
    update_navigation_home(namespace_name)
    os.chdir(features_path)

    update_settings_gradle(new_module)

    os.chdir(os.path.join("feature", new_module))
    create_gitignore()
    create_build_gradle(namespace_name)
    create_consumer_rules()
    create_proguard_rules()

    os.chdir(os.path.join("src", "main"))
    create_manifest()

    os.chdir(os.path.join("res", "navigation"))
    create_navigation(namespace_name)

    os.chdir(initial_path)

    UI().psuccess()
