from persistent_variables import PersistentVariables
import aes_tools

aes_tools.File.DeleteFile('persistent_variables.json')

pv = PersistentVariables(fileClass=aes_tools.File, fileMode='b')

pv.Set('key', 'value')
print('pv.Get("key")=', pv.Get('key'))