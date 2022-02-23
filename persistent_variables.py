from extronlib.system import File, ProgramLog, Timer
import json


class PersistentVariables:
    '''
    This class is used to easily manage non-volatile variables using the extronlib.system.File class
    '''

    def __init__(self, filename=None, fileClass=None, fileMode=None, debug=False):
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

        self.debug = debug

        if filename is None:
            filename = 'persistent_variables.json'
        self.filename = filename

        self._valueChangesCallback = None

        # init
        self._CreateFileIfMissing()
        self._data = self._GetDataFromFile()
        self.print('PV.__init__(', filename, fileClass, fileMode, debug)

        self.shouldSave = False
        self.timer = Timer(10, self.DoSave)

    def print(self, *a, **k):
        if self.debug:
            print(*a, **k)

    def _GetDataFromFile(self):
        self.print('_GetDataFromFile', self)
        try:
            with self._fileClass(self.filename, mode='r' + self._fileMode) as file:
                self.print('78 file=', file)

                if self._fileMode == 'b':
                    b = file.read()
                    self.print('82 b=', b)
                    data = json.loads(b.decode(encoding='iso-8859-1'))
                else:
                    data = json.load(file)

        except Exception as e:
            self.print(e)
            data = {}

        if data:
            return data
        else:
            return {}

    def _CreateFileIfMissing(self):
        self.print('_CreateFileIfMissing', self)
        if not self._fileClass.Exists(self.filename):
            self.print('76 The file doesnt exist yet, create a blank file')
            with self._fileClass(self.filename, mode='w' + self._fileMode) as file:
                if self._fileMode == 'b':
                    file.write(json.dumps({}).encode(encoding='iso-8859-1'))
                else:
                    file.write(json.dumps({}))

    def Set(self, varName, newValue):
        '''
        This will save the variable to non-volatile memory with the name varName
        :param varName: str that will be used to identify this variable in the future with .Get()
        :param newValue: any value hashable by the json library
        :return:
        '''
        self.print('Set(', varName, newValue)
        if not isinstance(varName, str):
            # json requires keys to be str
            varName = str(varName)

        # get the old value
        oldValue = self._data.get(varName, None)

        # Add/update the new value
        self._data[varName] = newValue

        # if the value is different do the callback
        if oldValue != newValue:
            self.DoChangeCallback(varName, newValue)

        self.Save()

    def DoChangeCallback(self, key, value):
        if callable(self._valueChangesCallback):
            self._valueChangesCallback(key, value)

    def Pop(self, key, default=None):
        self.print('Pop(', self, key, default)
        ret = self._data.pop(key, default)
        self.DoChangeCallback(key, ret)
        self.Save()
        return ret

    @property
    def Data(self):
        return self._data

    def Save(self):
        self.shouldSave = True

    def DoSave(self, *a, **k):
        if self.shouldSave:
            self.shouldSave = False
            self.print('DoSave()', self)
            dumpString = json.dumps(self._data, indent=2)
            self.print('len(dumpString)=', len(dumpString), self)
            with self._fileClass(self.filename, mode='w' + self._fileMode) as file:
                if self._fileMode == 'b':
                    file.write(dumpString.encode(encoding='iso-8859-1'))
                else:
                    file.write(dumpString)

    def Get(self, varName=None, default=None):
        '''
        This will return the value of the variable with varName. Or None if no value is found
        :param varName: name of the variable that was used with .Set()
        param default: returned if the varName is not found
        :return:
        '''
        self.print('Get(', varName, default, self)
        if varName is None and default is None:
            return self._data.copy()

        # Grab the value and return it
        try:
            varValue = self._data[varName]
        except KeyError:
            varValue = default
            self.Set(varName, varValue)

        return varValue

    def Append(self, key, item, allowDuplicates=True, maxlen=None):
        self.print('Append(', key, item, allowDuplicates, self)
        assert isinstance(key, str)
        tempList = self.Get(key, [])
        if not tempList:
            tempList = []
        tempList.append(item)

        while maxlen and len(tempList) > maxlen:
            tempList.pop(0)

        if allowDuplicates is False:
            tempList = list(set(tempList))
        self.Set(key, tempList)
        self.DoChangeCallback(key, tempList)
        return tempList

    def Remove(self, key, item):
        self.print('Remove(', key, item, self)
        l = self.Get(key, [])
        if item in l:
            ret = l.remove(item)
            self.Set(key, l)
        else:
            ret = None
        self.DoChangeCallback(key, l)
        return ret

    def SetItem(self, key, subKey, item):
        self.print('SetItem(', key, subKey, item, self)
        d = self.Get(key, {})
        d[subKey] = item
        self.Set(key, d)
        self.DoChangeCallback(key, d)

    def GetItem(self, key, subKey, default=None):
        self.print('GetItem(', key, subKey, default, self)
        d = self.Get(key, {})
        return d.get(subKey, default)

    def PopItem(self, key, subkey, *args):
        self.print('PopItem(', key, subkey, args, self)
        d = self.Get(key, {})

        ret = d.pop(subkey, *args)

        self.Set(key, d)
        self.DoChangeCallback(key, d)
        return ret

    def Delete(self, varName):
        self.print('Delete(', varName, self)
        # If the varName does not exist, return None
        val = self._data.pop(varName, None)
        self.Save()
        self.DoChangeCallback(varName, None)
        return val

    @property
    def ValueChanges(self):
        return self._valueChangesCallback

    @ValueChanges.setter
    def ValueChanges(self, callback):
        self._valueChangesCallback = callback

    def __str__(self):
        return '<PersistentVariables, filename={}>'.format(self.filename)

    def __del__(self):
        self.timer.Stop()
        self.timer.Function()


if __name__ == '__main__':
    pv = PersistentVariables('test.json')
    for i in range(10):
        pv.Set(i, i)
    print('end test')
