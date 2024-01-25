import time
from FTMSBLEServer import FTMSBLEServer
import asyncio

s = FTMSBLEServer()
loop = asyncio.get_event_loop()
loop.run_until_complete(s.run(loop))
time.sleep(30)
s.stop_server()
