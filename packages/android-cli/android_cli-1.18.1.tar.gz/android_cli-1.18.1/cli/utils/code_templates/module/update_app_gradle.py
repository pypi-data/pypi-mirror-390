def update_app_gradle(module_name):
    lines = []

    with open("build.gradle.kts", "r") as file:
        feature_import = 'implementation(project(":feature:'
        feature_import_seen = False
        new_line_added = False
        for line in file:
            if (not new_line_added and feature_import_seen and feature_import not in line):
                lines.append(f'    implementation(project(":feature:{module_name}"))\n')
                new_line_added = True
            if (feature_import in line):
                feature_import_seen = True
            lines.append(line)

    with open("build.gradle.kts", "w") as file:
        file.writelines(lines)
