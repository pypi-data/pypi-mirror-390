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


from collections.abc import Callable

from typhoon.api.configuration.schema import JSONSchema, JSONSchemaValue
from typhoon.api.configuration.stub import clstub

Handler = Callable[[dict[str, JSONSchemaValue]], None]


class ConfigurationAPI:
    def __init__(self, *args, **kwargs):
        """
        Initialize Configuration API instance.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        super().__init__(*args, **kwargs)

        # Indicator if messages are written to standard error
        self.debug = True

        # Flag used to tell if compiling should be aborted
        self.abort_compiling = False

    def raise_exceptions(self, value):
        clstub().raise_exceptions = value

    def _reconnect(self):
        """
        Reconnects client to Typhoon HIL Control Center.

        This method is used to reestablish the connection between the client and THCC
        in case the Typhoon HIL Control Center has been restarted.
        """
        clstub().reconnect()

    def subscribe(
        self,
        key: str,
        handler: Handler,
        immediate: bool = False,
    ):
        """
        Subscribe to configuration changes for a specific key.

        Args:
            key (str): The identifier for the configuration item to subscribe to.
                It can also be partial (e.g., "general" or "general.autosave").
            handler (Handler): Function to be called when the configuration item changes.
                The function accepts a single argument - a dictionary containing configuration keys and the updated values.
                If the key is partial (e.g., "general"), the dictionary will contain all the keys that start with "general".
            immediate (bool, optional): If True, the handler will be called immediately with the current value
                of the configuration item, synchronously blocking only on the first call.
                If False, the handler will be called on the next configuration change.

        Raises:
            KeyError: If the key is not part of the configuration schema.

        **Example:**

        .. literalinclude:: configuration_api_examples/subscribe.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python configuration_api_examples/subscribe.example
        """
        clstub().subscribe(key=key, handler=handler, immediate=immediate)

    def unsubscribe(self, key: str, handler: Handler):
        """
        Unsubscribe from configuration changes for a specific key.

        Note:
            The same key and handler that were passed into the subscribe method must be used in order to unsubscribe.

        Args:
            key (str): The identifier for the configuration item to unsubscribe from.
            handler (Handler): The function that was previously subscribed to the configuration item.
        """
        clstub().unsubscribe(key=key, handler=handler)

    def get(self, key: str = "") -> JSONSchemaValue:
        """
        Gets the current value of a configuration item specified by key.

        Args:
            key (str): The identifier for the configuration item to retrieve.
                It can also be partial (e.g., "general" or "general.autosave") to get a part of the configuration,
                or empty to get the whole configuration.

        Returns:
            JSONSchemaValue: The current value of the configuration item. The type can be str, float, int, bool, dict, list or None.

        Raises:
            KeyError: If the key is not part of the configuration schema.

        Note:
            Only predefined keys are available for use.
            For a complete list of configuration keys and their descriptions check out the "get_schema" method example below.

        **Example:**

        .. literalinclude:: configuration_api_examples/get.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python configuration_api_examples/get.example
        """
        return clstub().get(key=key)

    def set(self, key: str, value: JSONSchemaValue):
        """
        Sets the value of a configuration item identified by key.

        Args:
            key (str): The identifier for the configuration item to be updated.
            value (JSONSchemaType): The new value to set for the configuration item. Must match the schema for the item.

        Raises:
            KeyError: If the key is not part of the configuration schema.
            jsonschema.exceptions.ValidationError: if the value does not conform to the schema.
            json.JSONDecodeError: if the configuration file is malformed and needs to be fixed manually.
        """
        clstub().set(key=key, value=value)

    def reset(self, key: str):
        """
        Resets the configuration value for the specified key to its default or initial value.

        Args:
            key (str): The identifier for the configuration item to be reset.

        Raises:
            KeyError: If the key is not part of the configuration schema.
            json.JSONDecodeError: if the configuration file is malformed and needs to be fixed manually.

        **Example:**

        .. literalinclude:: configuration_api_examples/reset.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python configuration_api_examples/reset.example
        """
        clstub().reset(key=key)

    def get_schema(self, key: str = "") -> JSONSchema:
        """
        Retrieves the schema for a configuration item identified by the key.

        Args:
            key (str, optional): The identifier for the configuration item to retrieve.
                It can also be partial (e.g., "general" or "general.autosave") to get a part of the schema, or empty to get the whole schema.

        Returns:
            JSONSchema: The schema for the configuration item in JSONSchema format.

        Raises:
            KeyError: If the key is not part of the configuration schema.

        Note:
            Schema keys marked with "internal" are not visible in the settings UI located
            in the Typhoon HIL Control Center, but are still available for use in the API.

        **Example:**

        .. literalinclude:: configuration_api_examples/schema.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python configuration_api_examples/schema.example
        """
        return clstub().get_schema(key=key)

    @property
    def subscriber_thread(self):
        """
        Get the subscriber thread which listens for configuration changes.

        The thread is started as a daemon when the configuration API is first imported.
        It can be joined using the "join()" method to wait for it to finish.

        Returns:
            threading.Thread: The subscriber thread.
        """
        return clstub().subscriber_thread


configuration: ConfigurationAPI = ConfigurationAPI()
