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
"""
Package manager API module.
"""

from typhoon.api.package_manager.base import PackageManagerAPIBase
from typhoon.api.package_manager.stub import clstub

__all__ = ["package_manager"]

from typhoon.api.utils import determine_path


class PackageManagerAPI(PackageManagerAPIBase):
    """
    Class provides methods to manipulate user packages.
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize package manager instance.

        Arguments:
            None
        """
        super().__init__(*args, **kwargs)

        # Indicator if messages are written to standard error
        self.debug = True

    def raise_exceptions(self, value):
        clstub().raise_exceptions = value

    def _reconnect(self):
        """Reconnects client to Typhoon HIL Control Center.

        This is used in cases where Typhoon HIL Control Center needs to be
        restarted, to reestablish the connection between the client and THCC.
        """
        clstub().reconnect()

    def get_modified_packages(self):
        """
        Checks integrity of installed packages. Returns iterable over packages
        that have been modified.

        Returns:
            Iterable over modified packages (Package).

        **Example:**

        .. literalinclude:: package_manager_api_examples/get_modified_packages.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python package_manager_api_examples/get_modified_packages.example
        """
        return clstub().get_modified_packages()

    def get_installed_packages(self):
        """
        Returns iterable over installed packages.

        Returns:
            Iterable over installed packages (Package).

        **Example:**

        .. literalinclude:: package_manager_api_examples/get_installed_packages.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python package_manager_api_examples/get_installed_packages.example
        """
        return clstub().get_installed_packages()

    def get_available_packages(self, latest_version=True):
        """
        Returns iterable over packages available on Package Marketplace.

        Args:
            latest_version (bool): If true, return only latest version of
            the package. Otherwise, return an object for each version
            of the package available.

        Returns:
            Iterable over available packages (Package).

        **Example:**

        .. literalinclude:: package_manager_api_examples/get_available_packages.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python package_manager_api_examples/get_available_packages.example
        """
        return clstub().get_available_packages(latest_version=latest_version)

    def install_package(self, filename):
        """
        Installs a package located at filename, specified by parameter.

        Args:
            filename: filename in which package is located.

        Raises:
            PkmApiException

        **Example:**

        .. literalinclude:: package_manager_api_examples/install_package.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python package_manager_api_examples/install_package.example
        """
        return clstub().install_package(filename=filename)

    def download_package(self, output_path, package_name, version="latest"):
        """
        Returns iterable over packages available on Package Marketplace.

        Args:
            output_path (str): Output directory/file path for downloaded package.
                If file is passed, it must have .tpkg extension. If not, it will
                have "[package_name]-[version].tpkg" format.
            package_name (str): name of the package to be downloaded.
            version (str): Package version. String "latest" can be used for
            latest version of the package.

        Returns:
            String file path of downloaded package

        Raises:
            PkmApiException

        **Example:**

        .. literalinclude:: package_manager_api_examples/download_package.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python package_manager_api_examples/download_package.example
        """
        return clstub().download_package(
            output_path=determine_path(output_path),
            package_name=package_name,
            version=version,
        )

    def uninstall_package(self, package_name):
        """
        Uninstalls a package by name, specified by parameter package_name.

        Args:
            package_name: name of the package to be uninstalled.

        Raises:
            PkmApiException

        **Example:**

        .. literalinclude:: package_manager_api_examples/uninstall_package.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python package_manager_api_examples/uninstall_package.example
        """
        return clstub().uninstall_package(package_name=package_name)

    def reinstall_package(self, package_name):
        """
        Reinstall a package by name, specified by parameter package_name.

        Args:
            package_name: name of the package to be reinstalled.

        Raises:
            PkmApiException

        **Example:**

        .. literalinclude:: package_manager_api_examples/reinstall_package.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python package_manager_api_examples/reinstall_package.example
        """
        return clstub().reinstall_package(package_name=package_name)

    def validate_package(self, filename):
        """
        Validate a package located at filename, specified by parameter.

        Args:
            filename: filename in which package is located.

        Raises:
            PkmApiException

        **Example:**

        .. literalinclude:: package_manager_api_examples/validate_package.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python package_manager_api_examples/validate_package.example
        """
        return clstub().validate_package(filename=filename)

    def create_example(
        self,
        title,
        model_file,
        panel_file,
        output_path,
        tags=None,
        description="",
        image_file="",
        app_note_file="",
        tests=None,
        test_resources=None,
        resources=None,
    ):
        """
        Create an example with given parameters and save it at output_path

        Args:
            title: Example title
            model_file: Path to model file
            panel_file: Path to panel file
            output_path: Path where example will be saved
            tags: List of string tags
            description: Example description
            image_file: Path to image file
            app_note_file: Path to application note document
            tests: List of files representing tests
            test_resources: List of files representing resources used in tests
            resources: List of files representing resources

        Raises:
            PkmApiException

        **Example:**

        .. literalinclude:: package_manager_api_examples/create_example.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python package_manager_api_examples/create_example.example
        """
        return clstub().create_example(
            title=title,
            model_file=model_file,
            panel_file=panel_file,
            output_path=output_path,
            tags=tags,
            description=description,
            image_file=image_file,
            app_note_file=app_note_file,
            tests=tests,
            test_resources=test_resources,
            resources=resources,
        )

    def create_package(
        self,
        package_name,
        version,
        output_path,
        author="",
        website="",
        description="",
        minimal_sw_version="",
        library_paths=None,
        resource_paths=None,
        example_paths=None,
        additional_files_paths=None,
        python_packages_paths=None,
        documentation_paths=None,
        documentation_landing_page="",
        release_notes_path="",
        icon_path="",
    ):
        """
        Create a package with given parameters and save it at output_path

        Args:
            package_name: Package name
            version: Package version
            output_path: Path where package will be saved. If a directory path is passed, the package will be named "package_name - version.tpkg". If a file path is passed, it must have a .tpkg extension.
            author: Package author
            website: Website of package author
            description: Package description
            minimal_sw_version: Minimal version of software in which package is supported
            library_paths: List of paths representing libraries (directories/files)
            resource_paths: List of paths representing library resources (directories/files)
            example_paths: List of paths representing example directories
            additional_files_paths: List of paths representing additional files (directories/files)
            python_packages_paths: List of paths representing python packages (directories/files)
            documentation_paths: List of paths representing package documentation (directories/files)
            documentation_landing_page: Documentation landing page (must be included in documentation_paths)
            release_notes_path: Path to release notes file (html, pdf..)
            icon_path: Path to package icon file (svg, png, jpg, bmp...)

        Raises:
            PkmApiException

        **Example:**

        .. literalinclude:: package_manager_api_examples/create_package.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python package_manager_api_examples/create_package.example
        """
        return clstub().create_package(
            package_name=package_name,
            version=version,
            output_path=output_path,
            author=author,
            website=website,
            description=description,
            minimal_sw_version=minimal_sw_version,
            library_paths=library_paths,
            resource_paths=resource_paths,
            example_paths=example_paths,
            additional_files_paths=additional_files_paths,
            python_packages_paths=python_packages_paths,
            documentation_paths=documentation_paths,
            documentation_landing_page=documentation_landing_page,
            release_notes_path=release_notes_path,
            icon_path=icon_path,
        )


package_manager: PackageManagerAPI = PackageManagerAPI()
