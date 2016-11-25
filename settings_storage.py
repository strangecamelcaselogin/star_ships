class SettingsStorage(dict):
    '''
    Store your settings with access through the point
    Настройки с доступом через точку
    '''
    def __init__(self):
        self.path = r'/'

    def __setattr__(self, key, value):
        self[key] = value

    def __getattr__(self, key):
        try:
            return self[key]

        except KeyError as e:
            print(e)

    def load(self, settings_path):
        self.path = settings_path

        try:
            f = open(self.path, 'r')
            self.update(eval(f.read()))

        except Exception as e:
            print(e)

        finally:
            f.close()

    def save(self):
        f = open(self.path, 'w')
        f.write(repr(self.__dict__))
        f.close()

settings = SettingsStorage()
