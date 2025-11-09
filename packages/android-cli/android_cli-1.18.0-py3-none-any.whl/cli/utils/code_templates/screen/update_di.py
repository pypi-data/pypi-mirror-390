def update_di(di_path, name, package):
    import_line = f"import {package}.{name}ViewModel\n"
    injection_line = f"    viewModelOf(::{name}ViewModel)\n"

    import_lines = []
    module_lines = []
    package_lines = []

    with open(di_path + "/ViewModelsModule.kt", "r") as file:
        for line in file:
            if "package" in line:
                package_lines.append(line)
            elif "import" in line:
                import_lines.append(line)
            elif line.strip() != "":
                module_lines.append(line)

    import_lines.append(import_line)
    import_lines.sort()
    module_lines.insert(-1, injection_line)

    with open(di_path + "/ViewModelsModule.kt", "w") as file:
        file.writelines(package_lines)
        file.write("\n")
        file.writelines(import_lines)
        file.write("\n")
        file.writelines(module_lines)
