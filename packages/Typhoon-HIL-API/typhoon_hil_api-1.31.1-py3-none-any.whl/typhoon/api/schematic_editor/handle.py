#
# Schematic API handle module.
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


class ItemHandle:
    """
    Represents schematic item in the context of Schematic API.
    """

    def __init__(self, item_type, item_fqid, fqn, **kwargs):
        """
        Initialize schematic item object.

        Args:
            item_type (str): Item type constant.
            item_fqid(str): Core item fully qualified identification.
            fqn(str): Core item fully qualified name.
        """
        super().__init__()

        self.item_type = item_type
        self.item_fqid = item_fqid
        self.fqn = fqn

    def __str__(self):
        """
        String representation for this object.
        """
        return f"{self.item_type}: {self.fqn}"

    def __repr__(self):
        """
        Custom repr.
        """
        return f"ItemHandle('{self.item_type}', '{self.item_fqid}', '{self.fqn}')"

    def __hash__(self):
        return hash((self.item_type, self.item_fqid))

    def __eq__(self, other):
        return (
            self.item_type == other.item_type
            and self.fqn == other.fqn
            and self.item_fqid == other.item_fqid
        )
