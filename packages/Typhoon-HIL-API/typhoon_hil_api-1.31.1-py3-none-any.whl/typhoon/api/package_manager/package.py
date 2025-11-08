#
# Package manager API package module.
#
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
class Package:
    """
    Represents package in the context of Package Manager API.
    """

    def __init__(self, package_name, version, **kwargs):
        """
        Initialize Package object.

        Args:
            package_name (str): Package name
            version(str): Package version
        """
        super().__init__()

        self.package_name = package_name
        self.version = version

    def __str__(self):
        """
        String representation for this object.
        """
        return f"{self.package_name}-{self.version}"

    def __repr__(self):
        """
        Custom repr.
        """
        return f"Package('{self.package_name}', '{self.version}')"

    def __hash__(self):
        return hash((self.package_name, self.version))

    def __eq__(self, other):
        return self.package_name == other.package_name and self.version == other.version
