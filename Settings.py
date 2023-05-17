import json
import os


class Settings:
    """
    Basic Settings object.

    Initialize settings:
    settings = Settings(working_directory, logger) - both optional

    Identify settings file:
    settings.file = './resources/settings.json'

    Call to load settings from file (overwrites current settings parameters within object):
    settings.read_settings()

    """
    def __init__(self, working_dir=os.getcwd(), logger=None):
        self.file = None
        self.cwd = working_dir
        self.params = ['file', 'cwd']
        self.logger = logger

        self.pressure_maps_directory = None
        self.pressure_maps = None
        self.default_pressure_map = None
        
    def read_settings(self):
        # Reads and parses settings.json file
        f = open(self.file, 'r')
        settings = json.load(f)
        f.close()
        
        # Creates class attribute for each entry in json object
        for key, value in zip(settings.keys(), settings.values()):
            if key is not None and value is not None:
                setattr(self, key, value)
                self.params.append(key)

        if self.logger is not None:
            self.logger.debug('Settings File Loaded: {}'.format(self.file))

        return settings
    
    def check_settings(self):
        pass
    
    def dump_settings(self):
        # Prints current settings to console for debug
        settings_dict = {}

        for s in self.params:
            settings_dict[s] = self.__getattribute__(s)

            disp_length = 25
            if len(s) < disp_length:
                s_view = ' ' * (disp_length-len(s)) + s + ': '
            else:
                s_view = s[0:disp_length-4] + '... :'
            print(s_view, self.__getattribute__(s))

            if self.logger is not None:
                self.logger.debug(s_view + str(self.__getattribute__(s)))
        return settings_dict
        

if __name__ == '__main__':
    S = Settings(os.getcwd())
    S.file = './resources/settings.json'
    S.read_settings()

    S.dump_settings()
