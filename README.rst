Persistent Variables
====================
A module to provide easy persistent storage in Global Scripter.

Examples
========
Initialize the object

::

    from persistent_variables import PersistentVariables as PV

    myFilePath = 'my_file_name.json' # This is where the variables will be loaded/saved.

    pv = PV(myFilePath)
    # If the file exists already, then the current values will be loaded into pv

Saving Values
==============

::

    key = 'My Key'
    value = 'Test Value' # value can be anything json-able

    pv.Set(key, value) # the value is now stored

Retrieving Values
=================

::

    key = 'My Key'
    value = pv.Get(key, None)
    # The second parameter is a default value. If the key is not found, the default value (None in this case) is returned.

    print(value)
    >>> 'Test Value'


