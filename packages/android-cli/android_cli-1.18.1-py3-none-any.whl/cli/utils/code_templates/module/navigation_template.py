import re

def create_navigation(name):
    file_name = name + "_navigation.xml"
    file_content = f'''<?xml version="1.0" encoding="utf-8"?>
<navigation xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:id="@+id/{name}_nav_graph">

</navigation>

'''
    with open(file_name, "w") as file:
        file.write(file_content)

