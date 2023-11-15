

class Role:

    def __init__(self, role_name='user'):
        self.role_name = role_name

    def message(self, content):
        return {"role": f"{self.role_name}", "content": content}


Role.user = Role('user')
Role.assistant=Role('assistant')
Role.system = Role('system')


if __name__ == '__main__':
    print(Role.user().message('abc'))