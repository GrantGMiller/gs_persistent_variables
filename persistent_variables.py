from extronlib.system import File

class PersistentVariables():
    '''
    This class is used to easily manage non-volatile variables using the extronlib.system.File class
    '''

    def __init__(self, filename=None):
        '''

        :param filename: string like 'data.json' that will be used as the file name for the File class
        '''
        if filename is None:
            filename = 'persistent_variables.json'
        self.filename = filename

        self._valueChangesCallback = None

        self._CreateFileIfMissing()

    def _CreateFileIfMissing(self):
        if not File.Exists(self.filename):
            # If the file doesnt exist yet, create a blank file
            with File(self.filename, mode='wt') as file:
                file.write(json.dumps({}))
                file.close()

    def Set(self, varName, newValue):
        '''
        This will save the variable to non-volatile memory with the name varName
        :param varName: str that will be used to identify this variable in the future with .Get()
        :param newValue: any value hashable by the json library
        :return:
        '''
        self._CreateFileIfMissing()

        # load the current file
        with File(self.filename, mode='rt') as file:
            data = json.loads(file.read())
            file.close()

        #get the old value
        oldValue = data.get(varName, None)

        #if the value is different do the callback
        if oldValue != newValue:
            if callable(self._valueChangesCallback):
                self._valueChangesCallback(varName, newValue)

        # Add/update the new value
        data[varName] = newValue

        # Write new file
        with File(self.filename, mode='wt') as file:
            file.write(json.dumps(data, indent=4))
            file.close()

    def Get(self, varName):
        '''
        This will return the value of the variable with varName. Or None if no value is found
        :param varName: name of the variable that was used with .Set()
        :return:
        '''
        self._CreateFileIfMissing()
        # If the varName does not exist, return None

        # load the current file
        with File(self.filename, mode='rt') as file:
            data = json.loads(file.read())
            file.close()

        # Grab the value and return it
        try:
            varValue = data[varName]
        except KeyError:
            varValue = None
            self.Set(varName, varValue)

        return varValue

    @property
    def ValueChanges(self):
        return self._valueChangesCallback

    @ValueChanges.setter
    def ValueChanges(self, callback):
        self._valueChangesCallback = callback

