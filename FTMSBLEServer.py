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
    currentSpeed = 0
    currentCadence = 0
    currentPower = 0

    my_device_name = b"FTMSBLES02"
    my_service_name = "FTMSBLES02 Service"
    fitness_machine_S_UUID = "00001826-0000-1000-8000-00805f9b34fb"
    heart_rate_measurement_C_UUID = "00002a37-0000-1000-8000-00805f9b34fb"
    fitness_machine_control_point_C_UUID = "00002ad9-0000-1000-8000-00805f9b34fb"
    fitness_machine_feature_C_UUID = "00002acc-0000-1000-8000-00805f9b34fb"
    fitness_machine_status_C_UUID = "00002ada-0000-1000-8000-00805f9b34fb"
    indoor_bike_data_C_UUID = "00002ad2-0000-1000-8000-00805f9b34fb"
    cycling_power_measurement_C_UUID = "00002a63-0000-1000-8000-00805f9b34fb"
    supported_power_range_C_UUID = "00002ad8-0000-1000-8000-00805f9b34fb"
    device_name_C_UUID = "00002a00-0000-1000-8000-00805f9b34fb"
    appearance_C_UUID = "00002a01-0000-1000-8000-00805f9b34fb"
    characteristic_names={
        heart_rate_measurement_C_UUID:"Heart Rate Measurement",
        fitness_machine_control_point_C_UUID:"Fitness Machine Control Point",
        fitness_machine_feature_C_UUID:"Fitness Machine Feature",
        fitness_machine_status_C_UUID:"Fitness Machine Status",
        indoor_bike_data_C_UUID:"Indoor Bike Data",
        cycling_power_measurement_C_UUID:"Cycling Power Measurement",
        supported_power_range_C_UUID:"Supported Power Range",
        device_name_C_UUID:"Device Name",
        appearance_C_UUID:"Appearace"
    }
    fmf_CadenceSupported                        = 1 <<  1
    fmf_HeartRateMeasurementSupported           = 0 # 1 << 10
    fmf_PowerMeasurementSupported               = 1 << 14
    fmf_PowerTargetSettingSupported             = 0# 1 <<  3     #TODO: Re-enable!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    fmf_IndoorBikeSimulationParametersSupported = 0 # 1 << 13
    fmf_Info = struct.pack("<LL",   fmf_CadenceSupported                        |
                                    fmf_HeartRateMeasurementSupported           |
                                    fmf_PowerMeasurementSupported,
                                    fmf_PowerTargetSettingSupported             |
                                    fmf_IndoorBikeSimulationParametersSupported )
    ibd_InstantaneousSpeedIsNotPresent  = 0 # 1
    ibd_InstantaneousCadencePresent     = 1 << 2
    ibd_InstantaneousPowerPresent       = 1 << 6
    ibd_HeartRatePresent                = 0 # 1 << 9
    ibd_Flags                           = ibd_InstantaneousSpeedIsNotPresent | ibd_InstantaneousCadencePresent | ibd_InstantaneousPowerPresent | ibd_HeartRatePresent


    gatt: Dict = {
            fitness_machine_S_UUID: { 
                device_name_C_UUID: {
                    "Properties": (
                                    GATTCharacteristicProperties.read
                                ),
                    "Permissions": (GATTAttributePermissions.readable),
                    "Value": (my_device_name),
                    "value": (my_device_name),
                    "Description": "Device Name"
                },
                appearance_C_UUID:{
                    "Properties": (
                                    GATTCharacteristicProperties.read
                                ),
                    "Permissions": (GATTAttributePermissions.readable),
                    "Value":        b'\x80\x00',
                    "value":        b'\x80\x00',
                    "Description": "Appearance"
                },
                # heart_rate_measurement_C_UUID: {
                #     "Properties": (
                #                     GATTCharacteristicProperties.read |
                #                     GATTCharacteristicProperties.notify 
                #                 ),
                #     "Permissions": (GATTAttributePermissions.readable),
                #     "Value": None,
                #     "Description": "Heart Rate Measurement"
                # },
                fitness_machine_control_point_C_UUID: {
                    "Properties": (
                                    GATTCharacteristicProperties.write |
                                    GATTCharacteristicProperties.indicate
                                ),
                    "Permissions": (GATTAttributePermissions.readable | GATTAttributePermissions.writeable),
                    "Value": b"\x00\x00",
                    "value": b"\x00\x00",
                    "Description": "Heart Rate Measurement"
                },
                fitness_machine_feature_C_UUID: {
                    "Properties": (
                                    GATTCharacteristicProperties.read
                                ),
                    "Permissions": (GATTAttributePermissions.readable),
                    "Value": fmf_Info,
                    "Description": "Heart Rate Measurement"
                },
                supported_power_range_C_UUID: {
                    "Properties": (
                                    GATTCharacteristicProperties.read
                                ),
                    "Permissions": (GATTAttributePermissions.readable),
                    "Value": b'\x32\x00\x58\x02\x05\x00', # 50w - 600w, 5w increments
                    "Description": "Heart Rate Measurement"
                },
                # fitness_machine_status_C_UUID: {
                #     "Properties": (
                #                     GATTCharacteristicProperties.read |
                #                     GATTCharacteristicProperties.notify 
                #                 ),
                #     "Permissions": (GATTAttributePermissions.readable),
                #     "Value": None,
                #     "Description": "Heart Rate Measurement"
                # },
                indoor_bike_data_C_UUID: {
                    "Properties": (
                                    GATTCharacteristicProperties.read |
                                    GATTCharacteristicProperties.notify 
                                ),
                    "Permissions": (GATTAttributePermissions.readable),
                    "Value": None,
                    "Description": "Indoor Bike Data"
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
            # self.set_heart_rate(int(time.time() % 60) + 100)
            self.set_bike_data(int(time.time() % 60),int(time.time() % 30) + 65, int(time.time() % 60) + 200)
        
    def set_bike_data(self,currentSpeed,currentCadence,currentPower):
        self.currentSpeed = currentSpeed
        self.currentCadence = currentCadence
        self.currentPower = currentPower

        self.logger.debug(f"Setting Bike Data: s:{currentSpeed}, c:{currentCadence}, p:{currentPower}")

        s     = int(self.currentSpeed * 100) & 0xffff
        c     = int(self.currentCadence * 2) & 0xffff
        p     = int(self.currentPower)       & 0xffff
        info  = struct.pack("<HHHH", self.ibd_Flags, s, c, p)

        self.server.get_characteristic(self.indoor_bike_data_C_UUID).value = info
        self.server.update_value(self.fitness_machine_S_UUID, self.indoor_bike_data_C_UUID)

    def set_heart_rate(self,hrt):
        self.logger.debug(f"Setting Heart Rate: {hrt}")

        flags = 0
        info = struct.pack ('<BB', flags, hrt)
        self.server.get_characteristic(self.heart_rate_measurement_C_UUID).value = info
        self.server.update_value(self.fitness_machine_S_UUID,self.heart_rate_measurement_C_UUID)

    def set_target_watt(self,watt):
        self.logger.debug(f"Setting Target Watt: {watt}")

        flags = 0
        info = struct.pack ('<BB', flags, watt)
        self.server.get_characteristic(self.fitness_machine_control_point_C_UUID).value = info
        self.server.update_value(self.fitness_machine_S_UUID,self.fitness_machine_control_point_C_UUID)

    def stop_server(self):
        self.exit_trigger.set()

    def read_request(
                self,
                characteristic: BlessGATTCharacteristic,
                **kwargs
            ) -> bytearray:
        self.logger.debug(f"Reading {self.characteristic_names[characteristic._uuid]}: {characteristic.value}")
        return characteristic.value
    
    def write_request(
                self,
                characteristic: BlessGATTCharacteristic,
                value: Any,
                **kwargs
            ):
        uuid = str(characteristic._uuid)
        self.logger.debug(f"Setting value for {self.characteristic_names[uuid]} to {characteristic.value}")
        if uuid == self.fitness_machine_control_point_C_UUID:
            self.set_target_watt(value)
            pass

