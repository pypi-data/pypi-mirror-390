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
import atexit
import sys
import uuid
from collections import defaultdict
from functools import cache
from threading import RLock, Thread
from warnings import warn

import zmq

from typhoon.api.common import (
    ClientStubMixin,
    ConnectionMixin,
    LoggingMixin,
    thread_safe,
)
from typhoon.api.configuration.exception import ConfigurationAPIException
from typhoon.api.constants import CONFIGURATION_API_NAME
from typhoon.api.utils import check_environ_vars, init_stub

lock = RLock()


class ClientAPIStub(LoggingMixin, ClientStubMixin, ConnectionMixin):
    def __init__(self, server_params, log_file="client.log"):
        super().__init__(log_file)

        self._sub_socket = self._context.socket(zmq.SUB)

        self.server_ip, self.server_port = server_params
        self.server_pub_port = None

        self.subscriber_thread: Thread | None = None
        self.subscriptions: dict[str, set[callable]] = defaultdict(set)

        # Switch for raising exceptions and warnings instead of just printing
        self.raise_exceptions = False

        self.id = uuid.uuid4().hex

    @property
    def server_addr(self):
        return f"tcp://{self.server_ip}:{self.server_port}"

    @property
    def server_pub_addr(self):
        return f"tcp://{self.server_ip}:{self.server_pub_port}"

    def _ping_resp_handler(self, response):
        if self.server_port is None or self.server_pub_port is None:
            # If server_port is None, it means following:
            #   1. server_port is not defined in settings.conf
            #   2. server_port is not provided as env variable
            #
            # In that case, we use port number provided by server through
            # announcement.
            port_data = response.get("result")[2][CONFIGURATION_API_NAME]
            self.server_port = port_data["server_rep_port"]
            self.server_pub_port = port_data["server_pub_port"]

    def connect(self):
        self._ping()

    def connect_to_api_server(self):
        # call the connect method of the parent
        super().connect_to_api_server()
        self._sub_socket.connect(self.server_pub_addr)
        # socket.subscribe doesn't work, only setsockopt does
        self._sub_socket.setsockopt(zmq.SUBSCRIBE, b"")

        if not self.subscriber_thread:
            self.subscriber_thread = Thread(target=self._run_subscriber, daemon=True)
            self.subscriber_thread.start()

    def _subscribe(self, key: str, handler: callable):
        already_subscribed = handler in self.subscriptions[key]
        self.subscriptions[key].add(handler)
        return already_subscribed

    def _unsubscribe(self, key: str, handler: callable):
        self.subscriptions[key].remove(handler)

    def _on_configuration_changed(self, message):
        for key, handlers in self.subscriptions.items():
            if key in message:
                for handler in handlers:
                    handler(message)
                continue

            filtered_message = {k: message[k] for k in message if k.startswith(key)}
            if not filtered_message:
                continue

            for handler in handlers:
                handler(filtered_message)

    def _run_subscriber(self):
        atexit.register(self.cleanup)
        while True:
            message = self._sub_socket.recv_json()
            client_id = message["client_id"]
            if client_id != self.id:
                continue
            del message["client_id"]
            self._on_configuration_changed(message)

    def cleanup(self):
        keys_and_handlers = [(key, handler) for key, handlers in self.subscriptions.items() for handler in handlers]
        for key, handler in keys_and_handlers:
            self.unsubscribe(key=key, handler=handler)

    def __getattr__(self, name):
        try:
            attr = self.__getattribute__(name)
            return attr
        except Exception:

            @thread_safe(lock)
            def wrapper(*args, **kwargs):
                # Update local client state on sub/unsub
                if name == "subscribe":
                    # We don't need to call the server if we are already subscribed to the key with the same handler
                    already_subscribed = self._subscribe(
                        kwargs.get("key"), kwargs.get("handler")
                    )
                    if already_subscribed:
                        return

                    # Remove params that don't match the server stub signature (handler)
                    kwargs.pop("handler", None)
                    # Pass the client id to the server
                    kwargs.setdefault("client_id", self.id)

                elif name == "unsubscribe":
                    handler = kwargs.pop("handler", None)
                    handler and self._unsubscribe(kwargs.get("key"), handler)
                    # Pass the client id to the server
                    kwargs.setdefault("client_id", self.id)

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

                    data = error.get("data", {})
                    internal_code = data.get("internal_error_code", None)
                    raise ConfigurationAPIException(
                        err_msg, internal_code=internal_code
                    )

                return result

            return wrapper


@cache
@check_environ_vars(server_type=CONFIGURATION_API_NAME)
def clstub(server_params):
    return init_stub(ClientAPIStub, server_params)
