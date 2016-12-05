class SettingsStorage(dict):
    '''
    Store your settings with access through the point
    Настройки с доступом через точку
    '''

    def __init__(self):
        super().__init__()
        self.path = r'/'

    def __setattr__(self, key, value):
        self[key] = value

    def __getattr__(self, key):
        return self[key]

    def load(self, settings_path):
        self.path = settings_path

        with open(self.path, 'r') as f:
            self.update(eval(f.read()))


settings = SettingsStorage()
