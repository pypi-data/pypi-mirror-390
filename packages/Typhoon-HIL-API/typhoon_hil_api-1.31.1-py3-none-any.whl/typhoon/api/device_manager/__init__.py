#
# This file is a part of Typhoon HIL API library.
#
# Typhoon HIL API is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
import sys

from typhoon.api.device_manager.exceptions import DeviceManagerException
from typhoon.api.device_manager.stub import clstub


class DeviceManagerAPI:
    def __init__(self):
        super().__init__()

    def __getattr__(self, name):
        try:
            attr = clstub().__getattribute__(name)
            return attr
        except Exception:

            def wrapper(*args, **kwargs):
                msg = clstub().build_req_msg(name, **kwargs)

                clstub().log(f"{name} message: {msg}")

                clstub()._req_socket.send_json(msg)

                response = clstub()._req_socket.recv_json()

                result = response.get("result")
                error = response.get("error")

                clstub().log(f"{name} status: {result}")

                if error:
                    err_msg = error["message"]
                    err_msg = (
                        err_msg.encode("utf-8") if sys.version_info[0] < 3 else err_msg
                    )

                    raise DeviceManagerException(err_msg)

                return result

            return wrapper

    def load_setup(self, file=""):
        """
        Loads HIL setup from file to Control Center.

        Args:
            file (str): Setup description.

        Returns:
            status (bool): ``True`` if everything ok, otherwise returns ``False``.
        """
        return clstub().load_setup(file=file)

    def get_setup_devices(self):
        """
        Get all devices from current HIL setup.

        Returns:
             devices (list): dicts with information for each devices
              {"serial_number": "some_serial", "device_name": "some_device_name",
               "status": "device_stauts"}.

        """
        return clstub().get_setup_devices()

    def get_setup_devices_serials(self):
        """
        Get all devices from current HIL setup.

        Returns:
             devices (list): serial number of each device from setup.

        """
        return clstub().get_setup_devices_serials()

    def get_available_devices(self):
        """
        Get all discovered available devices.

        Returns:
            devices (list): available devices in JSON representation.

        """
        return clstub().get_available_devices()

    def get_detected_devices(self):
        """
        Get all discovered devices.

        Returns:
            devices (list): discovered devices in JSON representation.

        """
        return clstub().get_detected_devices()

    def add_devices_to_setup(self, devices=None):
        """
        Add devices to active setup.

        Args:
            devices (list): devices to add.

        Returns:
            status (bool): ``True`` if device is successfully added to setup, otherwise returns ``False``.
        """
        devices = devices if devices is not None else []
        return clstub().add_devices_to_setup(devices=devices)

    def remove_devices_from_setup(self, devices=None):
        """
        Remove devices from active setup.

        Args:
            devices (list): devices to remove.

        Returns:
            status (bool): ``True`` if device is successfully removed from setup, otherwise returns ``False``.
        """
        devices = devices if devices is not None else []
        return clstub().remove_devices_from_setup(devices=devices)

    def connect_setup(self):
        """
        Connect currently selected HIL setup.
        Make all devices in the selected setup inaccessible to others.

        Returns:
            status (bool): ``True`` if all the devices from the setup are available, otherwise returns ``False``.

        .. note::
             If any of the devices from the setup has a status (busy/not online), the execution of this function will return False
        """
        return clstub().connect_setup()

    def disconnect_setup(self):
        """
        Disconnect currently selected HIL setup.
        Make all devices in the selected setup accessible to others.

        Returns:
            status (bool): ``True`` if the disconnection is performed successfully from all devices in the setup, otherwise returns ``False``.
        """
        return clstub().disconnect_setup()

    def is_setup_connected(self):
        """
        Returns current status of active HIL setup.

        Returns:
            status (bool): ``True`` if setup is currently connected, otherwise returns ``False``.

        """
        return clstub().is_setup_connected()

    def add_discovery_ip_addresses(self, addresses=None):
        """
        Specify addresses where HIL devices are located if auto discovery
        fails for some reason.

        Args:
            addresses (list): IP addresses where HIL devices are located.

        Returns:
            status (bool): ``True`` if device IP is successfully added to the THCC address store, otherwise returns ``False``.

        """
        addresses = addresses if addresses is not None else []
        return clstub().add_discovery_ip_addresses(addresses=addresses)

    def remove_discovery_ip_addresses(self, addresses=None):
        """
        Remove previously added addresses where HIL devices are located
        if auto discovery fails for some reason.

        Args:
            addresses (list): IP addresses which you want to remove.

        Returns:
            status (bool): ``True`` if device IP is successfully removed from the THCC address store, otherwise returns ``False``.

        """
        addresses = addresses if addresses is not None else []
        return clstub().remove_discovery_ip_addresses(addresses=addresses)

    def update_firmware(self, device_to_update, configuration_id=None, force=False):
        """
        Updates the firmware of the selected device.

        Args:
            device_to_update (str): Serial number of the selected device.
            configuration_id (int): sequence number of the configuration.
            force (boolean): Force upload even if desired firmware is the same as
                the one already in HIL device

        """
        return clstub().update_firmware(
            device_to_update=device_to_update,
            configuration_id=configuration_id,
            force=force,
        )

    def sync_firmware(self, device_to_update, configuration_id=None, force=False):
        """
        Updates or rollback the firmware of the selected device.

        Args:
            device_to_update (str): Serial number of the selected device.
            configuration_id (int): sequence number of the configuration.
            force (boolean): Force upload even if desired firmware is the same as
                the one already in HIL device

        """
        return clstub().update_firmware(
            device_to_update=device_to_update,
            configuration_id=configuration_id,
            force=force,
        )

    def get_device_settings(self, device_serial):
        """
        Gets all settings from desired device.
        Args:
            device_serial (str): device serial number.

        Returns:
             settings (dict): {'device_name': 'hil_name',
              'ip_address_eth_port_1': '', 'netmask_eth_port_1': '',
                'gateway_eth_port_1': '', 'static_ip_address': '',
                 'netmask': '', 'gateway': '',
                  'heartbeat_timeout': '', 'usb_init_timeout': '',
                   'force_usb': 'False', 'ssh_enable': 'True'}


        .. list-table::  Format of one dictionary that holds HIL configurations.
           :widths: auto
           :header-rows: 1
           :align: left

           * - Dictionary key
             - Meaning
             - Value Type

           * - "device_name"
             - HIL Device name (device_name1, device_name2)
             - int value

           * - "ip_address_eth_port_1"
             - HIL static IP (192.168.0.1, 192.168.0.2...)
             - str value

           * - "netmask_eth_port_1"
             - HIL static IP (192.168.0.1, 192.168.0.2...)
             - str value

           * - "gateway_eth_port_1"
             - HIL gateway
             - str value

           * - "force_usb"
             - (True, False)
             - bool value

           * - "heartbeat_timeout"
             - Define time for heartbeat timeout (in secounds)
             - int value

           * - "usb_init_timeout"
             - Define time for usb init timeout (in secounds)
             - int value

        .. note::
             When an empty string is returned as the value of a setting, it means that the setting has a default value.

        .. note::
            Parameters static_ip_address, netmask and gateway will be replaced with ip_address_eth_port_1,
            netmask_eth_port_1, gateway_eth_port_1 and become deprecated

        """
        return clstub().get_device_settings(device_serial=device_serial)

    def set_device_settings(self, device_serial, settings=None):
        """
        Allows to change all device settings.
        Args:
            device_serial (str): serial number of the desired device.
            settings (dict): device settings by system key (setting name)
            and value (desired values for the previously specified key)
            settings (dict): {'device_name': 'hil_name',
            'ip_address_eth_port_1': '', 'netmask_eth_port_1': '',
            'gateway_eth_port_1': '', 'static_ip_address': '',
            'netmask': '', 'gateway': '','force_usb': 'False',
            'heartbeat_timeout': '', 'usb_init_timeout': '',
            'ssh_enable': 'True'}

        Returns:
            status (bool): ``True`` if the passed settings have been successfully written to the device, otherwise returns ``False``.

        .. note::
             When an empty string is passed as a setting value, that setting will be set to the default value.
        .. note::
            Depending on the HIL you can modify network settings on other ports
        .. note::
            Parameters static_ip_address, netmask and gateway will be replaced with ip_address_eth_port_1,
            gateway_eth_port_1 and netmask_eth_port_1 in future versions.

        """
        settings = settings if settings is not None else {}
        return clstub().set_device_settings(
            device_serial=device_serial, settings=settings
        )

    def get_hil_info(self):
        """
        Returns information about all connected HIL devices.

        Returns:
            list: list that contains dictionaries where each dictionary holds
            information about one connected HIL device.

            In case there is no connected HIL devices ``None`` will be returned.

        .. list-table::  Format of one dictionary that holds HIL information.
           :widths: auto
           :header-rows: 1
           :align: left

           * - Dictionary key
             - Meaning
             - Value Type

           * - "device_id"
             - HIL Device ID (0, 1, 2...)
             - int value

           * - "serial_number"
             - HIL Serial number (00404-00-0001, 00402-00-0001...)
             - string value

           * - "configuration_id"
             - HIL Configuration ID (1, 2, 3...)
             - int value

           * - "product_name"
             - HIL Product Name (HIL402, HIL602...)
             - string value

           * - "firmware_release_date"
             - HIL Firmware Release date (in format Y-M-D)
             - string value

           * - "calibration_date"
             - HIL Calibration date (in format Y-M-D). ``None`` will be
               returned if HIL is not calibrated, calibration data is
               wrong or calibration is not supported on connected HIL)
             - string value
        """

        return clstub().get_hil_info()


device_manager: DeviceManagerAPI = DeviceManagerAPI()
