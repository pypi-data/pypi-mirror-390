def update_settings_gradle(module_name):
    include_line = f'include(":feature:{module_name}")\n'

    lines = []

    with open("settings.gradle.kts", "r") as file:
        for line in file:
            lines.append(line)

    lines.append(include_line)

    with open("settings.gradle.kts", "w") as file:
        file.writelines(lines)
