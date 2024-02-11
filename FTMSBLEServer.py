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
    targetPower = 100
    isUnderControl = False
    isTrainingRunning = False

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
    fms_TargetPowerChanged = 1 << 3
    fmcp_RequestControl = 0x00
    fmcp_Reset = 0x01
    fmcp_SetTargetPower = 0x05
    fmcp_StartOrResume = 0x07
    fmcp_StopOrPause = 0x08
    fmcp_SetIndoorBikeSimulation = 0x11
    fmcp_ResponseCode = 0x80

    fmcp_Success = 0x01
    fmcp_OpCodeNotSupported = 0x02
    fmcp_InvalidParameter = 0x03
    fmcp_OperationFailed = 0x04
    fmcp_ControlNotPermitted = 0x05

    fms_Reset = 0x01
    fms_FitnessMachineStoppedOrPausedByUser = 0x02
    fms_FitnessMachineStartedOrResumedByUser = 0x04
    fms_TargetPowerChanged = 0x08
    fms_IndoorBikeSimulationParametersChanged = 0x12

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
                fitness_machine_status_C_UUID: {
                    "Properties": (
                                    GATTCharacteristicProperties.read |
                                    GATTCharacteristicProperties.notify 
                                ),
                    "Permissions": (GATTAttributePermissions.readable),
                    "Value": None,
                    "Description": "Heart Rate Measurement"
                },
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
        self.isUnderControl = False


    async def run(self,loop):
        self.exit_trigger.clear()
        self.server = BlessServer(name=self.my_service_name, loop=loop)
        self.server.read_request_func = self.read_request
        self.server.write_request_func = self.write_request
        
        
        await self.server.add_gatt(self.gatt)
        await self.server.start(prioritize_local_name = False)
        self.logger.debug("Advertising")
        while not(self.exit_trigger.isSet()):
            await asyncio.sleep(2)
            # self.set_heart_rate(int(time.time() % 60) + 100)
            self.set_bike_data(abs(int(time.time() % 40)-20)+10,abs(int(time.time() % 20)-10) + 65, abs(int(time.time() % 10)-5) + self.targetPower)
        
    def set_bike_data(self,currentSpeed,currentCadence,currentPower):
        self.currentSpeed = currentSpeed
        self.currentCadence = currentCadence
        self.currentPower = currentPower

        self.logger.debug(f"Setting Bike Data: s:{currentSpeed}, c:{currentCadence}, p:{currentPower} --- Status: Under Control:{self.isUnderControl}, In Training:{self.isTrainingRunning}, Target Power:{self.targetPower}")

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

    
    def reset_control(self):
        self.isUnderControl = False
        self.isTrainingRunning = False

    def handle_control_request(self, value):
        opcode = value[0]
        result = self.fmcp_Success
        if opcode == self.fmcp_RequestControl:
            if not self.isUnderControl:
                self.isUnderControl = True
                self.isTrainingRunning = False
                self.logger.debug(f"-->Control Request Accepted")
            else:
                result = self.fmcp_ControlNotPermitted
                self.logger.debug(f"--!Control Request Denied")
        elif not self.isUnderControl:
            result = self.fmcp_ControlNotPermitted
            self.logger.debug(f"--!Action Request Denied because no control")
        else:
            if opcode == self.fmcp_StartOrResume:
                self.fms_action_StartOrResume()
            elif opcode == self.fmcp_StopOrPause:
                self.fms_action_StopOrPause()
            elif opcode == self.fmcp_Reset:
                self.fms_action_Reset()
            elif opcode == self.fmcp_SetTargetPower:
                self.fms_action_SetTargetPower(value)
            else:
                self.logger.debug(f"--!Unknown Opcode: {opcode}")
                result = self.fmcp_ControlNotPermitted
        
        info = struct.pack("<BBB",self.fmcp_ResponseCode,opcode,result)
        self.logger.debug(f'Characteristic {self.characteristic_names[self.fitness_machine_control_point_C_UUID]}: writing {info}')
        self.update_characteristic(self.fitness_machine_control_point_C_UUID,info)
        self.logger.debug(f'Characteristic {self.characteristic_names[self.fitness_machine_control_point_C_UUID]}: writen')

    def fms_action_SetTargetPower(self,value):
        unpacked_value = struct.unpack("<BH",value)
        self.logger.debug(f'unpacked_value = {unpacked_value}')
        self.targetPower = unpacked_value[1]
        self.logger.debug(f"-->Training Target Power set to {self.targetPower}")
        info = struct.pack("<BH",self.fms_TargetPowerChanged,self.targetPower)
        self.logger.debug(f'Setting Fitness Machine Status to {info}')
        self.update_characteristic(self.fitness_machine_status_C_UUID,info)

    def fms_action_StartOrResume(self):
        self.isTrainingRunning = True
        self.logger.debug(f"-->Training Started")
        info = struct.pack("<B",self.fms_FitnessMachineStartedOrResumedByUser)
        self.update_characteristic(self.fitness_machine_status_C_UUID,info)

    def fms_action_StopOrPause(self):
        self.isTrainingRunning = False
        self.logger.debug(f"-->Training Stopped")
        info = struct.pack("<B",self.fms_FitnessMachineStoppedOrPausedByUser)
        self.update_characteristic(self.fitness_machine_status_C_UUID,info)

    def fms_action_Reset(self):
        self.reset_control()
        self.logger.debug(f"-->Training Reset, Control Ended")
        info = struct.pack("<B",self.fms_Reset)
        self.update_characteristic(self.fitness_machine_status_C_UUID,info)

    def update_characteristic(self,characteristic_uuid,info):
        self.logger.debug(f'Writing characteristic {self.characteristic_names[characteristic_uuid]} with value {info}...')
        self.server.get_characteristic(characteristic_uuid).value = info
        self.logger.debug(f'Characteristic {self.characteristic_names[characteristic_uuid]} written. Notifying...')
        self.server.update_value(self.fitness_machine_S_UUID,characteristic_uuid)
        self.logger.debug(f'Characteristic {self.characteristic_names[characteristic_uuid]}: notification sent')

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
        if uuid == self.fitness_machine_control_point_C_UUID:
            self.logger.debug(f"Writing to {self.characteristic_names[uuid]}: {value}")
            self.handle_control_request(value)
        else:
            self.logger.debug(f"NOT SUPPORTED: Setting value for {self.characteristic_names[uuid]} to {characteristic.value}")

