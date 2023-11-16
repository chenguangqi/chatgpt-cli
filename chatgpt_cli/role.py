
class Role:
    user = None
    assistant = None
    system = None

    def __init__(self, name='user'):
        self.name = name

    def message(self, content):
        return {"role": f"{self.name}", "content": content}


Role.user = Role('user')
Role.assistant = Role('assistant')
Role.system = Role('system')
