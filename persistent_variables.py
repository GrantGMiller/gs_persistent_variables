try:
    from extronlib.system import File, Wait
except Exception as e:
    print(e)
    File = open

import json

DEBUG = True

oldPrint = print

if DEBUG is False:
    print = lambda *a, **k: None


class PersistentVariables:
    '''
    This class is used to easily manage non-volatile variables using the extronlib.system.File class
    '''

    def __init__(self, filename=None, fileClass=None, fileMode=None):
        '''

        :param filename: string like 'data.json' that will be used as the file name for the File class
        '''
        if fileClass is None:
            self._fileClass = File  # use extronlib.system.File

        else:
            self._fileClass = fileClass  # use something else, like aes_tools.File

        if fileMode is None:
            self._fileMode = 't'
        else:
            self._fileMode = fileMode

        if filename is None:
            filename = 'persistent_variables.json'
        self.filename = filename

        self._valueChangesCallback = None

        self._CreateFileIfMissing()
        self._data = self._GetDataFromFile()
        self._waitSave = Wait(1, self.DoSave)
        self._waitSave.Cancel()

    def _GetDataFromFile(self):
        with self._fileClass(self.filename, mode='r' + self._fileMode) as file:
            print('78 file=', file)

            try:
                if self._fileMode == 'b':
                    b = file.read()
                    print('82 b=', b)
                    data = json.loads(b.decode(encoding='iso-8859-1'))
                else:
                    data = json.loads(file.read())

            except Exception as e:
                # probably the encryption key changed
                # oldPrint('pv Exception:', e)
                data = {}

            file.close()

        return data

    def _CreateFileIfMissing(self):
        if not self._fileClass.Exists(self.filename):
            print('If the file doesnt exist yet, create a blank file')
            with self._fileClass(self.filename, mode='w' + self._fileMode) as file:
                if self._fileMode == 'b':
                    file.write(json.dumps({}).encode(encoding='iso-8859-1'))
                else:
                    file.write(json.dumps({}))
                file.close()

    def Set(self, varName, newValue):
        '''
        This will save the variable to non-volatile memory with the name varName
        :param varName: str that will be used to identify this variable in the future with .Get()
        :param newValue: any value hashable by the json library
        :return:
        '''
        print('Set(', varName, newValue)
        if not isinstance(varName, str):
            # json requires keys to be str
            varName = str(varName)

        # get the old value
        oldValue = self._data.get(varName, None)

        # if the value is different do the callback
        if oldValue != newValue:
            if callable(self._valueChangesCallback):
                self._valueChangesCallback(varName, newValue)

        # Add/update the new value
        self._data[varName] = newValue

        self.Save()

    @property
    def Data(self):
        return self._data

    def Save(self):
        print('Save()')
        self._waitSave.Restart()

    def DoSave(self):
        print('DoSave()')
        with self._fileClass(self.filename, mode='w' + self._fileMode) as file:
            if self._fileMode == 'b':
                file.write(json.dumps(self._data, indent=2, sort_keys=True).encode(encoding='iso-8859-1'))
            else:
                file.write(json.dumps(self._data, indent=2, sort_keys=True))
            file.close()

    def Get(self, varName=None, default=None):
        '''
        This will return the value of the variable with varName. Or None if no value is found
        :param varName: name of the variable that was used with .Set()
        param default: returned if the varName is not found
        :return:
        '''

        if varName is None and default is None:
            return self._data.copy()

        # Grab the value and return it
        try:
            varValue = self._data[varName]
        except KeyError:
            varValue = default
            self.Set(varName, varValue)

        return varValue

    def Delete(self, varName):
        # If the varName does not exist, return None
        val = self._data.pop(varName, None)
        self.Save()
        return val

    @property
    def ValueChanges(self):
        return self._valueChangesCallback

    @ValueChanges.setter
    def ValueChanges(self, callback):
        self._valueChangesCallback = callback

    def __str__(self):
        return '<PersistentVariables, filename={}>'.format(self.filename)


if __name__ == '__main__':
    pv = PersistentVariables('test.json')
    for i in range(10):
        pv.Set(i, i)
    print('end test')
