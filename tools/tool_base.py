import os

class ToolBase:
    def __init__(self):
        pass

    def show_settings(self):
        pass

    def get_intro(self):
        script_name, script_extension = os.path.splitext(__file__)
        with open(f'{script_name}.md', 'r', encoding='utf-8') as file:
            markdown_content = file.read()
        return markdown_content

    def show_ui(self):
        pass
    
    def run(self):
        pass