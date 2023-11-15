

class Role:

    def __init__(self, name='user'):
        self.name = name

    def message(self, content):
        return {"role": f"{self.name}", "content": content}


Role.user = Role('user')
Role.assistant=Role('assistant')
Role.system = Role('system')


if __name__ == '__main__':
    print(Role.user().message('abc'))