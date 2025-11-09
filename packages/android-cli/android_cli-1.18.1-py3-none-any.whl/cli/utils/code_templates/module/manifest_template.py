def create_manifest():
    file_name = "AndroidManifest.xml"
    file_content = f'''<?xml version="1.0" encoding="utf-8"?>
<manifest>

</manifest>'''
    with open(file_name, "w") as file:
        file.write(file_content)

