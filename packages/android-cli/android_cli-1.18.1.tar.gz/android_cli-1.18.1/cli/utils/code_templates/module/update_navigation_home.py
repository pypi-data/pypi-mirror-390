def update_navigation_home(module_name):
    lines = []

    with open("navigation_home.xml", "r") as file:
        graph_include = '<include app:graph='
        include_seen = False
        new_line_added = False
        for line in file:
            if (not new_line_added and include_seen and graph_include not in line):
                lines.append(f'    <include app:graph="@navigation/{module_name}_navigation" />\n')
                new_line_added = True
            if (graph_include in line):
                include_seen = True
            lines.append(line)

    with open("navigation_home.xml", "w") as file:
        file.writelines(lines)