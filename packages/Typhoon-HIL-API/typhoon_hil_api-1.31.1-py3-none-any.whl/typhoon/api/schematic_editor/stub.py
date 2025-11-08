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
import threading
from functools import lru_cache  # Reverted because of Python 3.8
from warnings import warn

from typhoon.api.common import (
    ClientStubMixin,
    ConnectionMixin,
    LoggingMixin,
    thread_safe,
)
from typhoon.api.constants import SCHEMATIC_API_NAME
from typhoon.api.schematic_editor.const import DATA_FRAME, ITEM_HANDLE
from typhoon.api.schematic_editor.exception import SchApiException
from typhoon.api.schematic_editor.handle import ItemHandle
from typhoon.api.utils import check_environ_vars, init_stub

lock = threading.RLock()

# Functions that existed before the API update (these functions return True if
# everything went OK, and False in case of an error)
old_functions = {
    "load",
    "save",
    "save_as",
    "compile",
    "set_hw_settings",
    "detect_hw_settings",
    "get_hw_settings",
    "set_simulation_method",
    "set_simulation_time_step",
    "set_component_property",
    "set_property_attribute",  # deprecated, but still added
    # just in case
    "disable_items",
    "enable_items",
    "is_enabled",
    "export_library",
}


class ClientAPIStub(LoggingMixin, ClientStubMixin, ConnectionMixin):
    def __init__(self, server_params, log_file="client.log"):
        super().__init__(log_file)
        self.server_ip, self.server_port = server_params

        # Switch for raising exceptions and warnings instead of just printing
        self.raise_exceptions = False

    @property
    def server_addr(self):
        return f"tcp://{self.server_ip}:{self.server_port}"

    def _ping_resp_handler(self, response):
        if self.server_port is None:
            # If server_port is None, it means following:
            #   1. server_port is not defined in settings.conf
            #   2. server_port is not provided as env variable
            #
            # In that case, we use port number provided by server through
            # announcement.
            port_data = response.get("result")[2]
            self.server_port = port_data[SCHEMATIC_API_NAME]["server_rep_port"]

    def connect(self):
        self._ping()

    def __getattr__(self, name):
        try:
            attr = self.__getattribute__(name)
            return attr
        except Exception:

            @thread_safe(lock)
            def wrapper(*args, **kwargs):
                from typhoon.api.common.data_frame_serialization import deserialize_data_frame
                msg = self.build_req_msg(name, **kwargs)

                self.log(f"{name} message: {msg}")

                self._req_socket.send_json(msg)

                response = self._req_socket.recv_json()

                result = response.get("result")
                error = response.get("error")
                warnings = response.get("warnings", [])

                self.log(f"{name} status: {result}")

                for warning in warnings:
                    f_warning = warn if self.raise_exceptions else print

                    f_warning(warning)

                if error:
                    err_msg = error["message"]
                    err_msg = (
                        err_msg.encode("utf-8") if sys.version_info[0] < 3 else err_msg
                    )

                    if name in old_functions and self.raise_exceptions is False:
                        print(err_msg)
                        # Set result to False to ensure backward compatibility
                        result = False
                    else:
                        data = error.get("data", {})
                        internal_code = data.get("internal_error_code", None)
                        raise SchApiException(err_msg, internal_code=internal_code)

                # If result is None, and no errors occurred, it means that the
                # method is successfully called, but we need to switch result
                # to True to ensure backward compatibility.
                if name in old_functions and result is None and error is None:
                    result = True
                elif isinstance(result, dict) and ITEM_HANDLE in result:
                    result = ItemHandle(**result)
                elif isinstance(result, dict) and DATA_FRAME in result:
                    result = deserialize_data_frame(result["data"])
                elif isinstance(result, list):
                    res = []
                    for item in result:
                        if isinstance(item, dict) and ITEM_HANDLE in item:
                            res.append(ItemHandle(**item))
                        elif isinstance(item, dict) and DATA_FRAME in item:
                            res.append(deserialize_data_frame(item["data"]))
                        else:
                            res.append(item)
                    result = res

                return result

            return wrapper


@lru_cache  # Reverted because of Python 3.8
@check_environ_vars(server_type=SCHEMATIC_API_NAME)
def clstub(server_params):
    return init_stub(ClientAPIStub, server_params)
