import time
import tracemalloc
from persistent_variables import PersistentVariables as PV
import random

# tracemalloc.start(1)

startTime = time.time()
lastTime = time.time()
lastSnap = None

pvDEBUG = True

gPV = PV('global.json', debug=pvDEBUG)
while True:
    # print('while True')
    gPV.Set('one', random.randint(1, 100))

    lPV = PV('local_{}.json'.format(random.randint(1, 5)), debug=pvDEBUG)
    lPV.Set('local', random.randint(1, 100))
    del lPV

    if time.time() - lastTime > 5:
        lastTime = time.time()
        print('running for', int(time.time()) - int(startTime), 'seconds')

    #     snap = tracemalloc.take_snapshot()
    #     print('\r\n\r\n********************************* SNAP\r\n\r\n')
    #     for stat in snap.statistics('traceback')[:5]:
    #         print(stat)
    # #
    #     if lastSnap:
    #         print('Comp ************\n\n')
    #         comp = snap.compare_to(lastSnap, 'traceback')
    #         for stat in comp[:5]:
    #             print(stat)
    #
    #     lastSnap = snap