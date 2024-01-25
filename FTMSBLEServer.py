import logging
import threading
from typing import Any, Dict
from bless import (  # type: ignore
        BlessServer,
        BlessGATTCharacteristic,
        GATTCharacteristicProperties,
        GATTAttributePermissions
        )


class FTMSBLEServer:
    my_service_name = "FTMSBLE Test Service"
    gatt: Dict = {
            "A07498CA-AD5B-474E-940D-16F1FBE7E8CD": {
                "51FF12BB-3ED8-46E5-B4F9-D64E2FEC021B": {
                    "Properties": (GATTCharacteristicProperties.read |
                                   GATTCharacteristicProperties.write |
                                #    GATTCharacteristicProperties.notify |
                                   GATTCharacteristicProperties.indicate),
                    "Permissions": (GATTAttributePermissions.readable |
                                    GATTAttributePermissions.writeable),
                    "Value": None
                }
            }
        }
    def __init__(self):
        logging.basicConfig(level=logging.DEBUG)
        self.logger = logging.getLogger(name=self.__class__.__name__)
        self.exit_trigger: threading.Event = threading.Event()


    async def run(self,loop):
        self.exit_trigger.clear()
        self.server = BlessServer(name=self.my_service_name, loop=loop)
        self.server.read_request_func = self.read_request
        self.server.write_request_func = self.write_request
        await self.server.add_gatt(self.gatt)
        await self.server.start()
        self.logger.debug("Advertising")
        self.exit_trigger.wait()

    def stop_server(self):
        self.exit_trigger.set()

    def read_request(
                self,
                characteristic: BlessGATTCharacteristic,
                **kwargs
            ) -> bytearray:
        self.logger.debug(f"Reading {characteristic.value}")
        return characteristic.value
    def write_request(
                self,
                characteristic: BlessGATTCharacteristic,
                value: Any,
                **kwargs
            ):
        characteristic.value = value
        self.logger.debug(f"Char value set to {characteristic.value}")
