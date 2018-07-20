from extronlib.system import File
import json


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

        data = self.Data

        # get the old value
        oldValue = data.get(varName, None)

        # if the value is different do the callback
        if oldValue != newValue:
            if callable(self._valueChangesCallback):
                self._valueChangesCallback(varName, newValue)

        # Add/update the new value
        data[varName] = newValue

        # Write new file
        with File(self.filename, mode='wt') as file:
            file.write(json.dumps(data, indent=4))
            file.close()

    @property
    def Data(self):
        self._CreateFileIfMissing()
        # If the varName does not exist, return None

        # load the current file
        with File(self.filename, mode='rt') as file:
            data = json.loads(file.read())
            file.close()
        return data

    def Save(self, data):
        with File(self.filename, mode='wt') as file:
            file.write(json.dumps(data, indent=2))
            file.close()


    def Get(self, varName=None, default=None):
        '''
        This will return the value of the variable with varName. Or None if no value is found
        :param varName: name of the variable that was used with .Set()
        :return:
        '''
        data = self.Data

        if varName is None and default is None:
            return data.copy()

        # Grab the value and return it
        try:
            varValue = data[varName]
        except KeyError:
            varValue = default
            self.Set(varName, varValue)

        return varValue

    def Delete(self, varName):
        self._CreateFileIfMissing()
        # If the varName does not exist, return None

        # load the current file
        with File(self.filename, mode='rt') as file:
            data = json.loads(file.read())
            file.close()

        data.pop(varName, None)
        self.Save(data)


    @property
    def ValueChanges(self):
        return self._valueChangesCallback

    @ValueChanges.setter
    def ValueChanges(self, callback):
        self._valueChangesCallback = callback
