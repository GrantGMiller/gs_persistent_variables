from old.persistent_variables import PersistentVariables

#aes_tools.File.DeleteFile('persistent_variables.json')

pv = PersistentVariables()#fileClass=aes_tools.File, fileMode='b')

pv.Set('key', 'value2')
print('pv.Get("key")=', pv.Get('key'))