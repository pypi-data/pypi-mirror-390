import os
import re


def extract_version_code():
    current_dir = os.getcwd()
    file = f"{current_dir}/buildSrc/src/main/kotlin/android-config.gradle.kts"
    try:
        with open(file, 'r') as file:
            content = file.read()
            patron_version_code = r"versionCode\s*=\s*(\d+)"
            version_code_match = re.search(patron_version_code, content)
            version_code = version_code_match.group(1) if version_code_match else False

            return version_code
    except FileNotFoundError:
        return False
    except IOError as e:
        return False


def get_version_code_form():
    return extract_version_code()
