import os
import re


def extract_version_name():
    current_dir = os.getcwd()
    file = f"{current_dir}/buildSrc/src/main/kotlin/android-config.gradle.kts"
    try:
        with open(file, 'r') as file:
            content = file.read()
            patron_version_name = r"versionName\s*=\s*\"([^\"]+)\""
            version_name_match = re.search(patron_version_name, content)
            version_name = version_name_match.group(1) if version_name_match else None

            return version_name
    except FileNotFoundError:
        return False
    except IOError as e:
        return False


def get_version_name_form():
    return extract_version_name()
