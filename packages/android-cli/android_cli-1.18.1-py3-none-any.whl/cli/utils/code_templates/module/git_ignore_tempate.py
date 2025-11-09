def create_gitignore():
    file_name = ".gitignore"
    file_content = f'''/build'''
    with open(file_name, "w") as file:
        file.write(file_content)

