import asyncio
import logging
import struct
import threading
import time
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
            "00001800-0000-1000-8000-00805f9b34fb": { # GenericAccessUUID
                "00002a00-0000-1000-8000-00805f9b34fb": { # DeviceNameUUID
                    "Properties": (
                                    GATTCharacteristicProperties.read
                                ),
                    "Permissions": (GATTAttributePermissions.readable),
                    "Value": b'FFTMSBLEServerKER',
                    "value": b'FFTMSBLEServerKER',
                    "Description": "Device Name"
                },
                "00002a01-0000-1000-8000-00805f9b34fb": { # AppearanceNameUUID
                    "Properties": (
                                    GATTCharacteristicProperties.read
                                ),
                    "Permissions": (GATTAttributePermissions.readable),
                    "Value":        b'\x80\x00',
                    "value":        b'\x80\x00',
                    "Description": "Appearance"
                },
            },
            "0000180d-0000-1000-8000-00805f9b34fb": { # HeartRateUUID
                "00002a37-0000-1000-8000-00805f9b34fb": { # HeartRateMeasurementUUID
                    "Properties": (
                                    GATTCharacteristicProperties.read |
                                    GATTCharacteristicProperties.notify 
                                ),
                    "Permissions": (GATTAttributePermissions.readable),
                    "Value": None,
                    "Description": "Heart Rate Measurement"
                },
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
        await self.server.start(prioritize_local_name = False)
        self.logger.debug("Advertising")
        while not(self.exit_trigger.isSet()):
            await asyncio.sleep(1)
            hrt = int(time.time() % 60) + 100
            flags = 0
            info = struct.pack ('<BB', flags, hrt)
            self.server.get_characteristic("00002a37-0000-1000-8000-00805f9b34fb").value = info
            self.server.update_value("0000180d-0000-1000-8000-00805f9b34fb","00002a37-0000-1000-8000-00805f9b34fb")
        

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
