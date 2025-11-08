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
import json
import os
import pickle
import threading
from functools import lru_cache  # Reverted because of Python 3.8
from warnings import warn

import numpy as np
from typhoon.api.common import DEBUG, ClientStubMixin, LoggingMixin, thread_safe
from typhoon.api.constants import HIL_API_NAME
from typhoon.api.hil.exception import HILAPIException
from typhoon.api.utils import check_environ_vars, init_stub

ask_for_input = input

lock = threading.RLock()


def recv_array(socket, flags=0, copy=False, track=True):
    """recv a numpy array"""
    md = socket.recv_json(flags=flags)
    msg = socket.recv(flags=flags, copy=copy, track=track)

    # ZMQ sends read-only copy of the numpy array, so we need to create copy
    a = np.frombuffer(msg, dtype=md["dtype"])
    b = a.copy()
    # Copy is set to be writeable, so it can be changed in scripts.
    b.flags["WRITEABLE"] = True
    return b.reshape(md["shape"])


def recv_time_data(socket, flags=0, copy=False, track=True):
    """recv a numpy array or a dict with a numpy array and scalars"""

    # first receive a metadata as json
    md = socket.recv_json(flags=flags)

    # time data are sent as dictionary
    if md["time_data_type"] == "dict":
        # dictionary are serialized and sent as json
        msg = socket.recv_json(flags=flags)

        # deserialize a data from json
        data = json.loads(msg)

        # convert x_data (python list) to numpy array with correct type and shape
        a = np.fromiter(data["x_data"], dtype=md["dtype"])
        data["x_data"] = a.reshape(md["shape"])
        return data

    # time data are sent as numpy array as a bytearray
    else:
        msg = socket.recv(flags=flags, copy=copy, track=track)

        # ZMQ sends read-only copy of the numpy array, so we need to create copy
        a = np.frombuffer(msg, dtype=md["dtype"])
        b = a.copy()
        # Copy is set to be writeable, so it can be changed in scripts.
        b.flags["WRITEABLE"] = True
        return b.reshape(md["shape"])


def recv_dict(socket, flags=0, copy=False, track=True):
    """recv a numpy array"""
    md = socket.recv_json(flags=flags)
    msg = socket.recv(flags=flags, copy=copy, track=track)
    for signal_name, values in msg["signals"].items():
        a = np.frombuffer(values, dtype=md["dtype"])
        b = a.copy()
        # Copy is set to be writeable, so it can be changed in scripts.
        b.flags["WRITEABLE"] = True
        b.reshape(md["shape"])
        msg["signals"][signal_name] = b

    # ZMQ sends read-only copy of the numpy array, so we need to create copy
    return b.reshape(md["shape"])


class ClientAPIStub(LoggingMixin, ClientStubMixin):
    def __init__(self, server_params, log_file="client.log"):
        super().__init__(log_file=log_file)

        self.server_ip, self.server_port = server_params

        self._queue = None
        self._waiting_for_data = False
        self._cpt_req_sent = False

        self._dataBuffer = []

        # Switch for raising exceptions and warnings instead of just printing
        self.raise_exceptions = False

    def connect(self):
        self._ping()

    def _ping_resp_handler(self, response):
        if self.server_port is None:
            # If server_port is None, it means following:
            #   1. server_port is not defined in settings.conf
            #   2. server_port is not provided as env variable
            #
            # In that case, we use port number provided by server through
            # announcement.
            port_data = response.get("result")[2]
            ports = port_data[HIL_API_NAME]
            self.server_port = ports["server_rep_port"]

    @property
    def server_addr(self):
        return f"tcp://{self.server_ip}:{self.server_port}"

    def __getattr__(self, name):
        # This method will return the method with a given name if it exists.
        # If the method with a given name doesn't exist, a "wrapper" method
        # will be returned. The main job if the "wrapper" function is to make
        # a remote call to the server, and to return the response.
        try:
            attr = self.__getattribute__(name)
            return attr
        except Exception:
            # Dynamically create a function, and make a remote call.
            @thread_safe(lock)
            def wrapper(*args, **kwargs):
                msg = self.build_req_msg(name, **kwargs)

                self.log(f"{name} message: {msg}")

                # Send request to the server
                self._req_socket.send_json(msg)

                # Wait and process the response
                response = self._req_socket.recv_json()

                result = response.get("result", None)
                warnings = response.get("warnings", [])
                error = response.get("error", None)

                self.log(f"{name} result: {result}")

                for warning in warnings:
                    if self.raise_exceptions:
                        if result is False:
                            raise Exception(warning)
                        else:
                            warn(warning, stacklevel=2)
                    else:
                        print(warning)

                if error:
                    # Exception switch used by Typhoon Test.
                    # In case of any type of error (function raises exception
                    # or return some value in case of error) generic exception
                    # will be raised
                    if self.raise_exceptions:
                        raise Exception(error["message"])
                    else:
                        # Custom error that is created when server side
                        # functions raised exception
                        data = error.get("data", None)
                        if data is not None:
                            internal_code = data.get("internal_error_code")
                            raise HILAPIException(
                                error["message"], internal_code=internal_code
                            )

                        # Server side functions doesn't raise exception
                        # in case of error but return some value (mostly False)
                        else:
                            print(error["message"])
                            # Change result to False, since most methods
                            # in HIL API return False if they fail.
                            result = False

                return result

            return wrapper

    @thread_safe(lock)
    def _get_capture_data(self):
        """Returns the captured data."""

        # This method sends three requests to the server in total.
        # It is necessary to send a new request every time you expect that the
        # server will return numpy array.

        # Optimization? This part can be removed, since we already have list
        # of signal names?
        self.log("Get signal names")

        self._req_socket.send_json(self.build_req_msg("_get_signal_names"))
        response = self._req_socket.recv_json()

        signal_names = response["result"]

        self.log("Get captured data...")
        self._req_socket.send_json(self.build_req_msg("_get_captured_data"))
        captured_data = recv_array(self._req_socket)

        self.log("Get timed data...")
        self._req_socket.send_json(self.build_req_msg("_get_timed_data"))
        timed_data = recv_time_data(self._req_socket)

        buff = []
        if signal_names:
            buff.append(signal_names)

        if captured_data.size != 0:
            buff.append(captured_data)

        if len(timed_data) != 0:
            buff.append(timed_data)

        self.log(f"Captured: {buff}", DEBUG)
        if buff:
            self._dataBuffer.append(tuple(buff))

    @thread_safe(lock)
    def start_capture(
        self,
        cpSettings,
        trSettings,
        chSettings,
        dataBuffer=None,
        fileName="",
        executeAt=None,
        timeout=None,
        timeFormat="relative",
    ):
        """Calls the 'start_capture' function on the server."""
        # NOTE: parameters should NOT be removed/renamed to ensure backward
        # compatibility!

        # Save a reference to a dataBuffer, so a client code couldn't tell that
        # this function call uses network to get data from the capture.
        # NOTE: This ensures backward compatibility with old tests scripts
        dataBuffer = dataBuffer if dataBuffer is not None else []
        self._dataBuffer = dataBuffer

        # If file name is given, than the .mat file is generated on the server
        # side.
        # Since fileName path can be relative to the client script, we need to
        # convert it into abspath, but only if it's not empty.
        file_name = os.path.abspath(fileName) if fileName else ""

        message = self.build_req_msg(
            "start_capture",
            cpSettings=cpSettings,
            trSettings=trSettings,
            chSettings=chSettings,
            dataBuffer=[],
            fileName=file_name,
            executeAt=executeAt,
            timeout=timeout,
            timeFormat=timeFormat,
        )

        self.log(message, DEBUG)
        # Send a request to the server
        self._req_socket.send_json(message)

        # Wait for the response, and receive it
        response = self._req_socket.recv_json()

        result = response.get("result")
        error = response.get("error")
        warnings = response.get("warnings", [])

        if error:
            if self.raise_exceptions:
                raise Exception(error["message"])
            else:
                # Set result to False, since start_capture returns False in case of
                # an error
                result = False
                # Print error to the console.
                print(error["message"])

        # Print warnings into the console.
        for warning in warnings:
            if self.raise_exceptions:
                if result is False:
                    raise Exception(warning)
                else:
                    warn(warning, stacklevel=2)
            else:
                print(warning)

        return result

    @thread_safe(lock)
    def capture_in_progress(self):
        """Calls the 'capture_in_progress' function on the server."""

        self._req_socket.send_json(self.build_req_msg("capture_in_progress"))

        response = self._req_socket.recv_json()
        in_progress = response.get("result")
        warnings = response.get("warnings", [])
        error = response.get("error")

        if error:
            print(error["message"])  # print to console
            return False

        # Print warnings into the console.
        for warning in warnings:
            if self.raise_exceptions:
                print(warning)
            else:
                warn(warning, stacklevel=2)

        if not in_progress:
            self._get_capture_data()

        return in_progress

    @thread_safe(lock)
    def read_streaming_signals(self, signals, from_last_index):
        self._req_socket.send_json(
            self.build_req_msg(
                "read_streaming_signals",
                signals=signals,
                from_last_index=from_last_index,
            )
        )

        response = self._req_socket.recv_pyobj()
        if isinstance(response, dict):
            msg = response["message"]
            if self.raise_exceptions:
                raise Exception(msg)
            else:
                print(msg)
                return None, None

        data = pickle.loads(response)
        return data["data"], data["last_index"]

    @thread_safe(lock)
    def stop_capture(self):
        """Calls the 'stop_capture' function on the server."""
        message = self.build_req_msg("stop_capture")

        self.log("{} called".format("stop_capture"), DEBUG)
        self.log("{} message: {}".format("stop_capture", message), DEBUG)

        self._req_socket.send_json(message)

        response = self._req_socket.recv_json()
        result = response.get("result")
        warnings = response.get("warnings", [])
        error = response.get("error")

        if error:
            print(error["message"])  # print to console
            return False

        for warning in warnings:
            if self.raise_exceptions:
                if result is False:
                    raise Exception(warning)
                else:
                    warn(warning, stacklevel=2)
            else:
                print(warning)

        self.log("{} result: {}".format("stop_capture", result), DEBUG)
        if result:
            self._get_capture_data()

    @thread_safe(lock)
    def wait_on_user(self):
        """Waits on the user input."""
        print("PRESS 'ENTER' TO CONTINUE!")
        ask_for_input()

    @thread_safe(lock)
    def server_running(self):
        """Returns False if server is not running."""
        return self._ping(start=False, request_retries=1)


@lru_cache  # Reverted because of Python 3.8
@check_environ_vars(server_type=HIL_API_NAME)
def clstub(server_params):
    return init_stub(ClientAPIStub, server_params)
