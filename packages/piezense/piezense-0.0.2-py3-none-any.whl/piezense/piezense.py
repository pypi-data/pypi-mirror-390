#!/usr/bin/env python3

import asyncio
import bleak
FOLLOWER_COUNT=2
class PieZense:
    def __init__(self, system_name_list_input):
        self.system_name_list = system_name_list_input
        self.system_client_list=[] # list of BleakClient objects
        self.num_systems = len(self.system_name_list)
        for i, _ in enumerate(self.system_name_list):
            self.system_client_list.append(None)

        asyncio.run(self.reconnect_to_systems())

    async def reconnect_to_systems(self):
        while(True):
            for i, system_name in enumerate(self.system_name_list):
                if self.system_client_list[i] is None: # connect
                    print(f"Need device: {system_name}")
                    device = await bleak.BleakScanner.find_device_by_name(system_name)
                    print(f"Scanned for device: {system_name}")
                    if device:
                        print(f"Found device: {device}")
                        self.system_client_list[i] = bleak.BleakClient(device)
                        # self.system_client_list[i].set_disconnected_callback(self.generate_disconnect_callback(i, system_name))
                        await self.system_client_list[i].connect()
                        if self.system_client_list[i].is_connected:
                            print(f"Connected to device: {system_name}")
                            services=await self.system_client_list[i].services
                            print(f"Services: {services}")

                            for service in services:
                                for char in service.characteristics:
                                    if "notify" in char.properties:
                                        print(f"[{system_name}] Subscribing to {char.uuid}")
                                        await self.system_client_list[i].start_notify(
                                            char.uuid,
                                            lambda sender, data, idx=i: self.notification_handler(idx, sender, data)
                                        )
                        else:
                            print(f"Failed to connect to device: {system_name}")
                            self.system_client_list[i] = None

                else:
                    print(f"Device not found, will retry: {system_name}")
                await asyncio.sleep(11)

    def notification_handler(self, device_index, sender, data):
        expected_without_ts = FOLLOWER_COUNT * 2
        pressure_data = data[:expected_without_ts]
        num_followers = len(pressure_data) // 2 # // does integer division
        for follower_id in range(num_followers):
            low_byte = pressure_data[follower_id * 2]
            high_byte = pressure_data[follower_id * 2 + 1]
            pressure_value = (high_byte << 8) | low_byte
            print(f"Device {device_index}, Follower {follower_id}, Pressure: {pressure_value} Pa")